"""
Gunicorn設定ファイル（本番環境用）
"""
import multiprocessing
import os

# サーバーバインド
bind = f"0.0.0.0:{os.environ.get('PORT', '8080')}"

# ワーカー設定
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'sync'
worker_connections = 1000
timeout = 120
keepalive = 5

# ログ設定
accesslog = '/var/log/panzaiko/access.log'
errorlog = '/var/log/panzaiko/error.log'
loglevel = 'info'

# プロセス名
proc_name = 'panzaiko'

# デーモン化（systemdで管理する場合はFalse）
daemon = False

# pidファイル
pidfile = '/var/run/panzaiko/panzaiko.pid'

# セキュリティ
limit_request_line = 4096
limit_request_fields = 100
limit_request_field_size = 8190
