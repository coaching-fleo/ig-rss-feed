import requests
import datetime

PROFILE = "federico_leo88"
RSSHUB_URL = f"https://rsshub.app/instagram/user/{PROFILE}"

try:
    print(f"📥 Recupero feed RSS da RSSHub per {PROFILE}...")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    response = requests.get(RSSHUB_URL, headers=headers, timeout=15)
    response.raise_for_status()
    
    feed_content = response.text
    
    if '<item>' in feed_content or '<entry>' in feed_content:
        print("✅ Feed scaricato con successo!")
        print(f"📊 Numero di post nel feed: {feed_content.count('<item>')}")
    else:
        print("⚠️ Feed scaricato ma sembra vuoto")
    
except requests.exceptions.Timeout:
    print("⚠️ Timeout - RSSHub potrebbe essere sovraccarico. Prova tra poco.")
    feed_content = '''<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
    <channel>
        <title>Instagram Feed - {}</title>
        <link>https://instagram.com/{}</link>
        <description>Feed temporaneamente non disponibile</description>
    </channel>
</rss>'''.format(PROFILE, PROFILE)
    
except Exception as e:
    print(f"❌ Errore: {e}")
    feed_content = '''<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
    <channel>
        <title>Instagram Feed - {}</title>
        <link>https://instagram.com/{}</link>
        <description>Feed non disponibile</description>
    </channel>
</rss>'''.format(PROFILE, PROFILE)

# Salva il file
try:
    with open('feed.xml', 'w', encoding='utf-8') as f:
        f.write(feed_content)
    print("💾 Feed salvato in feed.xml")
except Exception as e:
    print(f"❌ Errore nel salvataggio: {e}")
