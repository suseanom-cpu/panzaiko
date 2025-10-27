import requests
from datetime import date, timedelta
from flask import current_app

# ============================================
# API設定
# ============================================
OPENWEATHER_API_KEY = "048704ba0917b05a66dd010b71e9a7e1"
OPENWEATHER_API_URL = "http://api.openweathermap.org/data/2.5/weather"

# 神戸市中央区の座標
KOBE_LAT = 34.6913
KOBE_LON = 135.1830

# ============================================
# 天気情報取得
# ============================================
def get_kobe_weather():
    """神戸市中央区の天気情報を取得"""
    try:
        params = {
            "lat": KOBE_LAT,
            "lon": KOBE_LON,
            "appid": OPENWEATHER_API_KEY,
            "lang": "ja",
            "units": "metric"
        }
        response = requests.get(OPENWEATHER_API_URL, params=params, timeout=5)

        if response.status_code == 200:
            data = response.json()
            return {
                "temp": round(data["main"]["temp"], 1),
                "feels_like": round(data["main"]["feels_like"], 1),
                "humidity": data["main"]["humidity"],
                "description": data["weather"][0]["description"],
                "icon": data["weather"][0]["icon"],
                "main": data["weather"][0]["main"],
                "city": "神戸市中央区"
            }
    except Exception as e:
        if current_app:
            current_app.logger.error(f"Weather API error: {e}")
    return None

# ============================================
# 中国祝日・イベント情報
# ============================================
def get_china_holidays_and_events():
    """中国の祝日と日本の飲食業に影響するイベントを取得"""
    today = date.today()
    events = []

    # 中国の主要祝日（2025年版）
    china_holidays = {
        (1, 1): {"name": "元旦", "impact": "high", "detail": "新年の祝日。訪日中国人観光客が増加する時期です。"},
        (1, 28): {"name": "春節前日", "impact": "very_high", "detail": "春節連休開始。大量の中国人観光客が来日します。"},
        (1, 29): {"name": "春節（旧正月）", "impact": "very_high", "detail": "中国最大の祝日。インバウンド需要が最も高まります。"},
        (1, 30): {"name": "春節連休", "impact": "very_high", "detail": "春節連休中。観光客で賑わいます。"},
        (1, 31): {"name": "春節連休", "impact": "very_high", "detail": "春節連休中。観光客で賑わいます。"},
        (2, 1): {"name": "春節連休", "impact": "very_high", "detail": "春節連休中。観光客で賑わいます。"},
        (2, 2): {"name": "春節連休", "impact": "very_high", "detail": "春節連休中。観光客で賑わいます。"},
        (2, 3): {"name": "春節連休", "impact": "very_high", "detail": "春節連休中。観光客で賑わいます。"},
        (2, 4): {"name": "春節連休最終日", "impact": "high", "detail": "春節連休最終日。帰国前の買い物需要が高まります。"},
        (4, 5): {"name": "清明節", "impact": "medium", "detail": "先祖を祀る日。一部観光客の来日があります。"},
        (5, 1): {"name": "労働節（メーデー）", "impact": "high", "detail": "ゴールデンウィーク。訪日観光客が増加します。"},
        (5, 2): {"name": "労働節連休", "impact": "high", "detail": "メーデー連休中。"},
        (5, 3): {"name": "労働節連休", "impact": "high", "detail": "メーデー連休中。"},
        (6, 10): {"name": "端午節", "impact": "medium", "detail": "伝統的な祝日。一部観光客の来日があります。"},
        (10, 1): {"name": "国慶節", "impact": "very_high", "detail": "建国記念日。大型連休で大量の観光客が来日します。"},
        (10, 2): {"name": "国慶節連休", "impact": "very_high", "detail": "国慶節連休中。"},
        (10, 3): {"name": "国慶節連休", "impact": "very_high", "detail": "国慶節連休中。"},
        (10, 4): {"name": "国慶節連休", "impact": "very_high", "detail": "国慶節連休中。"},
        (10, 5): {"name": "国慶節連休", "impact": "very_high", "detail": "国慶節連休中。"},
        (10, 6): {"name": "国慶節連休", "impact": "very_high", "detail": "国慶節連休中。"},
        (10, 7): {"name": "国慶節連休最終日", "impact": "high", "detail": "国慶節連休最終日。"},
    }

    # 今日から7日間のイベントをチェック
    for i in range(7):
        check_date = today + timedelta(days=i)
        key = (check_date.month, check_date.day)

        if key in china_holidays:
            event = china_holidays[key].copy()
            event["date"] = check_date.isoformat()
            event["days_until"] = i
            events.append(event)

    return events

def is_china_holiday(d: date):
    """指定日が中国の祝日かどうかをチェック"""
    events = get_china_holidays_and_events()
    for event in events:
        if event["date"] == d.isoformat():
            return True
    return False

def get_impact_multiplier(d: date):
    """指定日のインバウンド影響係数を返す"""
    events = get_china_holidays_and_events()
    for event in events:
        if event["date"] == d.isoformat():
            impact = event.get("impact", "low")
            if impact == "very_high":
                return 1.5
            elif impact == "high":
                return 1.3
            elif impact == "medium":
                return 1.15
    return 1.0
