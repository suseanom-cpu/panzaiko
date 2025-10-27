# AWS Elastic Beanstalk デプロイガイド

## 前提条件
- AWSアカウント
- AWS CLI インストール済み
- EB CLI インストール済み（`pip install awsebcli`）

## デプロイ手順

### 1. フロントエンドのビルド
```bash
cd app/frontend
npm install
npm run build
```
ビルドされたファイルは `app/frontend/dist/` に生成されます。

### 2. AWS CLI の設定
```bash
aws configure
```
以下の情報を入力：
- AWS Access Key ID
- AWS Secret Access Key
- Default region (例: ap-northeast-1)
- Default output format: json

### 3. EB CLI の初期化
プロジェクトルートで実行：
```bash
cd c:\Users\asd95\Downloads\在庫管理システム
eb init
```

対話形式で以下を選択：
1. リージョン: `ap-northeast-1` (東京)
2. アプリケーション名: `inventory-management-system`
3. プラットフォーム: `Python 3.11`
4. SSH キーペア: 必要に応じて設定

### 4. 環境の作成とデプロイ
```bash
eb create inventory-prod
```

または、詳細設定：
```bash
eb create inventory-prod \
  --instance-type t3.small \
  --envvars SECRET_KEY=your_secret_key_here
```

### 5. 環境変数の設定
```bash
eb setenv SECRET_KEY="your_secure_random_secret_key_change_this"
eb setenv FLASK_ENV=production
```

### 6. デプロイ
```bash
eb deploy
```

### 7. アプリケーションを開く
```bash
eb open
```

## データベース設定

### オプションA: SQLite（開発/小規模）
- デフォルトで動作
- インスタンス再起動時にデータが消える可能性あり
- EBS ボリュームをマウントして永続化が必要

### オプションB: RDS PostgreSQL（本番推奨）

1. RDS インスタンスを作成：
```bash
eb create --database
```

2. `app.py` を修正してPostgreSQLに接続：
```python
# requirements.txt に追加
# psycopg2-binary==2.9.9

# 環境変数からDB接続情報を取得
import os
DATABASE_URL = os.environ.get('RDS_DB_NAME')
```

## 監視とログ

### ログの確認
```bash
eb logs
```

### ヘルスチェック
```bash
eb health
```

### SSH接続
```bash
eb ssh
```

## カスタムドメインとSSL

### 1. Route 53 でドメイン設定
1. Route 53 でホストゾーン作成
2. Aレコードを EB環境のURLに設定

### 2. ACM で SSL証明書発行
1. AWS Certificate Manager でSSL証明書リクエスト
2. ドメイン検証（DNS or Email）

### 3. EB環境に証明書を適用
```bash
eb config
```
または、AWS コンソールで：
- Configuration → Load Balancer → Listener → Add HTTPS

## コスト見積もり

### 基本構成（月額）
- EC2 t3.small（1インスタンス）: 約3,000円
- EBS ストレージ（20GB）: 約300円
- データ転送: 約500円
- **合計: 約3,800円/月**

### RDS追加時
- RDS db.t3.micro: 約2,500円
- **合計: 約6,300円/月**

## トラブルシューティング

### デプロイが失敗する
```bash
eb logs --all
```
でエラーログを確認

### パッケージインストールエラー
- `requirements.txt` を確認
- Python バージョンを確認（3.11推奨）

### 静的ファイルが表示されない
- フロントエンドのビルドを確認
- `.ebignore` を確認

## 更新手順

1. コード修正
2. フロントエンドを再ビルド（必要な場合）
```bash
cd app/frontend
npm run build
```
3. デプロイ
```bash
eb deploy
```

## スケーリング設定

### 自動スケーリング有効化
```bash
eb scale 2  # インスタンス数を2に
```

または設定ファイルで：
`.ebextensions/03_scaling.config`
```yaml
option_settings:
  aws:autoscaling:asg:
    MinSize: 1
    MaxSize: 4
  aws:autoscaling:trigger:
    MeasureName: CPUUtilization
    Statistic: Average
    Unit: Percent
    UpperThreshold: 80
    LowerThreshold: 20
```

## セキュリティ

### 環境変数で機密情報を管理
```bash
eb setenv SECRET_KEY="xxx" \
  API_KEY="yyy" \
  PASSWORD_HASH_KEY="zzz"
```

### セキュリティグループ設定
- デフォルトでHTTP(80)とHTTPS(443)のみ開放
- 必要に応じてSSH(22)を特定IPのみに制限

## バックアップ

### スナップショット作成
```bash
eb snapshot
```

### 自動バックアップ設定
AWS Console → Elastic Beanstalk → Configuration → Managed Updates

## 環境の削除

```bash
eb terminate inventory-prod
```

**注意**: データベースも削除されます。必要に応じて事前にバックアップを取得してください。

## 参考リンク
- [AWS Elastic Beanstalk ドキュメント](https://docs.aws.amazon.com/elasticbeanstalk/)
- [EB CLI コマンドリファレンス](https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/eb-cli3.html)
- [Flask on Elastic Beanstalk](https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/create-deploy-python-flask.html)
