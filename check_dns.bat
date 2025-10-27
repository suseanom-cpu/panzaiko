@echo off
echo DNS状態確認スクリプト
echo ========================
echo.
echo 1. ネームサーバー確認:
nslookup -type=ns panzaiko.com
echo.
echo 2. Aレコード確認:
nslookup panzaiko.com
echo.
echo 3. WWWレコード確認:
nslookup www.panzaiko.com
echo.
echo ========================
echo 上記で "lennox.ns.cloudflare.com" と "lilith.ns.cloudflare.com" が
echo 表示されていれば成功です！
echo.
pause
