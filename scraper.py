import requests
import datetime

PROFILE = "federico_leo88"

# Prova più servizi in order di preferenza
SERVICES = [
    f"https://bibliogram.art/rss/user/{PROFILE}",
    f"https://insta.trom.tf/rss/user/{PROFILE}",
    f"https://biblio.1d10t.org/rss/user/{PROFILE}",
]

feed_content = None

for url in SERVICES:
    try:
        print(f"📥 Tentativo: {url.split('/')[2]}...")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        feed_content = response.text
        
        if '<item>' in feed_content or '<entry>' in feed_content:
            print(f"✅ Feed scaricato con successo da {url.split('/')[2]}!")
            print(f"📊 Numero di post: {feed_content.count('<item>')}")
            break
        
    except requests.exceptions.Timeout:
        print(f"⏱️ Timeout")
        continue
    except requests.exceptions.HTTPError as e:
        print(f"❌ Errore {e.response.status_code}")
        continue
    except Exception as e:
        print(f"⚠️ Errore: {e}")
        continue

# Se nessuno funziona, crea un feed vuoto ma valido
if not feed_content:
    print("\n⚠️ Nessun servizio disponibile. Creando feed vuoto...")
    feed_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
    <channel>
        <title>Instagram Feed - {PROFILE}</title>
        <link>https://instagram.com/{PROFILE}</link>
        <description>Feed di {PROFILE}</description>
        <lastBuildDate>{datetime.datetime.now().strftime('%a, %d %b %Y %H:%M:%S +0000')}</lastBuildDate>
    </channel>
</rss>'''

# Salva il file
try:
    with open('feed.xml', 'w', encoding='utf-8') as f:
        f.write(feed_content)
    print("💾 Feed salvato in feed.xml")
except Exception as e:
    print(f"❌ Errore nel salvataggio: {e}")
