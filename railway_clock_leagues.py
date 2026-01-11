"""
Railway Clock Worker - מריץ את סקרייפר הליגות כל 5 דקות
"""

import time
import schedule
from leagues_scraper import main as run_scraper
from datetime import datetime

print("🚀 Railway Clock Worker - Leagues התחיל!")
print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*60)

def job():
    """הרץ את סקרייפר הליגות"""
    print(f"\n🕐 {datetime.now().strftime('%H:%M:%S')} - מתחיל סריקת ליגות...")
    run_scraper()
    print(f"✅ סיום בדיקה")

# הרץ מיד בהתחלה
print("\n🔄 מריץ בדיקה ראשונית...")
job()

# תזמן לרוץ כל 5 דקות
schedule.every(5).minutes.do(job)

print(f"\n✅ המערכת פעילה - תבדוק ליגות כל 5 דקות")
print(f"📂 תוצאות יישמרו ב-GitHub (leagues_matches.json)")
print(f"⌨️  הלוגים יופיעו כאן...\n")

# רוץ לנצח
while True:
    schedule.run_pending()
    time.sleep(30)
