import redis
import uuid
from datetime import datetime
import json
import os


# Connexion à Redis (par défaut sur localhost:6379)
r = redis.Redis(host='localhost', port=6379, decode_responses=True)

# Fonction pour créer un chirp
def post_chirp(username: str, text: str):
    chirp_id = str(uuid.uuid4())[:8]  # ID unique raccourci
    timestamp = datetime.utcnow().isoformat()

    # Stocker le chirp dans un hash
    r.hset(f"chirp:{chirp_id}", mapping={
        "user": username,
        "text": text,
        "timestamp": timestamp
    })

    # Ajouter ce chirp à la liste des derniers chirps
    r.lpush("chirps:latest", chirp_id)
    r.ltrim("chirps:latest", 0, 4)

    # Incrémenter le compteur de chirps de l'utilisateur
    r.incr(f"user:{username}:chirp_count")
    r.zincrby("ranking:chirps", 1, username)

# Fonction pour simuler ou définir le nombre de followers
def set_followers(username: str, count: int):
    r.set(f"user:{username}:followers_count", count)
    r.zadd("ranking:followers", {username: count})

# Afficher les top 5 utilisateurs (followers ou activité)
def print_top_users(key: str, title: str):
    print(f"\n🏆 {title}")
    top = r.zrevrange(key, 0, 4, withscores=True)
    for rank, (user, score) in enumerate(top, start=1):
        print(f"{rank}. {user} ({int(score)})")

def get_top_user_followers():
    top = r.zrevrange("ranking:followers", 0, 4, withscores=True)
    followers = []
    for rank, (user, score) in enumerate(top, start=1):
        followers.append((user, int(score)))
    return followers

# Afficher les top 5 utilisateurs (followers ou activité)
def get_top_user_chirps():
    top = r.zrevrange("ranking:chirps", 0, 4, withscores=True)
    followers = []
    for rank, (user, score) in enumerate(top, start=1):
        followers.append((user, int(score)))
    return followers

# Afficher les 5 derniers chirps
def print_latest_chirps():
    print("\n🕒 Derniers chirps :")
    chirp_ids = r.lrange("chirps:latest", 0, 4)
    for chirp_id in chirp_ids:
        chirp = r.hgetall(f"chirp:{chirp_id}")
        print(f"- [{chirp['timestamp']}] {chirp['user']}: {chirp['text']}")

# Afficher les 5 derniers chirps
def get_latest_chirps():
    chirp_ids = r.lrange("chirps:latest", 0, 4)
    chirps = []
    for chirp_id in chirp_ids:
        chirp = r.hgetall(f"chirp:{chirp_id}")
        chirps.append((chirp['timestamp'], chirp['user'], chirp['text']))
    return chirps

# --- Exemple d'utilisation ---
def import_tweets_from_jsonl(file_path: str):
    with open(file_path, "r", encoding="utf-8") as f:
        for line_number, line in enumerate(f, start=1):
            try:
                tweet = json.loads(line)
            except json.JSONDecodeError:
                print(f"❌ Erreur de parsing ligne {line_number}")
                continue

            # Ne traiter que les tweets en anglais
            if tweet.get("lang") != "en":
                continue

            user_info = tweet.get("user", {})
            if not user_info:
                continue

            username = user_info.get("screen_name", "unknown_user")
            text = tweet.get("text", "").strip()
            followers = user_info.get("followers_count", 0)
            timestamp = tweet.get("created_at")

            if not text or not timestamp:
                continue

            # Enregistrement du nombre de followers si non défini
            if not r.exists(f"user:{username}:followers_count"):
                set_followers(username, followers)

            # Publier le chirp
            post_chirp(username, text)

    print("✅ Importation terminée depuis :", file_path)

def import_all_jsonl_from_folder(folder_path: str):
    for filename in os.listdir(folder_path):
        if filename.endswith(".json"):
            full_path = os.path.join(folder_path, filename)
            print(f"\n📄 Traitement du fichier : {filename}")
            import_tweets_from_jsonl(full_path)
            
# --- Exécution principale ---
if __name__ == "__main__":
    r.flushall()

    # Spécifie ici le dossier contenant tous les fichiers JSON
    import_all_jsonl_from_folder("twitter")

    print_top_users("ranking:followers", "Top 5 par followers")
    print_top_users("ranking:chirps", "Top 5 par nombre de chirps")
    get_latest_chirps()