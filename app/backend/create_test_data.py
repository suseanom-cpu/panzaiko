#!/usr/bin/env python3
"""
テスト用データ作成スクリプト
過去60日分の販売データを生成します（バックテスト用に十分なデータ）
"""
import sqlite3
from datetime import date, timedelta, datetime
import random

DB_PATH = "breads_full.db"
BREADS = ["細パン", "太パン", "サンドパン", "バゲット"]
TEST_USER = "テストユーザー"

# パンごとの基本販売数（平均値）
BASE_SALES = {
    "細パン": 25,
    "太パン": 18,
    "サンドパン": 22,
    "バゲット": 15
}

def create_test_data():
    """過去60日分のテストデータを作成（バックテスト用）"""
    db = sqlite3.connect(DB_PATH)
    cur = db.cursor()

    print(f"テストデータを作成中... ユーザー: {TEST_USER}")
    print("バックテスト用に60日分のデータを生成します")

    # 既存のテストユーザーのデータを削除
    cur.execute("DELETE FROM records WHERE user=?", (TEST_USER,))
    cur.execute("DELETE FROM batches WHERE user=?", (TEST_USER,))
    db.commit()

    # 過去60日分のデータを生成
    today = date.today()

    for days_ago in range(60, 0, -1):
        target_date = today - timedelta(days=days_ago)
        date_str = target_date.isoformat()

        for bread in BREADS:
            base_sales = BASE_SALES[bread]

            # 曜日効果を追加（週末は販売数が増える）
            weekday = target_date.weekday()
            weekday_multiplier = 1.3 if weekday in [5, 6] else 1.0

            # 季節効果を追加
            season_multiplier = 1.0
            if target_date.month in [12, 1, 2]:  # 冬
                season_multiplier = 1.1
            elif target_date.month in [7, 8]:  # 夏
                season_multiplier = 0.9

            # 販売数にランダムな変動を加える（±30%）
            variation = random.uniform(0.7, 1.3)
            sold = int(base_sales * variation * weekday_multiplier * season_multiplier)

            # 余りは0-5個の範囲でランダム
            leftover = random.randint(0, 5)

            # レコードを挿入
            cur.execute(
                """INSERT INTO records (user, day, bread, sold, leftover, created_at)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (TEST_USER, date_str, bread, sold, leftover, datetime.utcnow().isoformat())
            )

            # 余りがある場合はバッチとして登録
            if leftover > 0:
                cur.execute(
                    """INSERT INTO batches (user, bread, qty, added_date, remaining)
                       VALUES (?, ?, ?, ?, ?)""",
                    (TEST_USER, bread, leftover, date_str, leftover)
                )

        print(f"  {date_str}: 完了")

    db.commit()

    # データ件数を確認
    record_count = cur.execute("SELECT COUNT(*) FROM records WHERE user=?", (TEST_USER,)).fetchone()[0]
    batch_count = cur.execute("SELECT COUNT(*) FROM batches WHERE user=?", (TEST_USER,)).fetchone()[0]

    print(f"\n[OK] テストデータの作成が完了しました")
    print(f"  - レコード数: {record_count}件")
    print(f"  - バッチ数: {batch_count}件")
    print(f"  - ユーザー名: {TEST_USER}")
    print(f"\nログイン時に「{TEST_USER}」と入力してください")

    db.close()

if __name__ == "__main__":
    create_test_data()
