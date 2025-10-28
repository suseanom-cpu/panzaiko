#!/bin/bash

# デプロイスクリプト
# サーバーへのアップロードと設定を自動化

set -e  # エラーが発生したら停止

echo "=========================================="
echo "パン在庫管理システム - デプロイスクリプト"
echo "=========================================="

# カラー出力
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 設定
SERVER_USER="${SERVER_USER:-root}"
SERVER_HOST="${SERVER_HOST:-your-server-ip}"
DEPLOY_PATH="/var/www/panzaiko"
DOMAIN="${DOMAIN:-yourdomain.com}"

echo ""
echo -e "${YELLOW}設定確認:${NC}"
echo "  サーバーユーザー: $SERVER_USER"
echo "  サーバーホスト: $SERVER_HOST"
echo "  デプロイパス: $DEPLOY_PATH"
echo "  ドメイン: $DOMAIN"
echo ""

# 確認
read -p "この設定でデプロイを続行しますか？ (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "デプロイをキャンセルしました"
    exit 1
fi

echo ""
echo -e "${GREEN}Step 1: アプリケーションファイルをアップロード${NC}"
echo "----------------------------------------"

# 必要なディレクトリを作成
ssh $SERVER_USER@$SERVER_HOST "mkdir -p $DEPLOY_PATH"

# ファイルをアップロード（.gitignoreで除外されるものを除く）
rsync -avz --exclude-from='.gitignore' \
    --exclude='.git' \
    --exclude='venv' \
    --exclude='*.db' \
    --exclude='certs' \
    --exclude='*.csv' \
    ./ $SERVER_USER@$SERVER_HOST:$DEPLOY_PATH/

echo -e "${GREEN}✓ ファイルのアップロードが完了しました${NC}"

echo ""
echo -e "${GREEN}Step 2: サーバー上でセットアップ${NC}"
echo "----------------------------------------"

ssh $SERVER_USER@$SERVER_HOST << ENDSSH
set -e

cd $DEPLOY_PATH

echo "必要なパッケージをインストール..."
apt-get update
apt-get install -y python3 python3-pip python3-venv nginx certbot python3-certbot-nginx

echo "Python仮想環境を作成..."
python3 -m venv venv
source venv/bin/activate

echo "Pythonパッケージをインストール..."
pip install --upgrade pip
pip install -r app/backend/requirements.txt

echo "ディレクトリとログファイルを作成..."
mkdir -p /var/log/panzaiko
mkdir -p /var/run/panzaiko
chown -R www-data:www-data /var/log/panzaiko
chown -R www-data:www-data /var/run/panzaiko
chown -R www-data:www-data $DEPLOY_PATH

echo "✓ セットアップが完了しました"
ENDSSH

echo -e "${GREEN}✓ サーバー上のセットアップが完了しました${NC}"

echo ""
echo -e "${GREEN}Step 3: Systemdサービスを設定${NC}"
echo "----------------------------------------"

ssh $SERVER_USER@$SERVER_HOST << ENDSSH
set -e

# systemdサービスファイルをコピー
cp $DEPLOY_PATH/panzaiko.service /etc/systemd/system/

# サービスを有効化
systemctl daemon-reload
systemctl enable panzaiko

echo "✓ Systemdサービスを設定しました"
ENDSSH

echo -e "${GREEN}✓ Systemdサービスの設定が完了しました${NC}"

echo ""
echo -e "${GREEN}Step 4: Nginxを設定${NC}"
echo "----------------------------------------"

ssh $SERVER_USER@$SERVER_HOST << ENDSSH
set -e

# Nginx設定をコピー（ドメインを置換）
sed "s/yourdomain.com/$DOMAIN/g" $DEPLOY_PATH/nginx.conf > /etc/nginx/sites-available/panzaiko

# シンボリックリンクを作成
ln -sf /etc/nginx/sites-available/panzaiko /etc/nginx/sites-enabled/

# デフォルト設定を無効化
rm -f /etc/nginx/sites-enabled/default

# Nginx設定をテスト
nginx -t

echo "✓ Nginx設定を完了しました"
ENDSSH

echo -e "${GREEN}✓ Nginxの設定が完了しました${NC}"

echo ""
echo -e "${GREEN}Step 5: Let's Encrypt証明書を取得${NC}"
echo "----------------------------------------"

echo -e "${YELLOW}注意: DNS設定で $DOMAIN がこのサーバーを指していることを確認してください${NC}"
read -p "Let's Encrypt証明書を取得しますか？ (y/N): " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    ssh $SERVER_USER@$SERVER_HOST << ENDSSH
set -e

# Let's Encrypt証明書を取得
certbot --nginx -d $DOMAIN -d www.$DOMAIN --non-interactive --agree-tos --email admin@$DOMAIN

# 自動更新をテスト
certbot renew --dry-run

echo "✓ SSL証明書を取得しました"
ENDSSH
    echo -e "${GREEN}✓ SSL証明書の取得が完了しました${NC}"
else
    echo -e "${YELLOW}⚠ SSL証明書の取得をスキップしました（後で手動で実行してください）${NC}"
fi

echo ""
echo -e "${GREEN}Step 6: サービスを起動${NC}"
echo "----------------------------------------"

ssh $SERVER_USER@$SERVER_HOST << ENDSSH
set -e

# Nginxを再起動
systemctl restart nginx

# アプリケーションを起動
systemctl restart panzaiko

# ステータスを確認
systemctl status panzaiko --no-pager

echo "✓ サービスを起動しました"
ENDSSH

echo -e "${GREEN}✓ サービスの起動が完了しました${NC}"

echo ""
echo "=========================================="
echo -e "${GREEN}デプロイが完了しました！${NC}"
echo "=========================================="
echo ""
echo "アクセスURL:"
echo "  HTTP:  http://$DOMAIN"
echo "  HTTPS: https://$DOMAIN"
echo ""
echo "サービス管理コマンド:"
echo "  起動: sudo systemctl start panzaiko"
echo "  停止: sudo systemctl stop panzaiko"
echo "  再起動: sudo systemctl restart panzaiko"
echo "  状態確認: sudo systemctl status panzaiko"
echo "  ログ確認: sudo journalctl -u panzaiko -f"
echo ""
echo "次のステップ:"
echo "  1. ブラウザで https://$DOMAIN にアクセス"
echo "  2. 初期データを入力"
echo "  3. バックアップの設定"
echo ""
