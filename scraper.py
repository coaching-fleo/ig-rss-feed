from instagrapi import Client
from feedgen.feed import FeedGenerator
import datetime
import os
import json

PROFILE = "federico_leo88"
USERNAME = os.getenv("INSTAGRAM_USERNAME")
PASSWORD = os.getenv("INSTAGRAM_PASSWORD")

fg = FeedGenerator()
fg.title(f'Instagram Feed - {PROFILE}')
fg.link(href=f'https://instagram.com/{PROFILE}', rel='alternate')
fg.description(f'Ultimi post di {PROFILE} su Instagram')

try:
    if not USERNAME or not PASSWORD:
        raise ValueError("❌ INSTAGRAM_USERNAME e INSTAGRAM_PASSWORD non impostati nei GitHub Secrets!")
    
    print(f"🔐 Inizializzazione client Instagram...")
    cl = Client()
    
    # Carica sessione salvata se esiste
    session_file = "instagram_session.json"
    if os.path.exists(session_file):
        print(f"📂 Carico sessione salvata...")
        cl.load_settings(session_file)
        try:
            cl.get_timeline_feed()  # Verifica se sessione è valida
            print("✅ Sessione valida!")
        except Exception as e:
            print(f"⚠️ Sessione scaduta, effettuo nuovo login...")
            cl.login(USERNAME, PASSWORD)
            cl.dump_settings(session_file)
    else:
        print(f"🔐 Login come {USERNAME}...")
        cl.login(USERNAME, PASSWORD)
        cl.dump_settings(session_file)  # Salva la sessione
        print("✅ Login riuscito e sessione salvata!")
    
    # Recupera il profilo
    print(f"📥 Recupero profilo {PROFILE}...")
    user_info = cl.user_info_by_username(PROFILE)
    print(f"✅ Profilo trovato: {user_info.full_name} ({user_info.follower_count} follower)")
    
    # Estrae gli ultimi 10 post
    print(f"📊 Recupero ultimi 10 post...")
    medias = cl.user_medias(user_info.pk, amount=10)
    
    post_count = 0
    for media in medias:
        try:
            fe = fg.add_entry()
            fe.id(str(media.pk))
            fe.title(f'Post del {media.taken_at.strftime("%d/%m/%Y")}')
            fe.link(href=f'https://instagram.com/p/{media.code}')
            
            caption = media.caption_text if media.caption_text else "[Nessun testo]"
            
            # Prendi l'immagine
            image_url = ""
            if hasattr(media, 'image_versions2') and media.image_versions2:
                image_url = media.image_versions2.candidates[0].url
            elif hasattr(media, 'thumbnail_url'):
                image_url = media.thumbnail_url
            
            if image_url:
                fe.description(f'<img src="{image_url}" alt="Post image" style="max-width: 500px;"/><br><p>{caption}</p>')
            else:
                fe.description(f'<p>{caption}</p>')
            
            fe.pubDate(media.taken_at.replace(tzinfo=datetime.timezone.utc))
            
            post_count += 1
            print(f"  ✓ Post aggiunto: {media.code}")
            
        except Exception as e:
            print(f"  ⚠️ Errore nel post {media.code}: {e}")
            continue
    
    print(f"\n✅ {post_count} post aggiunti al feed!")
    
except Exception as e:
    print(f"❌ Errore: {e}")
    import traceback
    traceback.print_exc()

try:
    fg.rss_file('feed.xml')
    print("💾 Feed salvato in feed.xml")
except Exception as e:
    print(f"❌ Errore nel salvataggio: {e}")
