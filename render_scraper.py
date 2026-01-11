"""
Football Youth Cups Scraper for Railway.app
שומר נתונים ב-GitHub Pages
"""

import os
import json
import time
import random
import subprocess
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# הגדרות מהמשתני סביבה
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN', '')
GITHUB_REPO = os.getenv('GITHUB_REPO', 'harelbh/football-youth-cups-scraper')
GITHUB_EMAIL = os.getenv('GITHUB_EMAIL', 'bot@railway.app')
GITHUB_NAME = os.getenv('GITHUB_NAME', 'Railway Bot')

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
                    
                    # שלוף דקה חיה (אם קיימת)
                    live_minute = None
                    try:
                        live_span = row.find_element(By.CSS_SELECTOR, '.onLive')
                        live_minute = live_span.text.strip()
                        if live_minute:
                            print(f"      🔴 דקה חיה: {live_minute}")
                    except:
                        pass
                    
                    teams = row.find_elements(By.CSS_SELECTOR, '.team-name-text')
                    home_team = teams[0].text.replace('-', '').strip() if len(teams) > 0 else ''
                    away_team = teams[1].text.strip() if len(teams) > 1 else ''
                    
                    field_elements = row.find_elements(By.CSS_SELECTOR, '.table_col.align_content')
                    field = field_elements[2].text.replace('מגרש', '').strip() if len(field_elements) > 2 else ''
                    
                    # שעה - חיפוש משופר עם DEBUG
                    match_time = None
                    
                    try:
                        # חיפוש העמודה שיש בה span עם "שעה"
                        time_cols = row.find_elements(By.XPATH, ".//div[@class='table_col'][.//span[@class='sr-only' and text()='שעה']]")
                        
                        if time_cols:
                            time_text = time_cols[0].text.strip()
                            print(f"      DEBUG: נמצאה עמודת שעה, טקסט מקורי: '{time_text}'")
                            
                            # הטקסט יכול להיות "שעה14:00" או "14:00" או "14:00'"
                            time_text = time_text.replace('שעה', '').strip()
                            # הסר גרשיים ותווים מיוחדים
                            time_text = time_text.replace("'", '').replace('"', '').replace('״', '').replace('׳', '').strip()
                            print(f"      DEBUG: אחרי ניקוי: '{time_text}'")
                            
                            # בדיקה שזו שעה תקינה
                            if ':' in time_text:
                                parts = time_text.split(':')
                                if len(parts) == 2:
                                    try:
                                        hour = int(parts[0])
                                        minute = int(parts[1])
                                        if 0 <= hour <= 23 and 0 <= minute <= 59:
                                            match_time = time_text
                                            print(f"      ✅ שעה נמצאה: {match_time}")
                                    except Exception as e:
                                        print(f"      ❌ שגיאה בפרסור: {e}")
                        else:
                            print(f"      ⚠️  לא נמצאה עמודת שעה - מנסה גיבוי")
                            
                    except Exception as e:
                        print(f"      ❌ שגיאה בחיפוש שעה: {e}")
                    
                    # ניסיון גיבוי: חיפוש כללי
                    if not match_time:
                        try:
                            all_cols = row.find_elements(By.CSS_SELECTOR, '.table_col')
                            
                            for col in all_cols:
                                text = col.text.strip()
                                # נקה תווים מיוחדים
                                text = text.replace('שעה', '').replace("'", '').replace('"', '').replace('״', '').replace('׳', '').strip()
                                if ':' in text and len(text) >= 4 and len(text) <= 5:
                                    parts = text.split(':')
                                    if len(parts) == 2:
                                        try:
                                            hour = int(parts[0])
                                            minute = int(parts[1])
                                            if 0 <= hour <= 23 and 0 <= minute <= 59:
                                                match_time = text
                                                print(f"      ✅ שעה נמצאה בגיבוי: {match_time}")
                                                break
                                        except:
                                            continue
                        except Exception as e:
                            print(f"      ❌ שגיאה בגיבוי: {e}")
                    
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
                    
                    # קביעת סטטוס - בדיקה חכמה
                    status = 'upcoming'
                    
                    if extra_time or penalties:
                        # יש הארכה או פנדלים - בטוח נגמר
                        status = 'finished'
                    elif live_minute:
                        # יש דקה חיה מהאתר - המשחק חי!
                        status = 'live'
                    elif home_score is not None and away_score is not None:
                        # יש תוצאה אבל אין דקה חיה - בדוק לפי זמן
                        if date and match_time:
                            try:
                                from datetime import datetime
                                day, month, year = date.split('/')
                                hour, minute = match_time.split(':')
                                match_dt = datetime(int(year), int(month), int(day), int(hour), int(minute))
                                now = datetime.now()
                                diff_minutes = (now - match_dt).total_seconds() / 60
                                
                                # חי רק אם התחיל לפני 0-120 דקות
                                if 0 <= diff_minutes <= 120:
                                    status = 'live'
                                else:
                                    status = 'finished'  # עבר זמן רב מדי
                            except:
                                # אם יש בעיה בפרסור - נניח שנגמר
                                status = 'finished'
                        else:
                            # אין מידע על זמן - אם יש תוצאה נניח שנגמר
                            status = 'finished'
                    
                    matches.append({
                        'cupId': cup_id,
                        'cupName': cup_name,
                        'category': category,
                        'index': index + 1,
                        'date': date,
                        'time': match_time,  # כעת יכול להיות None או שעה תקינה
                        'homeTeam': home_team,
                        'awayTeam': away_team,
                        'field': field,
                        'score': {'home': home_score, 'away': away_score},
                        'extraTime': extra_time or None,
                        'penalties': penalties or None,
                        'liveMinute': live_minute,  # הדקה האמיתית מהאתר!
                        'link': link,
                        'status': status
                    })
                except Exception as e:
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


def setup_git():
    """הגדר Git עם Token"""
    print("\n🔧 מגדיר Git...")
    
    try:
        # הגדר משתמש
        subprocess.run(['git', 'config', '--global', 'user.email', GITHUB_EMAIL], check=True)
        subprocess.run(['git', 'config', '--global', 'user.name', GITHUB_NAME], check=True)
        
        # Clone מחדש כל פעם (למנוע קונפליקטים)
        repo_url = f"https://{GITHUB_TOKEN}@github.com/{GITHUB_REPO}.git"
        
        if os.path.exists('repo'):
            print("🗑️  מוחק repo ישן...")
            import shutil
            shutil.rmtree('repo')
        
        print("📦 Cloning repository...")
        subprocess.run(['git', 'clone', repo_url, 'repo'], check=True)
        
        print("✅ Git מוכן!")
        return True
    except Exception as e:
        print(f"❌ שגיאה בהגדרת Git: {e}")
        return False


def save_to_github(matches):
    """שמור נתונים ודחוף ל-GitHub"""
    print(f"\n📤 שומר ל-GitHub...")
    
    try:
        # כנס לתיקיית הRepo
        os.chdir('repo')
        
        # שמור JSON
        with open('matches.json', 'w', encoding='utf-8') as f:
            json.dump(matches, f, ensure_ascii=False, indent=2)
        
        print("✅ matches.json נשמר")
        
        # Commit & Push
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        subprocess.run(['git', 'add', 'matches.json'], check=True)
        subprocess.run(['git', 'commit', '-m', f'Update matches - {timestamp}'], check=True)
        subprocess.run(['git', 'push'], check=True)
        
        print(f"✅ נדחף ל-GitHub בהצלחה!")
        
        # חזור לתיקייה הראשית
        os.chdir('..')
        return True
        
    except subprocess.CalledProcessError as e:
        if 'nothing to commit' in str(e):
            print("💤 אין שינויים לעדכן")
            os.chdir('..')
            return True
        else:
            print(f"❌ שגיאה: {e}")
            os.chdir('..')
            return False
    except Exception as e:
        print(f"❌ שגיאה: {e}")
        try:
            os.chdir('..')
        except:
            pass
        return False


def should_update(matches):
    """בדוק אם צריך לעדכן"""
    now = datetime.now()
    
    for match in matches:
        if match['status'] == 'finished':
            continue
        
        try:
            date_parts = match['date'].split('/')
            day, month, year = int(date_parts[0]), int(date_parts[1]), int(date_parts[2])
            
            if match.get('time'):
                hour, minute = match['time'].split(':')
                hour, minute = int(hour), int(minute)
            else:
                hour, minute = 19, 0
            
            match_dt = datetime(year, month, day, hour, minute)
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
    print(f"📂 Repository: {GITHUB_REPO}")
    
    # הגדר Git
    if not setup_git():
        print("❌ לא ניתן להמשיך בלי Git")
        return
    
    scraper = YouthCupsScraper()
    
    try:
        # שלוף נתונים
        matches = scraper.scrape_all_cups()
        
        if not matches:
            print("❌ לא נמצאו משחקים")
            return
        
        # בדוק אם צריך לעדכן
        if should_update(matches):
            print(f"\n⚡ יש משחקים פעילים - מעדכן GitHub!")
            save_to_github(matches)
        else:
            print(f"\n💤 אין משחקים פעילים - לא מעדכן")
            # אבל נשמור פעם אחת בכל מקרה
            save_to_github(matches)
    
    except Exception as e:
        print(f"\n❌ שגיאה כללית: {e}")
    
    finally:
        scraper.close()
        print(f"\n✅ סיום")


if __name__ == "__main__":
    main()
