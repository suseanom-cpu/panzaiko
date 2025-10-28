# 🚀 デプロイ前チェックリスト

サーバーへアップロードする前に、以下を確認してください。

## ✅ 準備完了項目

### サーバー情報
- [ ] サーバーのIPアドレスを確認
- [ ] SSHでサーバーにアクセス可能
- [ ] sudo権限があることを確認
- [ ] ドメイン名を取得済み
- [ ] DNSレコードを設定済み（A/AAAAレコード）

### ローカル環境
- [ ] すべてのコードがテスト済み
- [ ] 開発環境でアプリケーションが正常に動作
- [ ] データベースのバックアップを作成
- [ ] 重要なCSVファイルをバックアップ

### セキュリティ
- [ ] SECRET_KEYをランダムな値に変更
- [ ] ADMIN_PASSWORDを安全なパスワードに変更
- [ ] APIキーを確認（OpenWeather）
- [ ] .gitignoreで機密情報を除外

## 📦 デプロイファイル確認

すべてのファイルが揃っていることを確認：

```bash
cd /Users/seanm/Downloads/untitled\ folder\ 13/panzaiko
ls -la
```

### 必須ファイル
- [x] app/backend/app.py
- [x] app/backend/forecast.py
- [x] app/backend/db.py
- [x] app/backend/weather_holiday.py
- [x] app/backend/requirements.txt
- [x] app/backend/config.py
- [x] app/templates/index.html
- [x] app/templates/dashboard.html

### デプロイ関連ファイル
- [x] deploy.sh
- [x] .gitignore
- [x] .env.example
- [x] panzaiko.service
- [x] nginx.conf
- [x] gunicorn.conf.py
- [x] setup_https.sh

### ドキュメント
- [x] README.md
- [x] DEPLOYMENT.md
- [x] IMPROVEMENTS.md
- [x] CHECKLIST.md

## 🔧 デプロイ方法の選択

### 方法1: 自動デプロイスクリプト（推奨）

```bash
# 環境変数を設定
export SERVER_USER="root"
export SERVER_HOST="123.45.67.89"  # ← 実際のIPに変更
export DOMAIN="yourdomain.com"      # ← 実際のドメインに変更

# スクリプトを実行
./deploy.sh
```

### 方法2: 手動デプロイ

[DEPLOYMENT.md](DEPLOYMENT.md) の手順に従ってください。

## 📋 デプロイ後の確認

### 1. サービスの起動確認

```bash
ssh root@your-server-ip

# サービス状態を確認
systemctl status panzaiko
systemctl status nginx

# ログを確認
journalctl -u panzaiko -n 50
```

### 2. Webアクセスの確認

ブラウザで以下にアクセス：

- [ ] HTTP: `http://yourdomain.com` → HTTPSにリダイレクトされる
- [ ] HTTPS: `https://yourdomain.com` → 正常に表示される
- [ ] ログイン機能が動作する
- [ ] ダッシュボードが表示される
- [ ] データ入力ができる

### 3. SSL証明書の確認

```bash
# 証明書の有効期限を確認
openssl s_client -connect yourdomain.com:443 -servername yourdomain.com < /dev/null 2>/dev/null | openssl x509 -noout -dates

# ブラウザで鍵アイコンをクリックして証明書を確認
```

### 4. パフォーマンステスト

```bash
# レスポンスタイムを確認
curl -o /dev/null -s -w "Time: %{time_total}s\n" https://yourdomain.com

# 負荷テスト（オプション）
ab -n 100 -c 10 https://yourdomain.com/
```

## 🔒 セキュリティチェック

### ファイアウォール
```bash
ufw status

# 必要なポートのみ開いていることを確認
# - 22 (SSH)
# - 80 (HTTP)
# - 443 (HTTPS)
```

### パーミッション
```bash
# アプリケーションディレクトリ
ls -la /var/www/panzaiko

# ログディレクトリ
ls -la /var/log/panzaiko

# データベース
ls -la /var/www/panzaiko/*.db
```

### 環境変数
```bash
# .envファイルが適切に保護されているか
ls -la /var/www/panzaiko/.env
# → -rw------- (600) であること
```

## 📊 バックアップの設定

```bash
# バックアップスクリプトを確認
cat /root/backup_panzaiko.sh

# Cronジョブを確認
crontab -l
```

## 🎯 最終チェック

すべての項目を確認してから本番稼働：

- [ ] アプリケーションが正常に動作
- [ ] HTTPSが正しく設定されている
- [ ] ファイアウォールが適切に設定されている
- [ ] バックアップが自動実行される
- [ ] ログローテーションが設定されている
- [ ] 監視・アラート設定（オプション）
- [ ] ドキュメントが最新の状態
- [ ] チームメンバーに共有

## 🆘 トラブルシューティング

問題が発生した場合：

1. **ログを確認**
   ```bash
   journalctl -u panzaiko -f
   tail -f /var/log/nginx/panzaiko_error.log
   ```

2. **サービスを再起動**
   ```bash
   systemctl restart panzaiko
   systemctl restart nginx
   ```

3. **手動起動でデバッグ**
   ```bash
   cd /var/www/panzaiko
   source venv/bin/activate
   cd app/backend
   python app.py
   ```

4. **ドキュメントを参照**
   - [DEPLOYMENT.md](DEPLOYMENT.md) - デプロイ手順
   - [IMPROVEMENTS.md](IMPROVEMENTS.md) - システム詳細

## 📞 サポート

デプロイに問題がある場合は、以下の情報を含めてIssueを作成してください：

- エラーメッセージ
- ログファイルの内容
- 実行したコマンド
- サーバーのOS・バージョン

---

✅ すべての項目を確認したら、デプロイを開始してください！

**Good luck! 🚀**
