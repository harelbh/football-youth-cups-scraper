"""
Football Youth Cups Scraper for Render.com
מעדכן את השרת שלך אוטומטית
"""

import os
import json
import time
import random
import requests
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# הגדרות מהמשתני סביבה
API_URL = os.getenv('API_URL', 'https://yty.s904.upress.link/api/update.php')
API_KEY = os.getenv('API_KEY', 'change-this-to-secret-key')

# רשימת הליגות
YOUTH_CUPS = [
    {'id': 617, 'name': 'גביע המדינה נשים', 'category': 'נשים'},
    {'id': 586, 'name': 'גביע לנוער ע"ש אבי רן ז"ל', 'category': 'נוער'},
    {'id': 692, 'name': 'גביע נערות ע"ש צבי (וילי) וילינגר ז"ל', 'category': 'נערות'},
    {'id': 587, 'name': 'גביע נערים א\' ע"ש חיים הברפלד ז"ל', 'category': 'נערים א\''},
    {'id': 813, 'name': 'גביע המדינה לנערות א\' ע\'\'ש מאי נעים ז\'\'ל', 'category': 'נערות א\''},
    {'id': 588, 'name': 'גביע נערים ב\' ע"ש ברוך מנדלבליט ז"ל', 'category': 'נערים ב\''},
    {'id': 589, 'name': 'גביע נערים ג ע"ש ז.קליאוט ז"ל', 'category': 'נערים ג\''},
    {'id': 590, 'name': 'גביע ילדים א\' ע"ש דוד שוויצר ז"ל', 'category': 'ילדים א\''},
    {'id': 718, 'name': 'גביע המדינה לילדות א\' ע"ש יהל שרעבי ז"ל', 'category': 'ילדות א\''},
    {'id': 591, 'name': 'גביע ילדים ב\' ע"ש שמואל סוחר ז"ל', 'category': 'ילדים ב\''},
    {'id': 919, 'name': 'גביע המדינה לילדות ב\'', 'category': 'ילדות ב\''},
    {'id': 592, 'name': 'גביע ילדים ג\' ע"ש יעקב גרונדמן ז"ל', 'category': 'ילדים ג\''},
    {'id': 593, 'name': 'גביע ילדים טרום א\'', 'category': 'טרום א\''}
]

SEASON_ID = 27

class YouthCupsScraper:
    def __init__(self):
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        
        # User-Agent אקראי
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
        ]
        options.add_argument(f'user-agent={random.choice(user_agents)}')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        self.driver = webdriver.Chrome(options=options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        self.all_matches = []
    
    def extract_matches_from_cup(self, cup_id, cup_name, category):
        url = f"https://www.football.org.il/national-cup/?national_cup_id={cup_id}&season_id={SEASON_ID}"
        print(f"🔄 {cup_name}...")
        
        try:
            self.driver.get(url)
            time.sleep(random.uniform(3, 6))
            
            match_rows = self.driver.find_elements(By.CSS_SELECTOR, '.results-grid .table_row')
            matches = []
            
            for index, row in enumerate(match_rows):
                try:
                    date = row.find_element(By.CSS_SELECTOR, '.game-date').text.strip() if row.find_elements(By.CSS_SELECTOR, '.game-date') else ''
                    
                    teams = row.find_elements(By.CSS_SELECTOR, '.team-name-text')
                    home_team = teams[0].text.replace('-', '').strip() if len(teams) > 0 else ''
                    away_team = teams[1].text.strip() if len(teams) > 1 else ''
                    
                    field_elements = row.find_elements(By.CSS_SELECTOR, '.table_col.align_content')
                    field = field_elements[2].text.replace('מגרש', '').strip() if len(field_elements) > 2 else ''
                    
                    # שעה
                    match_time = ''
                    time_elements = row.find_elements(By.CSS_SELECTOR, '.table_col')
                    for elem in time_elements:
                        text = elem.text.strip()
                        if ':' in text and len(text) == 5 and text.count(':') == 1:
                            match_time = text
                            break
                    
                    result = row.find_element(By.CSS_SELECTOR, '.result').text.replace('תוצאה', '').strip() if row.find_elements(By.CSS_SELECTOR, '.result') else ''
                    
                    extra_elements = row.find_elements(By.CSS_SELECTOR, '.new-desktop-only')
                    extra_time = extra_elements[0].text.replace('הארכה', '').strip() if len(extra_elements) > 0 else ''
                    penalties = extra_elements[1].text.replace('ב.הכרעה', '').strip() if len(extra_elements) > 1 else ''
                    
                    link = row.get_attribute('href') or ''
                    if link:
                        link = f"https://www.football.org.il{link}"
                    
                    home_score, away_score = None, None
                    if result and '-' in result:
                        parts = result.split('-')
                        try:
                            home_score = int(parts[0].strip())
                            away_score = int(parts[1].strip())
                        except:
                            pass
                    
                    matches.append({
                        'cupId': cup_id,
                        'cupName': cup_name,
                        'category': category,
                        'index': index + 1,
                        'date': date,
                        'time': match_time or None,
                        'homeTeam': home_team,
                        'awayTeam': away_team,
                        'field': field,
                        'score': {'home': home_score, 'away': away_score},
                        'extraTime': extra_time or None,
                        'penalties': penalties or None,
                        'link': link,
                        'status': 'finished' if result else 'upcoming'
                    })
                except Exception as e:
                    print(f"  ⚠️ שגיאה בשורה {index}: {e}")
                    continue
            
            print(f"  ✅ {len(matches)} משחקים")
            return matches
        except Exception as e:
            print(f"  ❌ שגיאה: {e}")
            return []
    
    def scrape_all_cups(self):
        print("="*60)
        print("🚀 מתחיל שליפה מכל הליגות")
        print("="*60)
        
        for cup in YOUTH_CUPS:
            matches = self.extract_matches_from_cup(cup['id'], cup['name'], cup['category'])
            self.all_matches.extend(matches)
            
            if cup != YOUTH_CUPS[-1]:
                delay = random.uniform(3, 8)
                time.sleep(delay)
        
        print(f"\n✅ סה\"כ: {len(self.all_matches)} משחקים")
        return self.all_matches
    
    def close(self):
        self.driver.quit()


def upload_to_server(matches):
    """שלח נתונים לשרת"""
    print(f"\n📤 שולח נתונים לשרת...")
    
    try:
        response = requests.post(
            API_URL,
            json=matches,
            headers={
                'X-API-Key': API_KEY,
                'Content-Type': 'application/json'
            },
            timeout=30
        )
        
        if response.status_code == 200:
            print(f"✅ השרת עודכן בהצלחה!")
            return True
        else:
            print(f"❌ שגיאה: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ שגיאה בשליחה: {e}")
        return False


def should_update(matches):
    """בדוק אם צריך לעדכן (האם יש משחקים פעילים)"""
    now = datetime.now()
    
    for match in matches:
        if match['status'] == 'finished':
            continue
        
        try:
            # המר תאריך
            date_parts = match['date'].split('/')
            day, month, year = int(date_parts[0]), int(date_parts[1]), int(date_parts[2])
            
            # שעה
            if match.get('time'):
                hour, minute = match['time'].split(':')
                hour, minute = int(hour), int(minute)
            else:
                hour, minute = 19, 0
            
            match_dt = datetime(year, month, day, hour, minute)
            
            # בדוק חלון זמן: 30 דקות לפני עד שעה אחרי
            start = match_dt - timedelta(minutes=30)
            end = match_dt + timedelta(hours=1)
            
            if start <= now <= end:
                return True
        except:
            continue
    
    return False


def main():
    """פונקציה ראשית"""
    print(f"\n🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌍 API URL: {API_URL}")
    
    scraper = YouthCupsScraper()
    
    try:
        # שלוף נתונים
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
            print(f"   (עדכון יקרה רק 30 דקות לפני עד שעה אחרי משחקים)")
    
    except Exception as e:
        print(f"\n❌ שגיאה כללית: {e}")
    
    finally:
        scraper.close()
        print(f"\n✅ סיום")


if __name__ == "__main__":
    main()
