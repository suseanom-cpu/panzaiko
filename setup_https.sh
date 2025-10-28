#!/bin/bash

# HTTPS設定スクリプト（自己署名証明書を使用）

echo "=========================================="
echo "HTTPS設定（自己署名証明書）"
echo "=========================================="

# 証明書ディレクトリを作成
CERT_DIR="./certs"
mkdir -p "$CERT_DIR"

# 自己署名証明書を生成
echo ""
echo "自己署名証明書を生成中..."
openssl req -x509 -newkey rsa:4096 -nodes \
  -out "$CERT_DIR/cert.pem" \
  -keyout "$CERT_DIR/key.pem" \
  -days 365 \
  -subj "/C=JP/ST=Hyogo/L=Kobe/O=PanZaiko/CN=localhost"

if [ $? -eq 0 ]; then
    echo "✓ 証明書を生成しました"
    echo "  - 証明書: $CERT_DIR/cert.pem"
    echo "  - 秘密鍵: $CERT_DIR/key.pem"
    echo ""
    echo "⚠️ 注意事項:"
    echo "  - これは開発用の自己署名証明書です"
    echo "  - ブラウザで「安全でない」という警告が表示されますが、続行できます"
    echo "  - 本番環境では Let's Encrypt などの正式な証明書を使用してください"
    echo ""
    echo "✓ HTTPS設定が完了しました"
    echo ""
    echo "サーバーを起動するには:"
    echo "  python app_https.py"
else
    echo "❌ 証明書の生成に失敗しました"
    exit 1
fi
