"""
Full Scraper Worker - סורק את כל המשחקים (נגמרו + עתידיים)
רץ כל 10 דקות - לא דחוף
"""

import time
import schedule
from render_scraper_api import main as run_full_scraper
from datetime import datetime

print("📊 Full Scraper Worker התחיל!")
print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*60)

def full_scraper_job():
    """הרץ את הסקרייפר המלא - כל המשחקים"""
    print(f"\n📊 {datetime.now().strftime('%H:%M:%S')} - מתחיל סריקה מלאה...")
    
    try:
        run_full_scraper()
        print(f"✅ סיום סריקה מלאה")
    except Exception as e:
        print(f"❌ שגיאה בסקרייפר מלא: {e}")

# הרץ מיד בהתחלה
print("\n🔄 מריץ סריקה ראשונית...")
full_scraper_job()

# תזמן לרוץ כל 10 דקות
schedule.every(10).minutes.do(full_scraper_job)

print(f"\n✅ Full Scraper פעיל!")
print(f"📊 סריקה מלאה כל 10 דקות")
print(f"💾 תוצאות נשמרות ב-matches.json")
print(f"⌨️  הלוגים יופיעו כאן...\n")

# רוץ לנצח
while True:
    schedule.run_pending()
    time.sleep(30)
