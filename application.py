"""
AWS Elastic Beanstalk用のエントリーポイント
Elastic BeanstalkはWSGIアプリケーションとして'application'変数を探します
"""
import sys
import os

# アプリケーションディレクトリをパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app', 'backend'))

from app import app as application

# Elastic Beanstalkの環境変数をデバッグ
if __name__ == "__main__":
    application.run(debug=False)
