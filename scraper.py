import requests
from feedgen.feed import FeedGenerator
import datetime
import json
import re

PROFILE = "federico_leo88"

fg = FeedGenerator()
fg.title(f'Instagram Feed - {PROFILE}')
fg.link(href=f'https://instagram.com/{PROFILE}', rel='alternate')
fg.description(f'Ultimi post di {PROFILE} su Instagram')

try:
    print(f"📥 Recupero profilo {PROFILE}...")
    
    # 1. Scarica la pagina Instagram (pubblica)
    url = f"https://www.instagram.com/{PROFILE}/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    
    print("✅ Pagina scaricata!")
    
    # 2. Estrai i dati JSON dal HTML
    # Instagram mette i dati in una variabile JavaScript
    match = re.search(r'window\._sharedData\s*=\s*({.*?});', response.text)
    
    if not match:
        # Prova pattern alternativo (Instagram cambia spesso)
        match = re.search(r'<script type="application/ld\+json">(.*?)</script>', response.text)
    
    if not match:
        raise Exception("❌ Non riesco a trovare i dati Instagram nella pagina. Instagram potrebbe aver cambiato il formato.")
    
    data = json.loads(match.group(1))
    
    # 3. Naviga nella struttura JSON
    try:
        user = data['entry_data']['ProfilePage'][0]['graphql']['user']
        profile_name = user['full_name']
        follower_count = user['edge_followed_by']['count']
        print(f"✅ Profilo trovato: {profile_name} ({follower_count} follower)")
    except KeyError:
        print("⚠️ Struttura JSON inaspettata, provo comunque a estrarre i post...")
        user = data.get('graphql', {}).get('user', {})
    
    # 4. Estrai i post
    try:
        edges = user['edge_owner_to_timeline_media']['edges']
    except KeyError:
        edges = user.get('edge_owner_to_timeline_media', {}).get('edges', [])
    
    if not edges:
        raise Exception("❌ Nessun post trovato. Il profilo potrebbe essere privato.")
    
    # 5. Aggiungi i post al feed (max 10)
    post_count = 0
    for edge in edges[:10]:
        try:
            node = edge['node']
            
            post_id = node.get('id')
            shortcode = node.get('shortcode')
            caption_text = ""
            
            # Estrai il caption se disponibile
            if node.get('edge_media_to_caption'):
                captions = node['edge_media_to_caption'].get('edges', [])
                if captions:
                    caption_text = captions[0]['node'].get('text', '')
            
            timestamp = node.get('taken_at_timestamp')
            if timestamp:
                dt = datetime.datetime.fromtimestamp(int(timestamp), tz=datetime.timezone.utc)
            else:
                dt = datetime.datetime.now(datetime.timezone.utc)
            
            # Prendi l'immagine
            image_url = node.get('display_url', '')
            
            # Se è un carousel, prendi il primo media
            if not image_url and node.get('edge_sidecar_to_children'):
                children = node['edge_sidecar_to_children'].get('edges', [])
                if children:
                    image_url = children[0]['node'].get('display_url', '')
            
            # Crea l'entry
            fe = fg.add_entry()
            fe.id(post_id)
            fe.title(f'Post del {dt.strftime("%d/%m/%Y %H:%M")}')
            fe.link(href=f'https://instagram.com/p/{shortcode}')
            
            # Stats
            likes = node.get('edge_liked_by', {}).get('count', 0)
            comments = node.get('edge_media_to_comment', {}).get('count', 0)
            
            # Descrizione con immagine
            if image_url:
                description_html = f'''
                <img src="{image_url}" alt="Post image" style="max-width: 500px; display: block; margin: 10px 0;"/>
                <p><strong>❤️ {likes} | 💬 {comments}</strong></p>
                <p>{caption_text if caption_text else "[Nessun testo]"}</p>
                '''
            else:
                description_html = f'<p>{caption_text if caption_text else "[Nessun testo]"}</p>'
            
            fe.description(description_html)
            fe.pubDate(dt)
            
            post_count += 1
            print(f"  ✓ Post aggiunto: {shortcode}")
            
        except Exception as e:
            print(f"  ⚠️ Errore nel post: {e}")
            continue
    
    print(f"\n✅ {post_count} post aggiunti al feed!")
    
except requests.exceptions.RequestException as e:
    print(f"❌ Errore di connessione: {e}")
    
except json.JSONDecodeError as e:
    print(f"❌ Errore nel parsing JSON: {e}")
    print("💡 Instagram potrebbe aver cambiato il formato della pagina")
    
except Exception as e:
    print(f"❌ Errore: {e}")
    import traceback
    traceback.print_exc()

# 6. Salva il file
try:
    fg.rss_file('feed.xml')
    print("💾 Feed salvato in feed.xml")
except Exception as e:
    print(f"❌ Errore nel salvataggio del feed: {e}")
