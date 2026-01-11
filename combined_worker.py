"""
Railway Combined Worker - מריץ סקרייפר + API
"""

import time
import schedule
from render_scraper import main as run_scraper
from datetime import datetime
from threading import Thread
import os

print("🚀 Railway Combined Worker התחיל!")
print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*60)

def scraper_job():
    """הרץ את הסקרייפר"""
    print(f"\n🕐 {datetime.now().strftime('%H:%M:%S')} - מתחיל סריקה...")
    try:
        run_scraper()
        print(f"✅ סיום בדיקה")
    except Exception as e:
        print(f"❌ שגיאה: {e}")

def run_api_server():
    """הרץ את Flask API"""
    from api_server import app
    port = int(os.environ.get('PORT', 8080))
    print(f"🌐 API Server מתחיל על port {port}...")
    app.run(host='0.0.0.0', port=port, threaded=True)

# הרץ את הסקרייפר מיד בהתחלה
print("\n🔄 מריץ בדיקה ראשונית...")
scraper_job()

# תזמן לרוץ כל 30 שניות
schedule.every(30).seconds.do(scraper_job)

print(f"\n✅ Scraper פעיל - תבדוק כל 30 שניות! ⚡")
print(f"📂 תוצאות נשמרות מקומית (matches.json)")

# הפעל את ה-API ב-thread נפרד
api_thread = Thread(target=run_api_server, daemon=True)
api_thread.start()

print(f"🌐 API Server פעיל!")
print(f"⌨️  הלוגים יופיעו כאן...\n")

# רוץ לנצח
while True:
    schedule.run_pending()
    time.sleep(5)
