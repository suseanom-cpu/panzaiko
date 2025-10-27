# Cloudflare設定ガイド - panzaiko.com

## 現在の設定情報

- **サーバーIPアドレス**: 13.112.246.93
- **Elastic Beanstalk URL**: inventory-prod.eba-rruev3pm.ap-northeast-1.elasticbeanstalk.com
- **ドメイン**: panzaiko.com, www.panzaiko.com

---

## セットアップ手順

### 1. Cloudflareアカウント作成・サイト追加

1. https://dash.cloudflare.com/ にアクセス
2. アカウント作成（無料）またはログイン
3. 「サイトを追加」をクリック
4. ドメイン名: `panzaiko.com` を入力
5. プラン選択: **Free ($0)** を選択

### 2. DNS設定

以下のDNSレコードを設定：

| タイプ | 名前 | 内容/ターゲット | プロキシ状態 | TTL |
|--------|------|----------------|--------------|-----|
| A | @ | 13.112.246.93 | プロキシ済み（🟠） | Auto |
| A | www | 13.112.246.93 | プロキシ済み（🟠） | Auto |

**重要**:
- プロキシ状態は必ず「プロキシ済み」（オレンジ色の雲）にする
- これでHTTPS、CDN、DDoS保護が自動的に有効になります

### 3. ネームサーバー変更

Cloudflareが表示するネームサーバー（例）:
```
carter.ns.cloudflare.com
roxy.ns.cloudflare.com
```

**ドメインレジストラでの設定：**
1. panzaiko.comを購入したサイト（お名前.com、GoDaddy等）にログイン
2. ドメイン管理画面を開く
3. ネームサーバー設定を変更
4. Cloudflareから提供された2つのネームサーバーを入力
5. 保存

**よくあるレジストラの設定場所：**
- **お名前.com**: ドメイン設定 > ネームサーバーの設定
- **GoDaddy**: DNS > ネームサーバー
- **Google Domains**: DNS > ネームサーバー > カスタムネームサーバー

### 4. SSL/TLS設定（HTTPS有効化）

Cloudflareダッシュボード:

1. **SSL/TLS** タブを開く
2. **暗号化モード**: 「Flexible」を選択
   ```
   ユーザー → Cloudflare: HTTPS (暗号化)
   Cloudflare → サーバー: HTTP (非暗号化)
   ```

3. **Edge Certificates** に移動
4. 以下を有効化:
   - ✅ **Always Use HTTPS** - HTTPを自動的にHTTPSにリダイレクト
   - ✅ **Automatic HTTPS Rewrites** - HTTP リンクを自動的にHTTPSに書き換え
   - ✅ **Opportunistic Encryption** - より安全な接続を試行

### 5. パフォーマンス最適化（推奨）

#### Speed > Optimization:
- ✅ **Auto Minify**: JavaScript, CSS, HTML すべてチェック
- ✅ **Brotli**: 有効化（圧縮率向上）
- ✅ **Rocket Loader**: 有効化（JavaScript読み込み高速化）

#### Caching > Configuration:
- **Browser Cache TTL**: 4 hours（推奨）
- **Caching Level**: Standard

#### Network:
- ✅ **HTTP/3 (with QUIC)**: 有効化
- ✅ **0-RTT Connection Resumption**: 有効化
- ✅ **WebSockets**: 有効化（アプリがWebSocketを使う場合）

### 6. セキュリティ設定（推奨）

#### Security > Settings:
- **Security Level**: Medium
- ✅ **Bot Fight Mode**: 有効化（無料のボット対策）
- ✅ **Challenge Passage**: 30分

---

## 設定確認

### DNSの伝播確認

ネームサーバー変更後、10-30分で反映されます。

**確認コマンド（Windows）:**
```bash
nslookup panzaiko.com
```

正しく設定されていれば、Cloudflareのネームサーバーが返されます。

**確認コマンド（オンライン）:**
- https://www.whatsmydns.net/#A/panzaiko.com

### HTTPS動作確認

ブラウザで以下にアクセス:
- https://panzaiko.com （自動的にHTTPSにリダイレクトされる）
- https://www.panzaiko.com

**確認ポイント:**
- ✅ URLバーに🔒（鍵マーク）が表示される
- ✅ "接続は保護されています" と表示される
- ✅ HTTP → HTTPS に自動リダイレクトされる

---

## トラブルシューティング

### 問題1: "DNS_PROBE_FINISHED_NXDOMAIN" エラー

**原因**: DNSがまだ伝播していない

**解決策**:
- 15-30分待つ
- ドメインレジストラでネームサーバーが正しく設定されているか確認

### 問題2: "ERR_TOO_MANY_REDIRECTS" エラー

**原因**: SSL/TLS設定が間違っている

**解決策**:
- Cloudflare SSL/TLS設定を「Flexible」に変更

### 問題3: "502 Bad Gateway" エラー

**原因**: サーバーが停止している

**解決策**:
```bash
cd "c:\Users\asd95\Downloads\在庫管理システム"
eb status
```
Health が "Green" であることを確認

### 問題4: HTTPSで "証明書が無効" エラー

**原因**: Cloudflareプロキシが無効

**解決策**:
- DNS設定でオレンジ色の雲（プロキシ済み）になっているか確認

---

## 完了チェックリスト

- [ ] Cloudflareアカウント作成完了
- [ ] panzaiko.com をCloudflareに追加
- [ ] DNSレコード（A @ と A www）を設定（プロキシ済み）
- [ ] ドメインレジストラでネームサーバーをCloudflareに変更
- [ ] SSL/TLS を「Flexible」に設定
- [ ] "Always Use HTTPS" を有効化
- [ ] https://panzaiko.com にアクセスして動作確認

---

## 費用

- **Cloudflare Free プラン**: $0/月
- **AWS Elastic Beanstalk**: 約3,800円/月（変わらず）

**合計**: 約3,800円/月

---

## メンテナンス

### 証明書の更新
- **不要** - Cloudflareが自動的に管理

### サーバーIPアドレスが変わった場合
1. Cloudflare Dashboard > DNS
2. Aレコードの内容を新しいIPアドレスに変更

---

## サポート

Cloudflare設定でわからないことがあれば:
- Cloudflareドキュメント: https://developers.cloudflare.com/
- Cloudflareコミュニティ: https://community.cloudflare.com/

---

## 次のステップ（オプション）

### カスタムエラーページ
Cloudflare > Customize > Error Pages

### アクセス解析
Cloudflare > Analytics（基本的なアクセス統計が見られます）

### Page Rules（無料プランで3つまで）
特定のURLに対してキャッシュやリダイレクトルールを設定可能
