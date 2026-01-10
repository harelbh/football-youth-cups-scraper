"""
Railway Clock Worker - מריץ את הסקרייפר כל 5 דקות
ושומר ב-GitHub Pages
"""

import time
import schedule
from github_scraper import main as run_scraper
from datetime import datetime

print("🚀 Railway Clock Worker התחיל!")
print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*60)

def job():
    """הרץ את הסקרייפר"""
    print(f"\n🕐 {datetime.now().strftime('%H:%M:%S')} - מתחיל סריקה...")
    run_scraper()
    print(f"✅ סיום בדיקה")

# הרץ מיד בהתחלה
print("\n🔄 מריץ בדיקה ראשונית...")
job()

# תזמן לרוץ כל 5 דקות
schedule.every(5).minutes.do(job)

print(f"\n✅ המערכת פעילה - תבדוק כל 5 דקות")
print(f"📂 תוצאות יישמרו ב-GitHub")
print(f"⌨️  הלוגים יופיעו כאן...\n")

# רוץ לנצח
while True:
    schedule.run_pending()
    time.sleep(30)
  # בדוק כל 30 שניות
