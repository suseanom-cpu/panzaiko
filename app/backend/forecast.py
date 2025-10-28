import pandas as pd
import numpy as np
import math
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from db import get_db
from datetime import date, timedelta, datetime
import weather_holiday

BREADS = ["細パン", "太パン", "サンドパン", "バゲット"]
SHELF_DAYS = 3
HISTORY_DAYS = 30
SERVICE_LEVEL = 0.9

# 曜日の重み付け（月曜日=0, 日曜日=6）
WEEKDAY_WEIGHTS = {
    0: 0.9,   # 月曜日
    1: 0.95,  # 火曜日
    2: 1.0,   # 水曜日
    3: 1.0,   # 木曜日
    4: 1.1,   # 金曜日
    5: 1.2,   # 土曜日
    6: 1.15   # 日曜日
}

def compute_z(sl):
    """サービスレベルからZ値を計算"""
    mapping = {0.5: 0.0, 0.8: 0.84, 0.9: 1.28, 0.95: 1.645}
    k = min(mapping.keys(), key=lambda x: abs(x - sl))
    return mapping[k]

def get_sales_series(user, bread, with_dates=False):
    """過去の販売データを取得"""
    db = get_db()
    rows = db.execute(
        "SELECT day, sold FROM records WHERE user=? AND bread=? ORDER BY day ASC",
        (user, bread)
    ).fetchall()

    if not rows:
        if with_dates:
            return pd.Series(dtype=float), pd.Series(dtype='datetime64[ns]')
        return pd.Series(dtype=float)

    # sqlite3.Rowオブジェクトを辞書に変換
    df = pd.DataFrame([dict(row) for row in rows])
    df["sold"] = df["sold"].astype(float)
    df["day"] = pd.to_datetime(df["day"])

    if with_dates:
        return df["sold"], df["day"]
    return df["sold"]

def remove_outliers(series, threshold=2.5):
    """外れ値を除外（IQR法の改良版）"""
    if len(series) < 4:
        return series

    q1 = series.quantile(0.25)
    q3 = series.quantile(0.75)
    iqr = q3 - q1

    if iqr == 0:  # すべての値が同じ場合
        return series

    lower_bound = q1 - threshold * iqr
    upper_bound = q3 + threshold * iqr

    return series[(series >= lower_bound) & (series <= upper_bound)]

def weighted_ma(series, alpha=0.7):
    """加重移動平均を計算（外れ値除外付き）"""
    if series.empty:
        return 0.0

    # 外れ値を除外
    cleaned = remove_outliers(series)
    if cleaned.empty:
        cleaned = series

    s = cleaned.tolist()
    weights = [alpha ** (len(s) - 1 - i) for i in range(len(s))]
    wsum = sum(weights)
    return sum(v * w for v, w in zip(s, weights)) / wsum

def holt_forecast(series):
    """Holt法による予測（フォールバック用）"""
    if len(series) < 3:
        return weighted_ma(series)
    try:
        model = ExponentialSmoothing(
            series,
            trend="add",
            seasonal=None,
            initialization_method="estimated"
        )
        fit = model.fit(optimized=True)
        return float(fit.forecast(1))
    except:
        return weighted_ma(series)

def holt_winters_forecast(series, seasonal_periods=7):
    """Holt-Winters法による予測（最も精度が高い）"""
    # データが十分でない場合はHolt法にフォールバック
    if len(series) < 2 * seasonal_periods:
        return holt_forecast(series)

    try:
        # 外れ値を除外してからモデルを構築
        cleaned = remove_outliers(series)
        if len(cleaned) < 2 * seasonal_periods:
            cleaned = series

        model = ExponentialSmoothing(
            cleaned,
            trend='add',
            seasonal='add',
            seasonal_periods=seasonal_periods,
            initialization_method='estimated'
        )
        fit = model.fit(optimized=True)
        return float(fit.forecast(1)[0])
    except:
        # エラーが発生した場合はHolt法にフォールバック
        return holt_forecast(series)

def get_batch_status(user, bread):
    """バッチごとの在庫状態を取得（FIFO用）"""
    db = get_db()
    today = date.today()

    rows = db.execute(
        """SELECT id, qty, added_date, remaining
           FROM batches
           WHERE user=? AND bread=? AND remaining > 0
           ORDER BY added_date ASC""",
        (user, bread)
    ).fetchall()

    batches = []
    for row in rows:
        added = date.fromisoformat(row["added_date"])
        days_old = (today - added).days
        days_until_expiry = SHELF_DAYS - days_old

        status = "expired" if days_until_expiry <= 0 else "valid"
        urgency = "high" if days_until_expiry == 1 else "medium" if days_until_expiry == 2 else "low"

        batches.append({
            "id": row["id"],
            "qty": row["qty"],
            "remaining": row["remaining"],
            "added_date": row["added_date"],
            "days_old": days_old,
            "days_until_expiry": days_until_expiry,
            "status": status,
            "urgency": urgency
        })

    return batches

def compute_recs(user):
    """注文推奨量を計算（改善版：Holt-Winters法使用）"""
    rec = {}
    today = date.today()
    tomorrow = today + timedelta(days=1)

    for bread in BREADS:
        # 過去の販売データ取得
        sales = get_sales_series(user, bread)

        # 予測値計算 - Holt-Winters法を優先
        if len(sales) >= 14:  # 十分なデータがある場合
            forecast = holt_winters_forecast(sales, seasonal_periods=7)
        elif len(sales) >= 3:  # 少ないデータの場合はHolt法
            forecast = holt_forecast(sales)
        else:  # データが非常に少ない場合は加重移動平均
            forecast = weighted_ma(sales)

        # 標準偏差計算（外れ値を除外）
        if len(sales) >= 4:
            cleaned_sales = remove_outliers(sales[-HISTORY_DAYS:])
            sigma = float(cleaned_sales.std(ddof=0)) if len(cleaned_sales) >= 2 else 0.0
        elif len(sales) >= 2:
            sigma = float(sales[-HISTORY_DAYS:].std(ddof=0))
        else:
            sigma = 0.0

        # 安全在庫係数
        z = compute_z(SERVICE_LEVEL)

        # 中国祝日・イベントの影響を反映
        impact_multiplier = weather_holiday.get_impact_multiplier(tomorrow)
        z *= impact_multiplier

        # 目標在庫
        target = forecast + z * sigma

        # 現在の在庫（バッチ合計）
        db = get_db()
        rem = db.execute(
            "SELECT SUM(remaining) as rem FROM batches WHERE user=? AND bread=?",
            (user, bread)
        ).fetchone()["rem"] or 0

        # 注文推奨量
        order_qty = max(0, math.ceil(target - rem))

        # バッチ状態取得
        batches = get_batch_status(user, bread)

        rec[bread] = {
            "forecast": round(forecast, 2),
            "sigma": round(sigma, 2),
            "target": round(target, 2),
            "leftover": int(rem),
            "order": int(order_qty),
            "impact_multiplier": round(impact_multiplier, 2),
            "batches": batches,
            "method": "Holt-Winters" if len(sales) >= 14 else "Holt" if len(sales) >= 3 else "WMA"
        }

    return rec

def backtest_model(user, bread, days=7):
    """バックテスト（MAE/RMSE計算）- 改善版Holt-Winters使用"""
    sales = get_sales_series(user, bread)

    if len(sales) < days + 7:
        return {"error": "データ不足", "mae": None, "rmse": None, "method": "N/A"}

    errors = []
    method_used = "Unknown"

    for i in range(len(sales) - days, len(sales)):
        historical = sales[:i]
        actual = sales.iloc[i]

        # 最適な手法を選択
        if len(historical) >= 14:
            predicted = holt_winters_forecast(historical, seasonal_periods=7)
            method_used = "Holt-Winters"
        elif len(historical) >= 3:
            predicted = holt_forecast(historical)
            method_used = "Holt"
        else:
            predicted = weighted_ma(historical)
            method_used = "WMA"

        errors.append(actual - predicted)

    errors = np.array(errors)
    mae = np.mean(np.abs(errors))
    rmse = np.sqrt(np.mean(errors ** 2))

    return {
        "mae": round(float(mae), 2),
        "rmse": round(float(rmse), 2),
        "samples": len(errors),
        "method": method_used
    }

def get_recent_records(user, days=30):
    """最近のレコードを取得"""
    db = get_db()
    cutoff = (date.today() - timedelta(days=days)).isoformat()

    rows = db.execute(
        """SELECT id, day, bread, sold, leftover, created_at
           FROM records
           WHERE user=? AND day>=?
           ORDER BY day DESC, created_at DESC""",
        (user, cutoff)
    ).fetchall()

    return [dict(row) for row in rows]

def update_record(record_id, sold, leftover):
    """レコードを更新"""
    db = get_db()
    cur = db.cursor()
    cur.execute(
        "UPDATE records SET sold=?, leftover=? WHERE id=?",
        (sold, leftover, record_id)
    )
    db.commit()

def delete_record(record_id):
    """レコードを削除"""
    db = get_db()
    cur = db.cursor()
    cur.execute("DELETE FROM records WHERE id=?", (record_id,))
    db.commit()
