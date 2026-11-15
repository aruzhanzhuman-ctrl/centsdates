import os
import requests
from bs4 import BeautifulSoup

TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
URL = "https://testcisia.it/calendario.php?tolc=cent-s&lingua=inglese"
FALLBACK_URL = "https://www.cisiaonline.it/en/altra-area-geografica-en/cent-s-schedule/"

def send_telegram(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"})

def check_url(target_url):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    response = requests.get(target_url, headers=headers, timeout=20)
    if response.status_code != 200:
        return []
    
    soup = BeautifulSoup(response.text, 'html.parser')
    found = []
    
    for row in soup.find_all('tr'):
        cols = [" ".join(td.get_text().split()) for td in row.find_all(['td', 'th'])]
        if len(cols) >= 8:
            fmt = cols[0].upper()
            uni = cols[1]
            region = cols[2]
            city = cols[3]
            deadline = cols[4]
            seats = cols[5]
            state = cols[6].upper()
            exam_date = cols[7]
            
            if "CENT@HOME" in fmt and ("AVAILABLE" in state and "NOT" not in state):
                entry = (
                    f"🏛 <b>Вуз:</b> {uni}\n"
                    f"📍 <b>Регион / Город:</b> {region} ({city})\n"
                    f"📅 <b>Дата экзамена:</b> {exam_date}\n"
                    f"⏳ <b>Регистрация до:</b> {deadline}\n"
                    f"💺 <b>Свободных мест:</b> {seats}"
                )
                found.append(entry)
    return found

def main():
    try:
        results = check_url(URL)
        if not results:
            results = check_url(FALLBACK_URL)
            
        if results:
            message = "🚨 <b>ПОЯВИЛИСЬ МЕСТА НА CENT-S (CENT@HOME)!</b>\n\n" + "\n\n──────────────\n\n".join(results)
            message += f"\n\n👉 <a href='{URL}'>Открыть календарь CISIA</a>"
            send_telegram(message)
        else:
            print("Свободных мест CENT@HOME для CENT-S пока нет.")
    except Exception as e:
        print(f"Ошибка при проверке: {e}")

if __name__ == "__main__":
    main()
