"""
Smart Live Scraper - סורק משחקים חיים בתדירות משתנה
- כל 30 שניות כשיש משחקים חיים
- כל 5 דקות כשאין משחקים חיים (מצב שינה)
"""

import time
import schedule
from live_games_scraper import main as run_live_scraper, LiveGamesScraper
from datetime import datetime
from threading import Thread
import os

print("🔴 Smart Live Scraper התחיל!")
print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*60)

# משתנה גלובלי - האם יש משחקים חיים
has_live_games = False

def live_scraper_job():
    """הרץ את סקרייפר המשחקים החיים"""
    global has_live_games
    
    print(f"\n🔴 {datetime.now().strftime('%H:%M:%S')} - בודק משחקים חיים...")
    
    try:
        # הרץ את הסקרייפר
        scraper = LiveGamesScraper()
        live_matches = scraper.scrape_live_games()
        scraper.close()
        
        # שמור את התוצאות
        if live_matches:
            has_live_games = True
            print(f"✅ נמצאו {len(live_matches)} משחקים חיים!")
            
            # שמור ל-JSON
            import json
            with open('live_matches.json', 'w', encoding='utf-8') as f:
                json.dump(live_matches, f, ensure_ascii=False, indent=2)
            
            print(f"💾 live_matches.json נשמר")
            
            # החלף ל-מצב מהיר (30 שניות)
            switch_to_fast_mode()
        else:
            has_live_games = False
            print(f"💤 אין משחקים חיים כרגע")
            
            # מחק את הקובץ (אין משחקים חיים)
            if os.path.exists('live_matches.json'):
                os.remove('live_matches.json')
            
            # החלף ל-מצב שינה (5 דקות)
            switch_to_sleep_mode()
        
    except Exception as e:
        print(f"❌ שגיאה בסקרייפר חיים: {e}")
        has_live_games = False
        switch_to_sleep_mode()

def switch_to_fast_mode():
    """החלף למצב מהיר - כל 30 שניות"""
    schedule.clear()
    schedule.every(30).seconds.do(live_scraper_job)
    print(f"⚡ מצב מהיר: סריקה כל 30 שניות")

def switch_to_sleep_mode():
    """החלף למצב שינה - כל 5 דקות"""
    schedule.clear()
    schedule.every(5).minutes.do(live_scraper_job)
    print(f"😴 מצב שינה: בדיקה כל 5 דקות")

def run_api_server():
    """הרץ את Flask API"""
    try:
        from api_server import app
        port = int(os.environ.get('PORT', 8080))
        print(f"🌐 API Server מתחיל על port {port}...")
        app.run(host='0.0.0.0', port=port, threaded=True)
    except Exception as e:
        print(f"❌ שגיאה ב-API Server: {e}")

# הרץ בדיקה ראשונית
print("\n🔄 מריץ בדיקה ראשונית...")
live_scraper_job()

# התחל במצב שינה (אם אין משחקים, זה כבר עבר לשינה)
# אם יש משחקים, זה כבר עבר למצב מהיר
print(f"\n✅ Smart Live Scraper פעיל!")
print(f"💾 תוצאות נשמרות ב-live_matches.json")

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
