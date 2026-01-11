"""
Football Youth Leagues Scraper for Railway.app
שולף משחקים מכל הליגות ושומר ב-GitHub Pages
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

# רשימת כל הליגות (202 ליגות!)
YOUTH_LEAGUES = {
    'נשים': [637, 639, 741, 654, 651, 641, 808, 860, 823, 809, 859, 705, 815, 749, 717, 900, 810, 901, 903, 902],
    'נוער': [101, 103, 102, 105, 104, 920, 787, 666, 110, 115],
    'נערים א\'': [726, 121, 120, 646, 755, 123, 122, 665, 664],
    'נערים ב\'': [773, 719, 720, 135, 139, 706, 131, 137, 130, 658, 134],
    'נערים ג\'': [824, 845, 826, 736, 663, 758, 759, 146, 816, 707, 144],
    'ילדים א\'': [871, 155, 734, 870, 648, 865, 764, 875, 876, 662, 862, 152, 156, 788, 150, 712, 872, 863, 158, 154, 861],
    'ילדים ב\'': [880, 739, 748, 689, 852, 868, 804, 881, 882, 897, 161, 165, 792, 879, 160, 747, 767, 878, 167, 163, 877, 765],
    'ילדים ג\'': [886, 887, 175, 713, 769, 890, 888, 770, 883, 884, 794, 738, 173, 793, 744, 170, 172, 885, 891, 174, 892, 661, 780, 750, 649],
    'טרום ילדים א\'': [908, 182, 631, 737, 838, 771, 819, 180, 710, 183, 801, 799, 840, 800, 904, 660, 839, 181, 806, 752],
    'טרום ילדים ב\'': [640, 732, 912, 913, 843, 798, 659, 851, 657, 844, 921, 922, 842, 186, 918, 722],
    'טרום ילדים ג\'': [795, 652, 916]
}

SEASON_ID = 27

class YouthLeaguesScraper:
    def __init__(self):
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        
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
    
    def extract_matches_from_league(self, league_id, league_name, category):
        url = f"https://www.football.org.il/leagues/league/?league_id={league_id}&season_id={SEASON_ID}"
        print(f"🔄 {league_name} (ID: {league_id})...")
        
        try:
            self.driver.get(url)
            time.sleep(random.uniform(3, 6))
            
            # בדוק אם הדף קיים
            try:
                page_title = self.driver.find_element(By.TAG_NAME, 'h1').text.strip()
                if not page_title or 'לא נמצא' in page_title:
                    print(f"  ⚠️  דף לא קיים")
                    return []
            except:
                print(f"  ⚠️  בעיה בטעינת הדף")
                return []
            
            match_rows = self.driver.find_elements(By.CSS_SELECTOR, '.results-grid .table_row')
            matches = []
            
            for index, row in enumerate(match_rows):
                try:
                    date = row.find_element(By.CSS_SELECTOR, '.game-date').text.strip() if row.find_elements(By.CSS_SELECTOR, '.game-date') else ''
                    
                    teams = row.find_elements(By.CSS_SELECTOR, '.team-name-text')
                    home_team = teams[0].text.replace('-', '').replace('\xa0', '').strip() if len(teams) > 0 else ''
                    away_team = teams[1].text.strip() if len(teams) > 1 else ''
                    
                    field_elements = row.find_elements(By.CSS_SELECTOR, '.table_col.align_content')
                    field = field_elements[2].text.replace('מגרש', '').strip() if len(field_elements) > 2 else ''
                    
                    # שעה - חיפוש משופר
                    match_time = None
                    
                    try:
                        time_cols = row.find_elements(By.XPATH, ".//div[@class='table_col'][.//span[@class='sr-only' and text()='שעה']]")
                        
                        if time_cols:
                            time_text = time_cols[0].text.strip()
                            time_text = time_text.replace('שעה', '').replace("'", '').replace('"', '').replace('״', '').replace('׳', '').strip()
                            
                            if ':' in time_text:
                                parts = time_text.split(':')
                                if len(parts) == 2:
                                    try:
                                        hour = int(parts[0])
                                        minute = int(parts[1])
                                        if 0 <= hour <= 23 and 0 <= minute <= 59:
                                            match_time = time_text
                                    except:
                                        pass
                    except:
                        pass
                    
                    # גיבוי - חיפוש כללי
                    if not match_time:
                        try:
                            all_cols = row.find_elements(By.CSS_SELECTOR, '.table_col')
                            
                            for col in all_cols:
                                text = col.text.strip()
                                text = text.replace('שעה', '').replace("'", '').replace('"', '').replace('״', '').replace('׳', '').strip()
                                if ':' in text and len(text) >= 4 and len(text) <= 5:
                                    parts = text.split(':')
                                    if len(parts) == 2:
                                        try:
                                            hour = int(parts[0])
                                            minute = int(parts[1])
                                            if 0 <= hour <= 23 and 0 <= minute <= 59:
                                                match_time = text
                                                break
                                        except:
                                            continue
                        except:
                            pass
                    
                    result = row.find_element(By.CSS_SELECTOR, '.result').text.replace('תוצאה', '').strip() if row.find_elements(By.CSS_SELECTOR, '.result') else ''
                    
                    extra_elements = row.find_elements(By.CSS_SELECTOR, '.new-desktop-only')
                    extra_time = extra_elements[0].text.replace('הארכה', '').strip() if len(extra_elements) > 0 else ''
                    penalties = extra_elements[1].text.replace('ב.הכרעה', '').strip() if len(extra_elements) > 1 else ''
                    
                    link = row.get_attribute('href') or ''
                    if link and not link.startswith('http'):
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
                        'leagueId': league_id,
                        'leagueName': league_name,
                        'category': category,
                        'index': index + 1,
                        'date': date,
                        'time': match_time,
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
                    continue
            
            print(f"  ✅ {len(matches)} משחקים")
            return matches
        except Exception as e:
            print(f"  ❌ שגיאה: {e}")
            return []
    
    def scrape_all_leagues(self):
        print("="*60)
        print("🚀 מתחיל שליפה מכל הליגות")
        print("="*60)
        
        for category, league_ids in YOUTH_LEAGUES.items():
            print(f"\n📂 קטגוריה: {category} ({len(league_ids)} ליגות)")
            
            for league_id in league_ids:
                # נסה לשלוף את שם הליגה מהדף
                try:
                    url = f"https://www.football.org.il/leagues/league/?league_id={league_id}&season_id={SEASON_ID}"
                    self.driver.get(url)
                    time.sleep(1)
                    
                    league_name_elem = self.driver.find_element(By.TAG_NAME, 'h1')
                    league_name = league_name_elem.text.strip()
                    
                    if '2025/2026' in league_name:
                        parts = league_name.split('\n')
                        league_name = parts[-1] if len(parts) > 1 else league_name
                    
                    if not league_name or league_name == '2025/2026':
                        league_name = f"ליגה {league_id}"
                except:
                    league_name = f"ליגה {league_id}"
                
                matches = self.extract_matches_from_league(league_id, league_name, category)
                self.all_matches.extend(matches)
                
                time.sleep(random.uniform(2, 5))
        
        print(f"\n✅ סה\"כ: {len(self.all_matches)} משחקים מ-{sum(len(ids) for ids in YOUTH_LEAGUES.values())} ליגות")
        return self.all_matches
    
    def close(self):
        self.driver.quit()


def setup_git():
    """הגדר Git עם Token"""
    print("\n🔧 מגדיר Git...")
    
    try:
        subprocess.run(['git', 'config', '--global', 'user.email', GITHUB_EMAIL], check=True)
        subprocess.run(['git', 'config', '--global', 'user.name', GITHUB_NAME], check=True)
        
        repo_url = f"https://{GITHUB_TOKEN}@github.com/{GITHUB_REPO}.git"
        
        if not os.path.exists('repo'):
            print("📦 Cloning repository...")
            subprocess.run(['git', 'clone', repo_url, 'repo'], check=True)
        else:
            print("📥 Pulling latest changes...")
            os.chdir('repo')
            subprocess.run(['git', 'pull'], check=True)
            os.chdir('..')
        
        print("✅ Git מוכן!")
        return True
    except Exception as e:
        print(f"❌ שגיאה בהגדרת Git: {e}")
        return False


def save_to_github(matches, filename='leagues_matches.json'):
    """שמור נתונים ודחוף ל-GitHub"""
    print(f"\n📤 שומר ל-GitHub...")
    
    try:
        os.chdir('repo')
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(matches, f, ensure_ascii=False, indent=2)
        
        print(f"✅ {filename} נשמר")
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        subprocess.run(['git', 'add', filename], check=True)
        subprocess.run(['git', 'commit', '-m', f'Update leagues - {timestamp}'], check=True)
        subprocess.run(['git', 'push'], check=True)
        
        print(f"✅ נדחף ל-GitHub בהצלחה!")
        
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
    """בדוק אם צריך לעדכן - אם יש משחקים פעילים"""
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
    
    if not setup_git():
        print("❌ לא ניתן להמשיך בלי Git")
        return
    
    scraper = YouthLeaguesScraper()
    
    try:
        matches = scraper.scrape_all_leagues()
        
        if not matches:
            print("❌ לא נמצאו משחקים")
            return
        
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
