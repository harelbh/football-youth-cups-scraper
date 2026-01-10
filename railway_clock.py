"""
Railway Clock Worker - מריץ את הסקרייפר כל 5 דקות
"""

import os
import time
import schedule
from render_scraper import YouthCupsScraper, upload_to_server, should_update
from datetime import datetime

print("🚀 Railway Clock Worker התחיל!")
print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*60)

def run_scraper():
    """הרץ את הסקרייפר"""
    print(f"\n🕐 {datetime.now().strftime('%H:%M:%S')} - מתחיל סריקה...")
    
    scraper = YouthCupsScraper()
    
    try:
        matches = scraper.scrape_all_cups()
        
        if not matches:
            print("❌ לא נמצאו משחקים")
            return
        
        # בדוק אם צריך לעדכן
        if should_update(matches):
            print(f"\n⚡ יש משחקים פעילים - מעדכן!")
            upload_to_server(matches)
        else:
            print(f"\n💤 אין משחקים פעילים - לא מעדכן")
    
    except Exception as e:
        print(f"❌ שגיאה: {e}")
    
    finally:
        scraper.close()
        print(f"✅ סיום בדיקה")

# הרץ מיד בהתחלה
print("\n🔄 מריץ בדיקה ראשונית...")
run_scraper()

# תזמן לרוץ כל 5 דקות
schedule.every(5).minutes.do(run_scraper)

print(f"\n✅ המערכת פעילה - תבדוק כל 5 דקות")
print(f"⌨️  הלוגים יופיעו כאן...\n")

# רוץ לנצח
while True:
    schedule.run_pending()
    time.sleep(30)  # בדוק כל 30 שניות
