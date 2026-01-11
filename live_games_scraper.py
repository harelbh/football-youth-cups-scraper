"""
Live Games Scraper - שולף משחקים חיים מדף הלייב של ההתאחדות
"""

import os
import json
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# גביעי הנוער שלנו
OUR_CUPS = {
    586: 'גביע לנוער ע"ש אבי רן ז"ל',
    587: 'גביע נערים א\' ע"ש חיים הברפלד ז"ל',
    588: 'גביע נערים ב\' ע"ש ברוך מנדלבליט ז"ל',
    589: 'גביע נערים ג ע"ש ז.קליאוט ז"ל',
    590: 'גביע ילדים א\' ע"ש דוד שוויצר ז"ל',
    591: 'גביע ילדים ב\' ע"ש שמואל סוחר ז"ל',
    592: 'גביע ילדים ג\' ע"ש יעקב גרונדמן ז"ל',
    593: 'גביע ילדים טרום א\'',
    692: 'גביע נערות ע"ש צבי (וילי) וילינגר ז"ל',
    718: 'גביע המדינה לילדות א\' ע"ש יהל שרעבי ז"ל',
    813: 'גביע המדינה לנערות א\' ע\'\'ש מאי נעים ז\'\'ל',
    919: 'גביע המדינה לילדות ב\'',
    790: 'גביע אתנה'
}

class LiveGamesScraper:
    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        # השתמש ב-webdriver-manager להורדה אוטומטית של ChromeDriver התואם
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.live_matches = []
    
    def scrape_live_games(self):
        """שלוף משחקים חיים מדף הלייב"""
        print("\n🔴 שולף משחקים חיים מדף הלייב...")
        
        try:
            # טען את דף הלייב
            url = 'https://www.football.org.il/gameslive/'
            self.driver.get(url)
            
            # חכה קצת שהדף ייטען
            import time
            time.sleep(3)
            
            # מצא את כל שורות המשחקים
            game_rows = self.driver.find_elements(By.CSS_SELECTOR, 'a.table_row')
            
            print(f"📊 נמצאו {len(game_rows)} משחקים חיים באתר")
            
            for row in game_rows:
                try:
                    match = self.parse_live_game(row)
                    if match and self.is_our_cup(match):
                        self.live_matches.append(match)
                        print(f"✅ {match['homeTeam']} vs {match['awayTeam']} - {match['liveMinute']}'")
                
                except Exception as e:
                    continue
            
            print(f"\n🎯 סה\"כ {len(self.live_matches)} משחקים חיים מהגביעים שלנו")
            return self.live_matches
        
        except Exception as e:
            print(f"❌ שגיאה בשליפת דף הלייב: {e}")
            return []
    
    def parse_live_game(self, row):
        """פרסר משחק בודד"""
        try:
            # ליגה/גביע
            league = row.find_element(By.CSS_SELECTOR, '.table_col:nth-child(1)').text.strip()
            
            # מחזור
            round_name = row.find_element(By.CSS_SELECTOR, '.table_col:nth-child(2)').text.strip()
            
            # דקה חיה
            live_minute = None
            try:
                live_span = row.find_element(By.CSS_SELECTOR, '.onLive')
                live_minute = live_span.text.strip()
            except:
                # אם אין onLive, אולי יש "הפסקה"
                date_col = row.find_element(By.CSS_SELECTOR, '.table_col.date')
                date_text = date_col.text.strip()
                if 'הפסקה' in date_text or 'הארכה' in date_text:
                    live_minute = date_text
            
            # קבוצות
            teams_text = row.find_element(By.CSS_SELECTOR, '.table_col:nth-child(4)').text.strip()
            teams = teams_text.split(' - ')
            home_team = teams[0].strip() if len(teams) > 0 else ''
            away_team = teams[1].strip() if len(teams) > 1 else ''
            
            # מגרש
            field = row.find_element(By.CSS_SELECTOR, '.table_col:nth-child(5)').text.strip()
            
            # תוצאה
            score_text = row.find_element(By.CSS_SELECTOR, '.table_col:nth-child(6)').text.strip()
            home_score = None
            away_score = None
            if '-' in score_text:
                parts = score_text.split('-')
                try:
                    home_score = int(parts[0].strip())
                    away_score = int(parts[1].strip())
                except:
                    pass
            
            # קישור
            link = row.get_attribute('href')
            
            return {
                'cupName': league,
                'round': round_name,
                'homeTeam': home_team,
                'awayTeam': away_team,
                'field': field,
                'score': {'home': home_score, 'away': away_score},
                'liveMinute': live_minute,
                'link': link,
                'status': 'live'
            }
        
        except Exception as e:
            return None
    
    def is_our_cup(self, match):
        """בדוק אם המשחק משייך לאחד מהגביעים שלנו"""
        cup_name = match['cupName']
        
        # בדוק אם שם הגביע מכיל אחד מהשמות שלנו
        for cup_id, our_cup_name in OUR_CUPS.items():
            # השווה בלי רווחים ותווים מיוחדים
            clean_cup = cup_name.replace(' ', '').replace('"', '').replace("'", '')
            clean_our = our_cup_name.replace(' ', '').replace('"', '').replace("'", '')
            
            if clean_our in clean_cup or clean_cup in clean_our:
                match['cupId'] = cup_id
                return True
        
        return False
    
    def close(self):
        self.driver.quit()


def main():
    """פונקציה ראשית"""
    print(f"\n🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🔴 מריץ סקרייפר משחקים חיים...")
    
    scraper = LiveGamesScraper()
    
    try:
        # שלוף משחקים חיים
        live_matches = scraper.scrape_live_games()
        
        if live_matches:
            # שמור מקומית
            print(f"\n💾 שומר {len(live_matches)} משחקים חיים...")
            with open('live_matches.json', 'w', encoding='utf-8') as f:
                json.dump(live_matches, f, ensure_ascii=False, indent=2)
            print(f"✅ live_matches.json נשמר")
        else:
            print("💤 אין משחקים חיים כרגע")
            # מחק את הקובץ אם קיים
            if os.path.exists('live_matches.json'):
                os.remove('live_matches.json')
    
    except Exception as e:
        print(f"\n❌ שגיאה כללית: {e}")
    
    finally:
        scraper.close()
        print(f"\n✅ סיום")


if __name__ == "__main__":
    main()
