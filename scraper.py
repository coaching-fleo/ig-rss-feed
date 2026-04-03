import requests
from feedgen.feed import FeedGenerator
import datetime
import json
import re
import time

PROFILE = "federico_leo88"

fg = FeedGenerator()
fg.title(f'Instagram Feed - {PROFILE}')
fg.link(href=f'https://instagram.com/{PROFILE}', rel='alternate')
fg.description(f'Ultimi post di {PROFILE} su Instagram')

try:
    print(f"📥 Recupero profilo {PROFILE}...")
    
    # Headers realistici
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Mobile/15E148 Safari/604.1',
        'Accept-Language': 'it-IT,it;q=0.9',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    }
    
    # Prova 1: Scarica il profilo come API GraphQL
    print("  🔍 Tentativo 1: GraphQL API...")
    api_url = f"https://www.instagram.com/api/v1/users/web_profile_info/"
    params = {"username": PROFILE}
    
    session = requests.Session()
    session.headers.update(headers)
    
    # Instagram richiede un CSRF token
    csrf_response = session.get(f"https://www.instagram.com/", headers=headers)
    csrf_token = csrf_response.cookies.get('csrftoken', '')
    
    api_headers = headers.copy()
    api_headers['X-CSRFToken'] = csrf_token
    api_headers['X-Requested-With'] = 'XMLHttpRequest'
    
    response = session.get(api_url, params=params, headers=api_headers, timeout=10)
    response.raise_for_status()
    
    data = response.json()
    
    if 'user' in data:
        print("✅ Accesso via API riuscito!")
        user = data['user']
        profile_name = user.get('full_name', PROFILE)
        follower_count = user.get('follower_count', 0)
        print(f"✅ Profilo: {profile_name} ({follower_count} follower)")
        
        # Estrai i media
        medias = user.get('recent_posts', [])
        if not medias:
            medias = user.get('media', [])
        
        post_count = 0
        
        if medias:
            print(f"📊 Trovati {len(medias)} post")
            
            for media in medias[:10]:
                try:
                    post_id = media.get('id')
                    shortcode = media.get('code')
                    caption = media.get('caption', {})
                    caption_text = caption.get('text', '') if isinstance(caption, dict) else str(caption)
                    
                    timestamp = media.get('taken_at')
                    if timestamp:
                        if isinstance(timestamp, int):
                            dt = datetime.datetime.fromtimestamp(timestamp, tz=datetime.timezone.utc)
                        else:
                            dt = datetime.datetime.fromisoformat(str(timestamp).replace('Z', '+00:00'))
                    else:
                        dt = datetime.datetime.now(datetime.timezone.utc)
                    
                    # Immagine
                    image_url = media.get('image_versions2', {}).get('candidates', [{}])[0].get('url', '')
                    if not image_url:
                        image_url = media.get('display_url', '')
                    
                    likes = media.get('like_count', 0)
                    comments = media.get('comment_count', 0)
                    
                    # Crea entry
                    fe = fg.add_entry()
                    fe.id(post_id)
                    fe.title(f'Post del {dt.strftime("%d/%m/%Y %H:%M")}')
                    fe.link(href=f'https://instagram.com/p/{shortcode}')
                    
                    if image_url:
                        description_html = f'''
                        <img src="{image_url}" alt="Post" style="max-width: 500px; display: block; margin: 10px 0;"/>
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
    
    else:
        raise Exception("Risposta API inaspettata")

except requests.exceptions.HTTPError as e:
    if e.response.status_code == 401:
        print(f"❌ Non autorizzato. Prova con un profilo pubblico.")
    else:
        print(f"❌ Errore HTTP {e.response.status_code}: {e}")
        
except Exception as e:
    print(f"❌ Errore: {e}")
    import traceback
    traceback.print_exc()

# Salva il file
try:
    fg.rss_file('feed.xml')
    print("💾 Feed salvato in feed.xml")
except Exception as e:
    print(f"❌ Errore nel salvataggio: {e}")
