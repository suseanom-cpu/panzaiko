"""
HTTPS対応版のFlaskアプリケーション

使用方法:
1. まず setup_https.sh を実行して証明書を生成
2. python app_https.py で起動
"""

from flask import Flask, render_template, request, session, redirect, url_for, jsonify, g
import os
from datetime import date, datetime, timedelta
from db import init_db, get_db, log_action, close_db
from forecast import compute_recs, backtest_model, BREADS, get_recent_records, update_record, delete_record
import weather_holiday

# 現在のディレクトリ
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Flaskアプリ作成
app = Flask(__name__, template_folder=os.path.join(BASE_DIR, '../templates'))
app.secret_key = "your_secure_random_secret_key_here_change_this_in_production"

# データベース初期化
init_db(app)
app.teardown_appcontext(close_db)

# ============================================
# ページルート
# ============================================

@app.route("/", methods=["GET"])
def index():
    """ログイン画面"""
    if "user" in session:
        return redirect(url_for("dashboard"))
    return render_template("index.html")

@app.route("/dashboard", methods=["GET"])
def dashboard():
    """ダッシュボード"""
    if "user" not in session:
        return redirect(url_for("index"))
    return render_template("dashboard.html", username=session["user"])

# ============================================
# API エンドポイント
# ============================================

@app.route("/api/weather", methods=["GET"])
def api_weather():
    """神戸市中央区の天気情報を取得"""
    weather = weather_holiday.get_kobe_weather()
    return jsonify(weather if weather else {"error": "天気情報を取得できませんでした"})

@app.route("/api/events", methods=["GET"])
def api_events():
    """中国祝日・イベント情報を取得"""
    events = weather_holiday.get_china_holidays_and_events()
    return jsonify({"events": events})

@app.route("/api/login", methods=["POST"])
def api_login():
    """ログイン処理"""
    data = request.get_json()
    username = data.get("username", "").strip()

    if not username:
        return jsonify({"success": False, "error": "名前を入力してください"}), 400

    session["user"] = username
    log_action(username, "login", "ユーザーがログインしました")

    return jsonify({"success": True, "username": username})

@app.route("/api/logout", methods=["POST"])
def api_logout():
    """ログアウト処理"""
    user = session.get("user")
    if user:
        log_action(user, "logout", "ユーザーがログアウトしました")
    session.pop("user", None)
    return jsonify({"success": True})

@app.route("/api/dashboard", methods=["GET"])
def api_dashboard():
    """ダッシュボードデータを取得"""
    if "user" not in session:
        return jsonify({"error": "未ログイン"}), 401

    user = session["user"]
    recommendations = compute_recs(user)

    # 天気情報と祝日情報を取得
    weather = weather_holiday.get_kobe_weather()
    events = weather_holiday.get_china_holidays_and_events()

    # 明日が中国の祝日かどうか
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    holiday_tomorrow = any(e.get("date") == tomorrow for e in events)

    return jsonify({
        "success": True,
        "recommendations": recommendations,
        "weather": weather if weather else {"error": "天気情報を取得できませんでした"},
        "holidayTomorrowChina": holiday_tomorrow,
        "events": events
    })

@app.route("/api/input", methods=["POST"])
def api_input():
    """データ入力（過去日付対応）"""
    if "user" not in session:
        return jsonify({"error": "未ログイン"}), 401

    user = session["user"]
    data = request.get_json()

    # 日付を取得（指定がない場合は今日）
    target_date = data.get("date", date.today().isoformat())

    # 日付の妥当性チェック
    try:
        date.fromisoformat(target_date)
    except ValueError:
        return jsonify({"error": "無効な日付形式です"}), 400

    db = get_db()
    cur = db.cursor()

    # 同日の既存データをチェック
    existing = {}
    for bread in BREADS:
        row = cur.execute(
            "SELECT id FROM records WHERE user=? AND day=? AND bread=?",
            (user, target_date, bread)
        ).fetchone()
        if row:
            existing[bread] = row["id"]

    for bread in BREADS:
        bread_data = data.get(bread, {})
        purchased = int(bread_data.get("purchased", 0))
        leftover = int(bread_data.get("leftover", 0))

        if bread in existing:
            # 既存データを更新（上書き）
            cur.execute(
                """UPDATE records SET sold=?, leftover=? WHERE id=?""",
                (purchased, leftover, existing[bread])
            )
        else:
            # 新規データを挿入
            cur.execute(
                """INSERT INTO records (user, day, bread, sold, leftover, created_at)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (user, target_date, bread, purchased, leftover, datetime.utcnow().isoformat())
            )

        # バッチとして在庫追加（余りがある場合）※今日のデータのみ
        if target_date == date.today().isoformat():
            if bread in existing:
                cur.execute(
                    "DELETE FROM batches WHERE user=? AND bread=? AND added_date=?",
                    (user, bread, target_date)
                )

            if leftover > 0:
                cur.execute(
                    """INSERT INTO batches (user, bread, qty, added_date, remaining)
                       VALUES (?, ?, ?, ?, ?)""",
                    (user, bread, leftover, target_date, leftover)
                )

    db.commit()
    log_action(user, "input_data", f"データ入力 ({target_date}): {data}")

    return jsonify({"success": True})

@app.route("/api/records", methods=["GET"])
def api_records():
    """最近のレコードを取得"""
    if "user" not in session:
        return jsonify({"error": "未ログイン"}), 401

    user = session["user"]
    days = int(request.args.get("days", 30))
    records = get_recent_records(user, days)

    return jsonify({"success": True, "records": records})

@app.route("/api/records/<int:record_id>", methods=["PUT"])
def api_update_record(record_id):
    """レコードを更新"""
    if "user" not in session:
        return jsonify({"error": "未ログイン"}), 401

    user = session["user"]
    data = request.get_json()
    sold = int(data.get("sold", 0))
    leftover = int(data.get("leftover", 0))

    update_record(record_id, sold, leftover)
    log_action(user, "update_record", f"レコード更新: ID={record_id}, sold={sold}, leftover={leftover}")

    return jsonify({"success": True})

@app.route("/api/records/<int:record_id>", methods=["DELETE"])
def api_delete_record(record_id):
    """レコードを削除"""
    if "user" not in session:
        return jsonify({"error": "未ログイン"}), 401

    user = session["user"]
    delete_record(record_id)
    log_action(user, "delete_record", f"レコード削除: ID={record_id}")

    return jsonify({"success": True})

@app.route("/api/backtest", methods=["GET"])
def api_backtest():
    """バックテスト実行"""
    if "user" not in session:
        return jsonify({"error": "未ログイン"}), 401

    user = session["user"]
    results = {}

    for bread in BREADS:
        results[bread] = backtest_model(user, bread)

    return jsonify({"success": True, "results": results})

@app.route("/api/logs", methods=["POST"])
def api_logs():
    """ログ取得（パスワード保護）"""
    data = request.get_json()
    password = data.get("password", "")

    if password != "047":
        return jsonify({"error": "パスワードが正しくありません"}), 403

    db = get_db()
    rows = db.execute(
        "SELECT * FROM logs ORDER BY created_at DESC LIMIT 200"
    ).fetchall()

    logs = [dict(row) for row in rows]

    return jsonify({"success": True, "logs": logs})

if __name__ == "__main__":
    # 証明書のパスを設定
    cert_path = os.path.join(BASE_DIR, '../../certs/cert.pem')
    key_path = os.path.join(BASE_DIR, '../../certs/key.pem')

    # 証明書が存在するか確認
    if not os.path.exists(cert_path) or not os.path.exists(key_path):
        print("❌ エラー: HTTPS証明書が見つかりません")
        print("まず setup_https.sh を実行して証明書を生成してください:")
        print("  cd /Users/seanm/Downloads/untitled\\ folder\\ 13/panzaiko")
        print("  bash setup_https.sh")
        exit(1)

    print("=" * 60)
    print("HTTPS対応サーバーを起動しています...")
    print("=" * 60)
    print(f"証明書: {cert_path}")
    print(f"秘密鍵: {key_path}")
    print("=" * 60)

    # HTTPSサーバーとして起動
    app.run(
        host="0.0.0.0",
        port=8443,  # HTTPS用の標準的なポート
        debug=True,
        ssl_context=(cert_path, key_path)
    )
