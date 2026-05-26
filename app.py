from flask import Flask, request, render_template_string, redirect, url_for, session, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import json
import os
import webbrowser

app = Flask(__name__)
app.secret_key = 'ulrichteddyassoumou'  # Change pour une chaîne aléatoire plus tard

# Configuration Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'   # redirige ici si pas connecté
login_manager.login_message = "Veuillez vous connecter pour accéder à cette page."

# ------------------------------------------------------------
# Modèle utilisateur simple (juste l'admin pour l'instant)
# ------------------------------------------------------------
class User(UserMixin):
    def __init__(self, id, email, password_hash):
        self.id = id
        self.email = email
        self.password_hash = password_hash

# Simulons une "base de données" en mémoire avec un fichier JSON pour l'admin
USERS_FILE = 'users.json'

def charger_utilisateurs():
    if not os.path.exists(USERS_FILE):
        # Créer un admin par défaut (email: admin@teddymarket.com, mdp: admin123)
        default_password = generate_password_hash('admin237')
        users = [{"id": 1, "email": "admin@teddymarket.com", "password_hash": default_password}]
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(users, f, indent=2)
    with open(USERS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def sauvegarder_utilisateurs(users):
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, indent=2)

@login_manager.user_loader
def load_user(user_id):
    users = charger_utilisateurs()
    for u in users:
        if u['id'] == int(user_id):
            return User(u['id'], u['email'], u['password_hash'])
    return None

# ------------------------------------------------------------
# Gestion des services et commandes (inchangé)
# ------------------------------------------------------------
SERVICES_FILE = 'services.json'
COMMANDES_FILE = 'commandes.json'

def charger_services():
    if not os.path.exists(SERVICES_FILE):
        services_defaut = [
            {"nom": "🎨 Création de logo", "categorie": "Graphisme", "description": "Logo professionnel pour votre entreprise."},
            {"nom": "🎬 Montage vidéo", "categorie": "Audiovisuel", "description": "Montage de vos vidéos événementielles."},
            {"nom": "🎉 Organisation d'événements", "categorie": "Événementiel", "description": "Décoration, mise en place, recherche de salle pour vos anniversaires, mariages, etc."}
        ]
        with open(SERVICES_FILE, 'w', encoding='utf-8') as f:
            json.dump(services_defaut, f, indent=2)
    with open(SERVICES_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def sauvegarder_services(services):
    with open(SERVICES_FILE, 'w', encoding='utf-8') as f:
        json.dump(services, f, indent=2)

def charger_commandes():
    if not os.path.exists(COMMANDES_FILE):
        return []
    with open(COMMANDES_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def sauvegarder_commande(commande):
    commandes = charger_commandes()
    commandes.append(commande)
    with open(COMMANDES_FILE, 'w', encoding='utf-8') as f:
        json.dump(commandes, f, indent=2)

# ------------------------------------------------------------
# Templates HTML (inchangé, sauf le lien admin qu'on remplace par /login)
# ------------------------------------------------------------
HTML_INDEX = '''
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bôlô Market</title>
    <style>
        * { margin:0; padding:0; box-sizing:border-box; }
        body { font-family: 'Segoe UI', Arial, sans-serif; background: #f9f9f9; color: #333; }
        .header { background: linear-gradient(135deg, #1a5632, #2e7d32); color: white; text-align: center; padding: 30px 20px; }
        .header img { width: 80px; height: 80px; border-radius: 50%; object-fit: cover; border: 3px solid white; margin-bottom: 10px; }
        .header h1 { font-size: 28px; margin-bottom: 5px; }
        .header p { font-size: 14px; opacity: 0.9; }
        .container { max-width: 600px; margin: 20px auto; padding: 0 15px; }
        .service { background: white; padding: 20px; margin: 15px 0; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); border-left: 5px solid #2e7d32; }
        .service strong { font-size: 18px; color: #1a5632; }
        .service p { margin-top: 8px; color: #666; }
        form { background: white; padding: 25px; margin-top: 30px; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }
        form h2 { margin-bottom: 20px; color: #1a5632; }
        input, select, textarea { width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #ddd; border-radius: 8px; font-size: 16px; }
        button { background: #1a5632; color: white; padding: 14px; border: none; border-radius: 8px; font-size: 16px; cursor: pointer; width: 100%; margin-top: 10px; font-weight: bold; }
        button:hover { background: #2e7d32; }
        .footer { text-align: center; margin: 30px 0; color: #999; font-size: 14px; }
        .footer a { color: #1a5632; text-decoration: none; }
        .whatsapp-link { color: #25D366; font-weight: bold; }
    </style>
</head>
<body>
    <div class="header">
        <img src="/static/logo.png" alt="Logo" onerror="this.style.display='none'">
        <h1>Bôlô Market</h1>
        <p>Le professionnalisme et la compétence nous caractérisent</p>
    </div>

    <div class="container">
        <h2>🛠️ Services disponibles</h2>
        {% for service in services %}
        <div class="service">
            <strong>{{ service.nom }}</strong><br>
            <p>{{ service.description }}</p>
        </div>
        {% endfor %}

        <form method="POST" action="/commander">
            <h2>📩 Passer une commande</h2>
            <input type="text" name="nom" placeholder="Votre nom complet" required>
            <input type="text" name="telephone" placeholder="Votre numéro WhatsApp" required>
            <select name="service" required>
                <option value="">-- Choisissez un service --</option>
                {% for service in services %}
                <option value="{{ service.nom }}">{{ service.nom }}</option>
                {% endfor %}
            </select>
            <input type="text" name="budget" placeholder="Budget estimé (ex: 5000 FCFA)" required>
            <textarea name="details" placeholder="Décrivez votre besoin (date, détails supplémentaires)"></textarea>
            <button type="submit">Envoyer la commande</button>
        </form>
    </div>

    <div class="footer">
        <p>Besoin d'aide ? Contactez-moi directement sur <a href="https://wa.me/237657147497" class="whatsapp-link">WhatsApp</a></p>
        <p><a href="/login">Accès Administration</a></p>
    </div>
</body>
</html>
'''

HTML_CONFIRMATION = '''
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Commande envoyée - Bôlô Market</title>
    <style>
        body { font-family: Arial; background: #f9f9f9; text-align: center; padding: 50px 20px; }
        .box { background: white; max-width: 500px; margin: auto; padding: 40px; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
        h2 { color: #1a5632; }
        p { margin: 15px 0; color: #333; }
        .whatsapp { color: #25D366; font-weight: bold; text-decoration: none; }
        a { color: #1a5632; }
    </style>
</head>
<body>
    <div class="box">
        <h2>✅ Commande reçue avec succès !</h2>
        <p>Merci ! <strong>Nous vous contacterons le plus tôt possible sur WhatsApp</strong> pour confirmer et vous mettre en relation avec le prestataire.</p>
        <p>En attendant, vous pouvez discuter directement avec moi : <a href="https://wa.me/237657147497" class="whatsapp">WhatsApp</a></p>
        <a href="/">⬅ Retour à l'accueil</a>
    </div>
</body>
</html>
'''

HTML_LOGIN = '''
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Connexion Admin - Bôlô Market</title>
    <style>
        body { font-family: Arial; background: #f9f9f9; text-align: center; padding: 50px 20px; }
        .box { background: white; max-width: 400px; margin: auto; padding: 30px; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
        h2 { color: #1a5632; }
        input { width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #ddd; border-radius: 8px; }
        button { background: #1a5632; color: white; padding: 12px; border: none; border-radius: 8px; cursor: pointer; width: 100%; }
        .error { color: red; margin: 10px 0; }
    </style>
</head>
<body>
    <div class="box">
        <h2>Connexion administrateur</h2>
        {% with messages = get_flashed_messages() %}
          {% if messages %}
            <div class="error">{{ messages[0] }}</div>
          {% endif %}
        {% endwith %}
        <form method="POST">
            <input type="email" name="email" placeholder="Email admin" required>
            <input type="password" name="password" placeholder="Mot de passe" required>
            <button type="submit">Se connecter</button>
        </form>
        <p style="margin-top:15px;"><a href="/">Retour au site</a></p>
    </div>
</body>
</html>
'''

HTML_ADMIN = '''
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin - Bôlô Market</title>
    <style>
        body { font-family: Arial; margin: 20px; background: #f0f0f0; }
        table { width: 100%; background: white; border-collapse: collapse; }
        th, td { padding: 10px; border: 1px solid #ddd; text-align: left; }
        th { background: #1a5632; color: white; }
        form { background: white; padding: 20px; margin-top: 20px; border-radius: 8px; }
        input, textarea { width: 100%; padding: 10px; margin: 5px 0; }
        button { background: #1a5632; color: white; padding: 10px; border: none; cursor: pointer; }
        a { color: #1a5632; }
    </style>
</head>
<body>
    <h1>Panneau d'administration</h1>
    <p>Connecté en tant que {{ current_user.email }} | <a href="/logout">Se déconnecter</a></p>
    <h2>Liste des commandes</h2>
    {% if commandes %}
    <table>
        <tr><th>Nom</th><th>Téléphone</th><th>Service</th><th>Budget</th><th>Détails</th></tr>
        {% for c in commandes %}
        <tr>
            <td>{{ c.nom }}</td>
            <td>{{ c.telephone }}</td>
            <td>{{ c.service }}</td>
            <td>{{ c.budget }}</td>
            <td>{{ c.details }}</td>
        </tr>
        {% endfor %}
    </table>
    {% else %}
    <p>Aucune commande pour le moment.</p>
    {% endif %}

    <h2>Ajouter un nouveau service</h2>
    <form method="POST" action="/admin/ajouter_service">
        <input type="text" name="nom" placeholder="Nom du service" required>
        <input type="text" name="categorie" placeholder="Catégorie" required>
        <textarea name="description" placeholder="Description courte"></textarea>
        <button type="submit">Ajouter le service</button>
    </form>
    <p><a href="/">Retour au site</a></p>
</body>
</html>
'''
# ------------------------------------------------------------
# Routes publiques
# ------------------------------------------------------------
@app.route('/')
def index():
    services = charger_services()
    return render_template_string(HTML_INDEX, services=services)

@app.route('/commander', methods=['POST'])
def commander():
    commande = {
        "nom": request.form.get('nom'),
        "telephone": request.form.get('telephone'),
        "service": request.form.get('service'),
        "budget": request.form.get('budget'),
        "details": request.form.get('details')
    }
    sauvegarder_commande(commande)
    return render_template_string(HTML_CONFIRMATION)

# ------------------------------------------------------------
# Routes d'authentification
# ------------------------------------------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin'))
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        users = charger_utilisateurs()
        for u in users:
            if u['email'] == email and check_password_hash(u['password_hash'], password):
                user = User(u['id'], u['email'], u['password_hash'])
                login_user(user)
                flash('Connexion réussie.', 'success')
                next_page = request.args.get('next')
                return redirect(next_page or url_for('admin'))
        flash('Email ou mot de passe incorrect.', 'danger')
    return render_template_string(HTML_LOGIN)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# ------------------------------------------------------------
# Routes protégées (admin)
# ------------------------------------------------------------
@app.route('/admin')
@login_required
def admin():
    commandes = charger_commandes()
    services = charger_services()
    return render_template_string(HTML_ADMIN, commandes=commandes, services=services)

@app.route('/admin/ajouter_service', methods=['POST'])
@login_required
def ajouter_service():
    services = charger_services()
    nouveau = {
        "nom": request.form.get('nom'),
        "categorie": request.form.get('categorie'),
        "description": request.form.get('description')
    }
    services.append(nouveau)
    sauvegarder_services(services)
    return redirect(url_for('admin'))

# ------------------------------------------------------------
# Sécurité supplémentaire : empêcher l'accès direct aux fichiers JSON
# ------------------------------------------------------------
@app.route('/<filename>.json')
def bloquer_json(filename):
    # Empêcher le téléchargement des fichiers de données
    return "Accès interdit", 403

# ------------------------------------------------------------
# Démarrage
# ------------------------------------------------------------
if __name__ == '__main__':
    charger_services()
    charger_commandes()
    charger_utilisateurs()  # crée l'admin par défaut si besoin
    # En local, ouverture automatique
    if not os.environ.get('RENDER'):
        webbrowser.open('http://127.0.0.1:5000')
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)