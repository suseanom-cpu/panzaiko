"""
複数の予測手法を比較するスクリプト

実装する手法:
1. 単純移動平均 (Simple Moving Average)
2. 加重移動平均 (Weighted Moving Average)
3. 指数平滑法 (Exponential Smoothing)
4. Holt法 (Holt's Linear Trend)
5. Holt-Winters法 (季節性考慮)
6. 曜日効果を加えた加重移動平均
"""

import sqlite3
import pandas as pd
import numpy as np
from datetime import date, timedelta
from statsmodels.tsa.holtwinters import ExponentialSmoothing, SimpleExpSmoothing, Holt
import warnings
warnings.filterwarnings('ignore')

BREADS = ["細パン", "太パン", "サンドパン", "バゲット"]

# 曜日の重み付け（実データから調整可能）
WEEKDAY_WEIGHTS = {
    0: 0.9,   # 月曜日
    1: 0.95,  # 火曜日
    2: 1.0,   # 水曜日
    3: 1.0,   # 木曜日
    4: 1.1,   # 金曜日
    5: 1.2,   # 土曜日
    6: 1.15   # 日曜日
}

def get_sales_data(user, bread):
    """データベースから販売データを取得"""
    db = sqlite3.connect('breads_full.db')
    query = """
    SELECT day, sold
    FROM records
    WHERE user=? AND bread=?
    ORDER BY day ASC
    """
    df = pd.read_sql_query(query, db, params=(user, bread))
    db.close()

    if len(df) == 0:
        return pd.Series(dtype=float), pd.Series(dtype='datetime64[ns]')

    df['day'] = pd.to_datetime(df['day'])
    return df['sold'].values, df['day'].values

def simple_moving_average(series, window=7):
    """単純移動平均"""
    if len(series) < window:
        return np.mean(series) if len(series) > 0 else 0
    return np.mean(series[-window:])

def weighted_moving_average(series, alpha=0.7):
    """加重移動平均（新しいデータに高い重み）"""
    if len(series) == 0:
        return 0

    weights = np.array([alpha ** (len(series) - 1 - i) for i in range(len(series))])
    weights = weights / weights.sum()
    return np.sum(series * weights)

def exponential_smoothing(series):
    """指数平滑法"""
    if len(series) < 2:
        return np.mean(series) if len(series) > 0 else 0

    try:
        model = SimpleExpSmoothing(series)
        fit = model.fit(optimized=True)
        return fit.forecast(1)[0]
    except:
        return np.mean(series)

def holt_method(series):
    """Holt法（トレンド考慮）"""
    if len(series) < 3:
        return np.mean(series) if len(series) > 0 else 0

    try:
        model = Holt(series)
        fit = model.fit(optimized=True)
        return fit.forecast(1)[0]
    except:
        return np.mean(series)

def holt_winters_method(series, seasonal_periods=7):
    """Holt-Winters法（季節性考慮）"""
    if len(series) < 2 * seasonal_periods:
        return holt_method(series)

    try:
        model = ExponentialSmoothing(
            series,
            trend='add',
            seasonal='add',
            seasonal_periods=seasonal_periods
        )
        fit = model.fit(optimized=True)
        return fit.forecast(1)[0]
    except:
        return holt_method(series)

def weekday_weighted_ma(series, dates_data=None, alpha=0.7):
    """曜日効果を考慮した加重移動平均"""
    if len(series) == 0:
        return 0

    # 基本的な加重移動平均を計算
    base_forecast = weighted_moving_average(series, alpha)

    # 明日の曜日を取得
    tomorrow = date.today() + timedelta(days=1)
    tomorrow_weekday = tomorrow.weekday()

    # 曜日効果を適用
    weekday_factor = WEEKDAY_WEIGHTS.get(tomorrow_weekday, 1.0)

    return base_forecast * weekday_factor

def backtest_method(method_func, series, dates, test_days=7, **kwargs):
    """
    バックテスト実行

    Args:
        method_func: 予測関数
        series: 売上データ
        dates: 日付データ
        test_days: テスト日数
        **kwargs: 予測関数に渡す追加パラメータ

    Returns:
        dict: MAE, RMSE, MAPE などの評価指標
    """
    if len(series) < test_days + 7:
        return {
            'mae': None,
            'rmse': None,
            'mape': None,
            'error': 'データ不足'
        }

    errors = []
    absolute_errors = []
    percentage_errors = []

    for i in range(len(series) - test_days, len(series)):
        train_series = series[:i]
        train_dates = dates[:i] if dates is not None else None
        actual = series[i]

        # 予測実行
        if 'dates_data' in kwargs:
            predicted = method_func(train_series, dates_data=train_dates, **{k: v for k, v in kwargs.items() if k != 'dates_data'})
        else:
            predicted = method_func(train_series, **kwargs)

        error = actual - predicted
        errors.append(error)
        absolute_errors.append(abs(error))

        # MAPE計算（実際の値が0でない場合）
        if actual > 0:
            percentage_errors.append(abs(error / actual) * 100)

    mae = np.mean(absolute_errors)
    rmse = np.sqrt(np.mean(np.array(errors) ** 2))
    mape = np.mean(percentage_errors) if percentage_errors else None

    return {
        'mae': round(mae, 2),
        'rmse': round(rmse, 2),
        'mape': round(mape, 2) if mape is not None else None,
        'samples': len(errors)
    }

def compare_all_methods(user='TestUser'):
    """すべての予測手法を比較"""

    results = {}

    for bread in BREADS:
        print(f"\n{'='*60}")
        print(f"パン種類: {bread}")
        print(f"{'='*60}")

        # データ取得
        series, dates = get_sales_data(user, bread)

        if len(series) < 14:
            print(f"⚠️ データ不足（{len(series)}件）- スキップ")
            continue

        print(f"データ数: {len(series)}件")
        print(f"期間: {dates[0]} 〜 {dates[-1]}")
        print(f"平均売上: {np.mean(series):.2f}")
        print(f"標準偏差: {np.std(series):.2f}")

        methods = {
            '単純移動平均(7日)': (simple_moving_average, {'window': 7}),
            '加重移動平均': (weighted_moving_average, {'alpha': 0.7}),
            '指数平滑法': (exponential_smoothing, {}),
            'Holt法': (holt_method, {}),
            'Holt-Winters法': (holt_winters_method, {'seasonal_periods': 7}),
            '曜日加重移動平均': (weekday_weighted_ma, {'dates_data': True, 'alpha': 0.7})
        }

        bread_results = {}

        print(f"\n{'手法':<20} {'MAE':<10} {'RMSE':<10} {'MAPE(%)':<10}")
        print("-" * 60)

        for method_name, (method_func, params) in methods.items():
            result = backtest_method(method_func, series, dates, test_days=7, **params)
            bread_results[method_name] = result

            if result['mae'] is not None:
                mape_str = f"{result['mape']:.2f}" if result['mape'] is not None else "N/A"
                print(f"{method_name:<20} {result['mae']:<10.2f} {result['rmse']:<10.2f} {mape_str:<10}")
            else:
                print(f"{method_name:<20} {result['error']}")

        # 最良の手法を特定（MAEが最小）
        valid_results = {k: v for k, v in bread_results.items() if v['mae'] is not None}
        if valid_results:
            best_method = min(valid_results, key=lambda k: valid_results[k]['mae'])
            print(f"\n✓ 最良の手法: {best_method} (MAE: {valid_results[best_method]['mae']:.2f})")

        results[bread] = bread_results

    return results

def export_results_to_csv(results):
    """結果をCSVにエクスポート"""
    rows = []
    for bread, methods in results.items():
        for method_name, metrics in methods.items():
            rows.append({
                'パン種類': bread,
                '予測手法': method_name,
                'MAE': metrics.get('mae'),
                'RMSE': metrics.get('rmse'),
                'MAPE(%)': metrics.get('mape'),
                'サンプル数': metrics.get('samples'),
                'エラー': metrics.get('error', '')
            })

    df = pd.DataFrame(rows)
    df.to_csv('forecast_comparison_results.csv', index=False, encoding='utf-8-sig')
    print(f"\n✓ 結果をCSVに保存しました: forecast_comparison_results.csv")

    return df

if __name__ == "__main__":
    print("="*60)
    print("予測手法比較プログラム")
    print("="*60)

    # すべての手法を比較
    results = compare_all_methods(user='TestUser')

    # 結果をCSVにエクスポート
    df_results = export_results_to_csv(results)

    print("\n" + "="*60)
    print("比較完了")
    print("="*60)

    # 総合的な推奨を表示
    print("\n【総合評価】")
    for bread in BREADS:
        if bread in results:
            valid_results = {k: v for k, v in results[bread].items() if v.get('mae') is not None}
            if valid_results:
                best_method = min(valid_results, key=lambda k: valid_results[k]['mae'])
                best_mae = valid_results[best_method]['mae']
                print(f"{bread}: {best_method} (MAE: {best_mae:.2f})")
