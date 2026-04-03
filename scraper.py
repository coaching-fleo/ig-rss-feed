import instaloader
from feedgen.feed import FeedGenerator
import datetime
import os

# 1. Impostazioni
PROFILE = "federico_leo88"  # INSERISCI QUI L'ACCOUNT SENZA LA @
USERNAME = os.getenv("INSTAGRAM_USERNAME")  # Da GitHub Secrets
PASSWORD = os.getenv("INSTAGRAM_PASSWORD")  # Da GitHub Secrets

# 2. Inizializza il Feed RSS
fg = FeedGenerator()
fg.title(f'Instagram Feed - {PROFILE}')
fg.link(href=f'https://instagram.com/{PROFILE}', rel='alternate')
fg.description(f'Ultimi post di {PROFILE} su Instagram')

try:
    # 3. Login a Instagram (OBBLIGATORIO)
    if not USERNAME or not PASSWORD:
        raise ValueError("❌ INSTAGRAM_USERNAME e INSTAGRAM_PASSWORD non impostati nei GitHub Secrets!")
    
    L = instaloader.Instaloader(
        quiet=False,  # Mostra i log per debuggare
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    )
    
    print(f"🔐 Login come {USERNAME}...")
    L.login(USERNAME, PASSWORD)
    print("✅ Login riuscito!")
    
    # 4. Scarica i dati del profilo
    print(f"📥 Recupero profilo {PROFILE}...")
    profile = instaloader.Profile.from_username(L.context, PROFILE)
    print(f"✅ Profilo trovato: {profile.full_name} ({profile.followees} follower)")
    
    # 5. Estrae gli ultimi 10 post
    post_count = 0
    for post in profile.get_posts():
        if post_count >= 10:
            break
        
        try:
            fe = fg.add_entry()
            fe.id(post.shortcode)
            fe.title(f'Post del {post.date_utc.strftime("%d/%m/%Y")}')
            fe.link(href=f'https://instagram.com/p/{post.shortcode}')
            
            # Crea il contenuto: immagine + testo
            caption = post.caption if post.caption else "[Nessun testo]"
            
            # Se è un video, usa una preview
            if post.is_video:
                fe.description(f'<p><strong>Video</strong></p><img src="{post.url}" alt="Video thumbnail"/><br><p>{caption}</p>')
            else:
                fe.description(f'<img src="{post.url}" alt="Post image"/><br><p>{caption}</p>')
            
            # Data formattata correttamente
            fe.pubDate(post.date_utc.replace(tzinfo=datetime.timezone.utc))
            
            post_count += 1
            print(f"  ✓ Post aggiunto: {post.shortcode}")
            
        except Exception as e:
            print(f"  ⚠️ Errore nel post {post.shortcode}: {e}")
            continue
    
    print(f"\n✅ {post_count} post aggiunti al feed!")
    
except instaloader.exceptions.InstaloaderException as e:
    print(f"❌ Errore Instagram: {e}")
    print("💡 Controlla che USERNAME e PASSWORD siano corretti nei GitHub Secrets")
    
except ValueError as e:
    print(f"❌ Configurazione mancante: {e}")
    
except Exception as e:
    print(f"❌ Errore inaspettato: {e}")
    import traceback
    traceback.print_exc()

# 6. Salva il file (sempre, anche se vuoto per debuggare)
try:
    fg.rss_file('feed.xml')
    print("💾 Feed salvato in feed.xml")
except Exception as e:
    print(f"❌ Errore nel salvataggio del feed: {e}")
