"""
WSGI エントリーポイント
AWS Elastic Beanstalk や Gunicorn で使用
"""
from app import app as application

if __name__ == "__main__":
    application.run()
