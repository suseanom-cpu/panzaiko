# パン在庫管理システム - デプロイ手順書

## 📋 目次

1. [準備](#準備)
2. [サーバー要件](#サーバー要件)
3. [デプロイ方法](#デプロイ方法)
4. [手動デプロイ手順](#手動デプロイ手順)
5. [トラブルシューティング](#トラブルシューティング)
6. [メンテナンス](#メンテナンス)

---

## 準備

### 1. 必要な情報を収集

- **サーバーIPアドレス**: `your-server-ip`
- **ドメイン名**: `yourdomain.com`
- **SSHユーザー**: `root` または `sudo権限を持つユーザー`
- **メールアドレス**: SSL証明書用

### 2. DNSの設定

ドメインのDNSレコードを設定します：

```
A    yourdomain.com     -> サーバーのIPアドレス
A    www.yourdomain.com -> サーバーのIPアドレス
```

DNS反映には最大48時間かかる場合があります。

---

## サーバー要件

### 推奨スペック

- **OS**: Ubuntu 20.04 LTS / 22.04 LTS
- **RAM**: 最低 1GB（推奨 2GB以上）
- **CPU**: 1コア以上
- **ストレージ**: 10GB以上の空き容量

### 必要なソフトウェア

- Python 3.9以上
- Nginx
- Certbot（Let's Encrypt用）
- systemd

---

## デプロイ方法

### 🚀 方法1: 自動デプロイスクリプト（推奨）

最も簡単な方法です。

#### 1. 環境変数を設定

```bash
export SERVER_USER="root"                    # SSHユーザー名
export SERVER_HOST="your-server-ip"          # サーバーIP
export DOMAIN="yourdomain.com"               # ドメイン名
```

#### 2. デプロイスクリプトを実行

```bash
cd /Users/seanm/Downloads/untitled\ folder\ 13/panzaiko
./deploy.sh
```

スクリプトが自動的に以下を実行します：

1. ✅ ファイルをサーバーにアップロード
2. ✅ 必要なパッケージをインストール
3. ✅ Python仮想環境を構築
4. ✅ Systemdサービスを設定
5. ✅ Nginxを設定
6. ✅ SSL証明書を取得（オプション）
7. ✅ サービスを起動

#### 3. アクセス確認

ブラウザで以下にアクセス：

- HTTP: `http://yourdomain.com`
- HTTPS: `https://yourdomain.com`

---

### 🔧 方法2: 手動デプロイ（上級者向け）

細かい制御が必要な場合は手動でデプロイします。

#### Step 1: ファイルをサーバーにアップロード

```bash
# ローカルマシンで実行
cd /Users/seanm/Downloads/untitled\ folder\ 13/panzaiko

# rsyncでアップロード
rsync -avz --exclude-from='.gitignore' \
    --exclude='.git' \
    --exclude='venv' \
    --exclude='*.db' \
    --exclude='certs' \
    ./ root@your-server-ip:/var/www/panzaiko/
```

または、Gitを使用：

```bash
# サーバーで実行
cd /var/www
git clone https://github.com/yourusername/panzaiko.git
cd panzaiko
```

#### Step 2: サーバー上でセットアップ

```bash
# サーバーにSSH接続
ssh root@your-server-ip

# 必要なパッケージをインストール
apt-get update
apt-get install -y python3 python3-pip python3-venv nginx certbot python3-certbot-nginx

# アプリケーションディレクトリに移動
cd /var/www/panzaiko

# Python仮想環境を作成
python3 -m venv venv
source venv/bin/activate

# 依存パッケージをインストール
pip install --upgrade pip
pip install -r app/backend/requirements.txt
```

#### Step 3: 環境変数を設定

```bash
# .envファイルを作成
cp .env.example .env
nano .env

# 以下を編集：
# SECRET_KEY=ランダムな長い文字列に変更
# FLASK_ENV=production
# ADMIN_PASSWORD=安全なパスワードに変更
```

#### Step 4: ディレクトリとパーミッションを設定

```bash
# ログディレクトリを作成
mkdir -p /var/log/panzaiko
mkdir -p /var/run/panzaiko

# パーミッションを設定
chown -R www-data:www-data /var/www/panzaiko
chown -R www-data:www-data /var/log/panzaiko
chown -R www-data:www-data /var/run/panzaiko
```

#### Step 5: Systemdサービスを設定

```bash
# サービスファイルをコピー
cp /var/www/panzaiko/panzaiko.service /etc/systemd/system/

# サービスを有効化して起動
systemctl daemon-reload
systemctl enable panzaiko
systemctl start panzaiko

# ステータスを確認
systemctl status panzaiko
```

#### Step 6: Nginxを設定

```bash
# Nginx設定をコピー（ドメインを置換）
sed "s/yourdomain.com/your-actual-domain.com/g" \
    /var/www/panzaiko/nginx.conf > /etc/nginx/sites-available/panzaiko

# シンボリックリンクを作成
ln -sf /etc/nginx/sites-available/panzaiko /etc/nginx/sites-enabled/

# デフォルト設定を無効化
rm -f /etc/nginx/sites-enabled/default

# Nginx設定をテスト
nginx -t

# Nginxを再起動
systemctl restart nginx
```

#### Step 7: SSL証明書を取得

```bash
# Let's Encrypt証明書を取得
certbot --nginx -d yourdomain.com -d www.yourdomain.com

# 自動更新をテスト
certbot renew --dry-run
```

---

## トラブルシューティング

### ❌ サービスが起動しない

```bash
# ログを確認
journalctl -u panzaiko -n 50

# 手動で起動してエラーを確認
cd /var/www/panzaiko
source venv/bin/activate
cd app/backend
python app.py
```

**よくある原因：**
- Pythonパッケージが不足 → `pip install -r requirements.txt`
- パーミッション不足 → `chown -R www-data:www-data /var/www/panzaiko`
- ポートが使用中 → `lsof -i :8080` で確認

### ❌ Nginxエラー

```bash
# Nginx設定をテスト
nginx -t

# Nginxのログを確認
tail -f /var/log/nginx/panzaiko_error.log
```

### ❌ SSL証明書の問題

```bash
# DNS設定を確認
nslookup yourdomain.com

# ファイアウォールを確認
ufw status
ufw allow 80/tcp
ufw allow 443/tcp
```

### ❌ データベースエラー

```bash
# データベースファイルのパーミッションを確認
ls -la /var/www/panzaiko/*.db

# パーミッションを修正
chown www-data:www-data /var/www/panzaiko/breads_full.db
chmod 664 /var/www/panzaiko/breads_full.db
```

---

## メンテナンス

### サービス管理コマンド

```bash
# 起動
sudo systemctl start panzaiko

# 停止
sudo systemctl stop panzaiko

# 再起動
sudo systemctl restart panzaiko

# 状態確認
sudo systemctl status panzaiko

# ログをリアルタイム表示
sudo journalctl -u panzaiko -f
```

### アプリケーション更新

```bash
# サーバーにSSH接続
ssh root@your-server-ip

# アプリケーションディレクトリに移動
cd /var/www/panzaiko

# 最新コードを取得（Gitの場合）
git pull origin main

# または、rsyncで更新
# ローカルから: rsync -avz ...

# 仮想環境をアクティブ化
source venv/bin/activate

# 依存パッケージを更新
pip install -r app/backend/requirements.txt

# サービスを再起動
systemctl restart panzaiko
```

### データベースバックアップ

```bash
# 自動バックアップスクリプトを作成
cat > /root/backup_panzaiko.sh << 'BACKUP_SCRIPT'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/root/backups/panzaiko"
mkdir -p $BACKUP_DIR

# データベースをバックアップ
cp /var/www/panzaiko/breads_full.db $BACKUP_DIR/breads_full_$DATE.db

# 7日以上古いバックアップを削除
find $BACKUP_DIR -name "*.db" -mtime +7 -delete

echo "Backup completed: $DATE"
BACKUP_SCRIPT

chmod +x /root/backup_panzaiko.sh

# Cronで毎日実行
crontab -e
# 以下を追加：
# 0 2 * * * /root/backup_panzaiko.sh >> /var/log/panzaiko/backup.log 2>&1
```

### ログのローテーション

```bash
# logrotate設定を作成
cat > /etc/logrotate.d/panzaiko << 'LOGROTATE'
/var/log/panzaiko/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
    postrotate
        systemctl reload panzaiko > /dev/null 2>&1 || true
    endscript
}
LOGROTATE
```

### セキュリティアップデート

```bash
# システムを更新
apt-get update
apt-get upgrade -y

# SSL証明書を更新
certbot renew

# ファイアウォールを確認
ufw status
```

---

## 📊 監視とモニタリング

### アプリケーションの健全性チェック

```bash
# サービス状態
systemctl is-active panzaiko

# プロセス確認
ps aux | grep gunicorn

# ポート確認
netstat -tlnp | grep 8080
```

### パフォーマンス監視

```bash
# CPU・メモリ使用率
top
htop

# ディスク使用率
df -h

# ログのサイズ
du -sh /var/log/panzaiko/*
```

---

## 🔐 セキュリティベストプラクティス

1. **定期的なアップデート**
   - OS、Python、パッケージを定期的に更新

2. **ファイアウォール設定**
   ```bash
   ufw allow 22/tcp    # SSH
   ufw allow 80/tcp    # HTTP
   ufw allow 443/tcp   # HTTPS
   ufw enable
   ```

3. **SSH設定**
   - パスワード認証を無効化
   - SSH鍵認証を使用
   - ポート22を変更（オプション）

4. **環境変数の保護**
   - `.env`ファイルのパーミッションを制限
   ```bash
   chmod 600 /var/www/panzaiko/.env
   ```

5. **データベースバックアップ**
   - 毎日自動バックアップ
   - オフサイトに保存

---

## 📞 サポート

問題が発生した場合：

1. ログを確認: `journalctl -u panzaiko -f`
2. Nginxログを確認: `tail -f /var/log/nginx/panzaiko_error.log`
3. [IMPROVEMENTS.md](IMPROVEMENTS.md) を参照
4. Issueを作成

---

**最終更新**: 2025-10-28
**バージョン**: 2.0
