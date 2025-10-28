# AWS Elastic Beanstalkデプロイ完了ガイド

## 🎉 デプロイ状況

現在、AWS Elastic Beanstalk環境を作成中です。

### 作成された設定ファイル

✅ **application.py** - Elastic Beanstalkエントリーポイント
✅ **requirements.txt** - Python依存パッケージ
✅ **.ebextensions/01_flask.config** - Flask設定
✅ **AWS認証情報** - 設定完了

### デプロイコマンド実行中

```bash
eb create panzaiko-env --single --instance-type t3.micro
```

## 📋 完了後の手順

### 1. 環境の状態を確認

```bash
cd /Users/seanm/Downloads/untitled\ folder\ 13/panzaiko
eb status
```

### 2. URLを取得

```bash
eb open
```

または

```bash
eb status | grep CNAME
```

### 3. ログを確認

```bash
eb logs
```

### 4. アプリケーション更新（今後）

```bash
# コードを変更後
eb deploy
```

## 🔧 トラブルシューティング

### 環境の再作成が必要な場合

```bash
# 環境を削除
eb terminate panzaiko-env

# 再作成
eb create panzaiko-env --single --instance-type t3.micro
```

### ログでエラーを確認

```bash
eb logs --all
```

### SSHで直接接続（デバッグ用）

```bash
eb ssh
```

## 📊 使用しているAWSリソース

- **リージョン**: ap-northeast-1 (東京)
- **プラットフォーム**: Python 3.11
- **インスタンスタイプ**: t3.micro (無料枠)
- **環境タイプ**: Single instance

## 💰 コスト

- **t3.micro**: 無料枠対象（月750時間まで無料）
- **その他**: ロードバランサーなし（シングルインスタンス）

## 🔐 セキュリティ

### 環境変数の設定（本番用）

```bash
eb setenv SECRET_KEY=your-secret-key-here \
          FLASK_ENV=production \
          ADMIN_PASSWORD=secure-password
```

### HTTPS化（オプション）

1. Route 53でドメインを設定
2. Certificate Managerで証明書を取得
3. ロードバランサーを設定

```bash
eb create panzaiko-env --instance-type t3.micro \
    --elb-type application \
    --enable-spot
```

## 📝 管理コマンド一覧

### 状態確認
```bash
eb status          # 環境状態
eb health          # ヘルスチェック
eb logs            # ログ表示
```

### デプロイ
```bash
eb deploy          # アプリケーション更新
eb deploy --staged # Gitにコミット前のファイルをデプロイ
```

### 設定変更
```bash
eb config          # 設定をエディタで編集
eb setenv KEY=VALUE # 環境変数を設定
eb scale 2         # インスタンス数を変更
```

### その他
```bash
eb open            # ブラウザで開く
eb ssh             # SSH接続
eb terminate       # 環境を削除
```

## 🎯 次のステップ

1. **環境作成の完了を待つ** (5-10分)
2. **URLにアクセスして動作確認**
3. **ログインしてダッシュボードをテスト**
4. **データを入力して予測をテスト**

## 📞 サポート

問題が発生した場合：

1. `eb logs` でエラーを確認
2. `eb status` で環境状態を確認
3. AWS Consoleでより詳細な情報を確認

---

**デプロイ日時**: 2025-10-28
**AWS リージョン**: ap-northeast-1 (東京)
