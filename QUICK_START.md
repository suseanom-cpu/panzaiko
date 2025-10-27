# クイックスタートガイド - AWS デプロイ

## 最短5ステップでデプロイ

### ステップ1: 前提条件のインストール
```bash
# AWS CLI インストール（Windowsの場合）
# https://aws.amazon.com/cli/ からダウンロード

# EB CLI インストール
pip install awsebcli

# AWS 認証情報を設定
aws configure
```

### ステップ2: フロントエンドのビルド
```bash
cd app/frontend
npm install
npm run build
cd ../..
```

### ステップ3: EB CLI 初期化
```bash
eb init -p python-3.11 -r ap-northeast-1 inventory-management
```

### ステップ4: 環境作成とデプロイ
```bash
eb create inventory-prod --instance-type t3.small
```

### ステップ5: アプリケーションを開く
```bash
eb open
```

## 重要な注意事項

### ⚠️ セキュリティ
デプロイ前に必ず SECRET_KEY を変更してください：
```bash
eb setenv SECRET_KEY="ランダムな長い文字列に変更してください"
```

### 💾 データベース
- 現在はSQLiteを使用（開発用）
- 本番環境ではRDS PostgreSQLの使用を推奨
- データの永続化が必要な場合は AWS_DEPLOYMENT_GUIDE.md を参照

### 💰 コスト
- 基本構成: 約3,800円/月
- 無料枠を使用する場合は t3.micro を選択：
```bash
eb create inventory-prod --instance-type t3.micro
```

## トラブルシューティング

### デプロイが失敗した場合
```bash
eb logs
```
でエラーログを確認

### 環境を削除したい場合
```bash
eb terminate inventory-prod
```

## 詳細情報
より詳しい情報は [AWS_DEPLOYMENT_GUIDE.md](./AWS_DEPLOYMENT_GUIDE.md) を参照してください。
