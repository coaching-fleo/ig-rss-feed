import instaloader
from feedgen.feed import FeedGenerator
import datetime
import os

# 1. Impostazioni
L = instaloader.Instaloader(quiet=True)
PROFILE = "federico_leo88"

# 2. Recupera le credenziali segrete da GitHub
IG_USER = os.environ.get("IG_USER")
IG_PASS = os.environ.get("IG_PASS")

# 3. Inizializza il Feed RSS
fg = FeedGenerator()
fg.title(f'Instagram Feed - {PROFILE}')
fg.link(href=f'https://instagram.com/{PROFILE}', rel='alternate')
fg.description(f'Ultimi post di {PROFILE} su Instagram')

try:
    # 4. Fai il Login con l'account finto per bypassare i blocchi
    if IG_USER and IG_PASS:
        try:
            L.login(IG_USER, IG_PASS)
            print("Login effettuato con successo.")
        except Exception as e:
            print(f"Errore di login: {e}")
    else:
        print("ATTENZIONE: Credenziali non trovate nei Secrets.")

    # 5. Scarica i dati del profilo
    profile = instaloader.Profile.from_username(L.context, PROFILE)
    
    # 6. Estrae gli ultimi 10 post
    for i, post in enumerate(profile.get_posts()):
        if i >= 10:
            break
            
        fe = fg.add_entry()
        fe.id(post.shortcode)
        fe.title(f'Post del {post.date_utc.strftime("%d/%m/%Y")}')
        fe.link(href=f'https://instagram.com/p/{post.shortcode}')
        
        caption = post.caption if post.caption else ''
        fe.description(f'<img src="{post.url}" /><br><p>{caption}</p>')
        fe.pubDate(post.date_utc.replace(tzinfo=datetime.timezone.utc))
        
except Exception as e:
    print(f"Errore durante l'estrazione: {e}")

# 7. Salva il file
fg.rss_file('feed.xml')
