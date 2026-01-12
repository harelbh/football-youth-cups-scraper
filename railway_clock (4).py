"""
Railway Worker - מריץ 2 סקרייפרים במקביל:
1. Smart Live - 30 שניות כשיש משחקים / 5 דקות כשאין
2. Full Scraper - כל 10 דקות
"""

import time
import schedule
from render_scraper_api import main as run_full_scraper
from live_games_scraper import LiveGamesScraper
from live_leagues_scraper import LiveLeaguesScraper
from datetime import datetime
from threading import Thread
import os
import json

print("🚀 Railway Worker התחיל!")
print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*60)

# משתנה גלובלי - האם יש משחקים חיים
has_live_games = False
has_live_leagues = False
live_schedule_tag = 'live_scraper'
leagues_schedule_tag = 'leagues_scraper'

def live_scraper_job():
    """הרץ את סקרייפר המשחקים החיים"""
    global has_live_games
    
    # בדוק אם אנחנו בשעות שינה (00:00-08:00)
    current_hour = datetime.now().hour
    if 0 <= current_hour < 8:
        print(f"\n💤 {datetime.now().strftime('%H:%M:%S')} - שעות שינה (00:00-08:00), דילוג על סריקה")
        return
    
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

def full_scraper_job():
    """הרץ את הסקרייפר המלא - כל המשחקים"""
    
    # בדוק אם אנחנו בשעות שינה (00:00-08:00)
    current_hour = datetime.now().hour
    if 0 <= current_hour < 8:
        print(f"\n💤 {datetime.now().strftime('%H:%M:%S')} - שעות שינה (00:00-08:00), דילוג על סריקה מלאה")
        return
    
    print(f"\n📊 {datetime.now().strftime('%H:%M:%S')} - מתחיל סריקה מלאה...")
    
    try:
        run_full_scraper()
        print(f"✅ סיום סריקה מלאה")
    except Exception as e:
        print(f"❌ שגיאה בסקרייפר מלא: {e}")

def live_leagues_scraper_job():
    """הרץ את סקרייפר משחקי הליגה החיים"""
    global has_live_leagues
    
    # בדוק אם אנחנו בשעות שינה (00:00-08:00)
    current_hour = datetime.now().hour
    if 0 <= current_hour < 8:
        print(f"\n💤 {datetime.now().strftime('%H:%M:%S')} - שעות שינה (00:00-08:00), דילוג על סריקת ליגות")
        return
    
    print(f"\n⚽ {datetime.now().strftime('%H:%M:%S')} - בודק משחקי ליגה חיים...")
    
    try:
        # הרץ את הסקרייפר
        scraper = LiveLeaguesScraper()
        live_leagues = scraper.scrape_live_leagues()
        scraper.close()
        
        # שמור את התוצאות
        if live_leagues:
            has_live_leagues = True
            print(f"✅ נמצאו {len(live_leagues)} משחקי ליגה חיים!")
            
            # שמור ל-JSON
            with open('live_leagues.json', 'w', encoding='utf-8') as f:
                json.dump(live_leagues, f, ensure_ascii=False, indent=2)
            
            print(f"💾 live_leagues.json נשמר")
            
            # החלף ל-מצב מהיר (30 שניות)
            switch_leagues_to_fast_mode()
        else:
            has_live_leagues = False
            print(f"💤 אין משחקי ליגה חיים כרגע")
            
            # מחק את הקובץ (אין משחקים חיים)
            if os.path.exists('live_leagues.json'):
                os.remove('live_leagues.json')
            
            # החלף ל-מצב שינה (5 דקות)
            switch_leagues_to_sleep_mode()
        
    except Exception as e:
        print(f"❌ שגיאה בסקרייפר ליגות חיות: {e}")
        has_live_leagues = False
        switch_leagues_to_sleep_mode()

def switch_to_fast_mode():
    """החלף למצב מהיר - כל 30 שניות"""
    # מחק רק את המשימות של הלייב
    schedule.clear(live_schedule_tag)
    schedule.every(30).seconds.do(live_scraper_job).tag(live_schedule_tag)
    print(f"⚡ מצב מהיר: סריקת לייב כל 30 שניות")

def switch_to_sleep_mode():
    """החלף למצב שינה - כל 5 דקות"""
    # מחק רק את המשימות של הלייב
    schedule.clear(live_schedule_tag)
    schedule.every(5).minutes.do(live_scraper_job).tag(live_schedule_tag)
    print(f"😴 מצב שינה: בדיקת לייב כל 5 דקות")

def switch_leagues_to_fast_mode():
    """החלף למצב מהיר ליגות - כל 30 שניות"""
    schedule.clear(leagues_schedule_tag)
    schedule.every(30).seconds.do(live_leagues_scraper_job).tag(leagues_schedule_tag)
    print(f"⚡ מצב מהיר ליגות: סריקה כל 30 שניות")

def switch_leagues_to_sleep_mode():
    """החלף למצב שינה ליגות - כל 5 דקות"""
    schedule.clear(leagues_schedule_tag)
    schedule.every(5).minutes.do(live_leagues_scraper_job).tag(leagues_schedule_tag)
    print(f"😴 מצב שינה ליגות: בדיקה כל 5 דקות")

def run_api_server():
    """הרץ את Flask API"""
    try:
        from api_server import app
        port = int(os.environ.get('PORT', 8080))
        print(f"🌐 API Server מתחיל על port {port}...")
        app.run(host='0.0.0.0', port=port, threaded=True)
    except Exception as e:
        print(f"❌ שגיאה ב-API Server: {e}")

# הרץ את שני הסקרייפרים מיד בהתחלה - תמיד! (גם בשעות שינה)
print("\n🔄 מריץ בדיקה ראשונית...")
print("💡 סריקה ראשונית רצה תמיד, גם בשעות שינה")

# הרץ ישירות בלי לבדוק שעות שינה
print(f"\n📊 {datetime.now().strftime('%H:%M:%S')} - מתחיל סריקה מלאה ראשונית...")
try:
    run_full_scraper()
    print(f"✅ סיום סריקה מלאה")
except Exception as e:
    print(f"❌ שגיאה בסקרייפר מלא: {e}")

# משחקי גביע חיים
live_scraper_job()

# משחקי ליגה חיים  
live_leagues_scraper_job()

# תזמן סריקה מלאה כל 10 דקות
schedule.every(10).minutes.do(full_scraper_job)

# המצב של הלייב נקבע אוטומטית ב-live_scraper_job
print(f"\n✅ Railway Worker פעיל!")
print(f"   📊 סריקה מלאה - כל 10 דקות")
print(f"   🔴 משחקי גביע חיים - חכם (30 שניות / 5 דקות)")
print(f"   ⚽ משחקי ליגה חיים - חכם (30 שניות / 5 דקות)")
print(f"💾 תוצאות נשמרות מקומית")

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
