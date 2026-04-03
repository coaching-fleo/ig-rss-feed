import instaloader
from feedgen.feed import FeedGenerator
import datetime

# 1. Impostazioni
L = instaloader.Instaloader(quiet=True)
PROFILE = "NOME_UTENTE_QUI" # INSERISCI QUI L'ACCOUNT SENZA LA @

# 2. Inizializza il Feed RSS
fg = FeedGenerator()
fg.title(f'Instagram Feed - {PROFILE}')
fg.link(href=f'https://instagram.com/{PROFILE}', rel='alternate')
fg.description(f'Ultimi post di {PROFILE} su Instagram')

try:
    # 3. Scarica i dati del profilo (senza login)
    profile = instaloader.Profile.from_username(L.context, PROFILE)
    
    # 4. Estrae gli ultimi 10 post
    for i, post in enumerate(profile.get_posts()):
        if i >= 10:
            break
            
        fe = fg.add_entry()
        fe.id(post.shortcode)
        fe.title(f'Post del {post.date_utc.strftime("%d/%m/%Y")}')
        fe.link(href=f'https://instagram.com/p/{post.shortcode}')
        
        # Crea il contenuto: immagine + testo
        caption = post.caption if post.caption else ''
        fe.description(f'<img src="{post.url}" /><br><p>{caption}</p>')
        
        # Aggiunge la data formattata correttamente per i feed RSS
        fe.pubDate(post.date_utc.replace(tzinfo=datetime.timezone.utc))
        
except Exception as e:
    print(f"Errore durante l'estrazione: {e}")

# 5. Salva il file
fg.rss_file('feed.xml')
