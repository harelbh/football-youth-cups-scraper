"""
Railway Clock Worker - מריץ 2 סקרייפרים:
1. render_scraper - כל המשחקים (כל 5 דקות)
2. live_games_scraper - רק חיים (כל 30 שניות)
"""

import time
import schedule
from render_scraper_api import main as run_full_scraper
from live_games_scraper import main as run_live_scraper
from datetime import datetime
from threading import Thread
import os

print("🚀 Railway Combined Worker התחיל!")
print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*60)

def full_scraper_job():
    """הרץ את הסקרייפר המלא - כל המשחקים"""
    print(f"\n🕐 {datetime.now().strftime('%H:%M:%S')} - מתחיל סריקה מלאה...")
    try:
        run_full_scraper()
        print(f"✅ סיום סריקה מלאה")
    except Exception as e:
        print(f"❌ שגיאה בסקרייפר מלא: {e}")

def live_scraper_job():
    """הרץ את סקרייפר המשחקים החיים"""
    print(f"\n🔴 {datetime.now().strftime('%H:%M:%S')} - מתחיל סריקת משחקים חיים...")
    try:
        run_live_scraper()
        print(f"✅ סיום סריקת חיים")
    except Exception as e:
        print(f"❌ שגיאה בסקרייפר חיים: {e}")

def run_api_server():
    """הרץ את Flask API"""
    try:
        from api_server import app
        port = int(os.environ.get('PORT', 8080))
        print(f"🌐 API Server מתחיל על port {port}...")
        app.run(host='0.0.0.0', port=port, threaded=True)
    except Exception as e:
        print(f"❌ שגיאה ב-API Server: {e}")

# הרץ את שני הסקרייפרים מיד בהתחלה
print("\n🔄 מריץ בדיקה ראשונית...")
full_scraper_job()  # כל המשחקים
live_scraper_job()  # משחקים חיים

# תזמן סריקה מלאה כל 5 דקות
schedule.every(5).minutes.do(full_scraper_job)

# תזמן סריקת חיים כל 30 שניות
schedule.every(30).seconds.do(live_scraper_job)

print(f"\n✅ Scrapers פעילים:")
print(f"   📊 סריקה מלאה - כל 5 דקות")
print(f"   🔴 משחקים חיים - כל 30 שניות! ⚡")
print(f"💾 תוצאות נשמרות מקומית (matches.json + live_matches.json)")

# הפעל את ה-API ב-thread נפרד
print(f"🌐 מפעיל API Server...")
api_thread = Thread(target=run_api_server, daemon=True)
api_thread.start()

print(f"✅ API Server פעיל!")
print(f"⌨️  הלוגים יופיעו כאן...\n")

# רוץ לנצח
while True:
    schedule.run_pending()
    time.sleep(5)
