# 🥖 パン在庫管理システム (Panzaiko)

AIを活用した高精度なパンの在庫管理・需要予測システム

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/flask-3.0-green)](https://flask.palletsprojects.com/)

## ✨ 特徴

- 📊 **高精度な需要予測**: Holt-Winters法により30-50%の誤差削減を実現
- 🗓️ **季節性を自動考慮**: 週単位の売上パターンを自動検出
- 🌤️ **天気・イベント連動**: 天気予報と中国の祝日を考慮した予測
- 📦 **FIFO在庫管理**: 消費期限を考慮した先入先出管理
- 📈 **リアルタイムダッシュボード**: 直感的なUIで在庫状況を可視化
- 🔒 **HTTPS対応**: Let's Encryptによる安全な通信
- 📱 **レスポンシブデザイン**: PCでもスマホでも快適に操作

## 🚀 クイックスタート

### ローカル環境での起動（開発用）

```bash
# リポジトリをクローン
cd /Users/seanm/Downloads/untitled\ folder\ 13/panzaiko

# 仮想環境を作成
python3 -m venv venv
source venv/bin/activate

# 依存パッケージをインストール
pip install -r app/backend/requirements.txt

# サーバーを起動
cd app/backend
python app.py
```

**アクセス**: http://localhost:8080

### 本番環境へのデプロイ

```bash
# 環境変数を設定
export SERVER_USER="root"
export SERVER_HOST="your-server-ip"
export DOMAIN="yourdomain.com"

# デプロイスクリプトを実行
./deploy.sh
```

詳細は [DEPLOYMENT.md](DEPLOYMENT.md) を参照してください。

## 📊 予測精度

31日間のテストデータで検証した結果：

| パン種類 | 予測手法 | MAE | RMSE | MAPE(%) |
|---------|---------|-----|------|---------|
| 細パン | Holt-Winters | **2.39** | 2.90 | 12.18 |
| 太パン | 指数平滑法 | **1.92** | 2.84 | 13.62 |
| サンドパン | Holt-Winters | **3.36** | 3.66 | 12.09 |
| バゲット | Holt-Winters | **1.70** | 2.24 | 18.79 |

従来のHolt法と比較して **30-50%の精度向上** を実現。

## 🛠️ 技術スタック

### バックエンド
- **Python 3.9+**
- **Flask 3.0**: Webフレームワーク
- **SQLite**: データベース
- **Statsmodels**: 時系列分析・予測
- **Pandas & NumPy**: データ処理
- **Gunicorn**: WSGIサーバー

### フロントエンド
- **HTML/CSS/JavaScript**: ピュアJS実装
- **レスポンシブデザイン**: モバイル対応

### インフラ
- **Nginx**: リバースプロキシ
- **Let's Encrypt**: SSL/TLS証明書
- **systemd**: サービス管理

## 📁 プロジェクト構造

```
panzaiko/
├── app/
│   ├── backend/
│   │   ├── app.py              # メインアプリケーション
│   │   ├── app_https.py        # HTTPS版
│   │   ├── forecast.py         # 予測エンジン
│   │   ├── db.py               # データベース管理
│   │   ├── weather_holiday.py  # 外部API連携
│   │   ├── config.py           # 設定ファイル
│   │   └── requirements.txt    # 依存パッケージ
│   └── templates/
│       ├── index.html          # ログイン画面
│       └── dashboard.html      # ダッシュボード
├── forecast_comparison.py      # 予測手法比較ツール
├── deploy.sh                   # デプロイスクリプト
├── setup_https.sh              # HTTPS設定スクリプト
├── panzaiko.service            # systemdサービス
├── nginx.conf                  # Nginx設定
├── gunicorn.conf.py            # Gunicorn設定
├── DEPLOYMENT.md               # デプロイ手順書
├── IMPROVEMENTS.md             # 改善レポート
└── README.md                   # このファイル
```

## 📖 ドキュメント

- [DEPLOYMENT.md](DEPLOYMENT.md) - 詳細なデプロイ手順
- [IMPROVEMENTS.md](IMPROVEMENTS.md) - 改善内容と検証結果
- [.env.example](.env.example) - 環境変数のサンプル

## 🎯 主な機能

### 1. ダッシュボード
- 明日の注文推奨量を表示
- 現在の在庫状況をリアルタイム表示
- 消費期限が近いパンを警告
- 天気予報と中国祝日の情報を表示

### 2. データ入力
- 簡単な入力フォーム
- 過去日付のデータ入力にも対応
- 自動で在庫を更新

### 3. データ修正
- 過去のデータを編集・削除
- 今日のデータを直接編集可能

### 4. デバッグ機能
- バックテストで精度を確認
- MAE/RMSE/MAPEを表示
- ログ閲覧（パスワード保護）

## 🔐 セキュリティ

- ✅ HTTPS対応（Let's Encrypt）
- ✅ セッション管理
- ✅ パスワード保護されたログ閲覧
- ✅ XSS/CSRF対策
- ✅ セキュリティヘッダー設定

## 📊 データエクスポート

すべてのデータをCSV形式でエクスポート可能：

```bash
# 比較ツールを実行
python forecast_comparison.py
```

生成されるファイル：
- `sales_data_export.csv` - 全販売データ
- `test_data_31days.csv` - テストデータ
- `forecast_comparison_results.csv` - 予測精度比較

## 🧪 テスト

```bash
# 予測手法の比較テストを実行
python forecast_comparison.py

# 31日分のテストデータを自動生成し、
# 6種類の予測手法を比較します
```

## 🤝 貢献

貢献を歓迎します！以下の手順で参加してください：

1. このリポジトリをフォーク
2. 機能ブランチを作成 (`git checkout -b feature/AmazingFeature`)
3. 変更をコミット (`git commit -m 'Add some AmazingFeature'`)
4. ブランチにプッシュ (`git push origin feature/AmazingFeature`)
5. プルリクエストを作成

## 📝 ライセンス

MIT License - 詳細は [LICENSE](LICENSE) ファイルを参照

## 👥 作者

開発: Claude (Anthropic AI)
プロジェクト管理: Sean M

## 📞 サポート

問題が発生した場合は、Issueを作成してください。

---

**最終更新**: 2025-10-28
**バージョン**: 2.0
