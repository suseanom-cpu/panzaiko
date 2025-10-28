"""
アプリケーション設定ファイル
"""
import os
from pathlib import Path

class Config:
    """基本設定"""
    # アプリケーションルート
    BASE_DIR = Path(__file__).parent.parent.parent
    
    # Flask設定
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # データベース
    DB_PATH = os.environ.get('DB_PATH', str(BASE_DIR / 'breads_full.db'))
    
    # サーバー設定
    HOST = os.environ.get('HOST', '0.0.0.0')
    PORT = int(os.environ.get('PORT', 8080))
    HTTPS_PORT = int(os.environ.get('HTTPS_PORT', 8443))
    
    # SSL証明書
    SSL_CERT_PATH = os.environ.get('SSL_CERT_PATH', str(BASE_DIR / 'certs' / 'cert.pem'))
    SSL_KEY_PATH = os.environ.get('SSL_KEY_PATH', str(BASE_DIR / 'certs' / 'key.pem'))
    
    # デバッグモード
    DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'
    
    # ログ設定
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE', str(BASE_DIR / 'app.log'))

class DevelopmentConfig(Config):
    """開発環境設定"""
    DEBUG = True
    PORT = 8080

class ProductionConfig(Config):
    """本番環境設定"""
    DEBUG = False
    PORT = 8080
    # 本番環境では環境変数から読み込む
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY環境変数が設定されていません")

# 環境に応じた設定を選択
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

def get_config():
    """現在の環境に応じた設定を取得"""
    env = os.environ.get('FLASK_ENV', 'development')
    return config.get(env, config['default'])
