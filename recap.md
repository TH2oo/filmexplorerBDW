# 📚 Récap complet – Projet FilmExplorer (Django)

Ce document résume **toutes les tâches** réalisées sur le projet, les problèmes rencontrés et les solutions apportées. L'objectif est de te permettre de comprendre et d'apprendre chaque concept Django utilisé.

---

## Table des matières

1. [Architecture du projet](#1-architecture-du-projet)
2. [Correction du cache CSS](#2-correction-du-cache-css)
3. [Correction d'URL (NoReverseMatch)](#3-correction-durl-noreversematch)
4. [Système d'authentification (login/logout)](#4-système-dauthentification-loginlogout)
5. [Page d'inscription (signup)](#5-page-dinscription-signup)
6. [Page d'accueil + Navbar conditionnelle](#6-page-daccueil--navbar-conditionnelle)
7. [Modèle Watchlist (par utilisateur)](#7-modèle-watchlist-par-utilisateur)
8. [Popup modale avec films de la BDD](#8-popup-modale-avec-films-de-la-bdd)
9. [Page détails d'un film (revamp complet)](#9-page-détails-dun-film-revamp-complet)
10. [CSS moderne avec animations](#10-css-moderne-avec-animations)

---

## 1. Architecture du projet

```
filmexplorer/              ← Dossier de configuration Django
    settings.py            ← Paramètres globaux (INSTALLED_APPS, DB, etc.)
    urls.py                ← Routes principales du projet
films/                     ← Application Django "films"
    models.py              ← Modèles de données (Film, WatchlistItem)
    views.py               ← Logique des vues (fonctions qui répondent aux requêtes)
    forms.py               ← Formulaires personnalisés (SignUpForm)
    admin.py               ← Enregistrement des modèles dans l'admin Django
    templates/             ← Fichiers HTML (templates Django)
    static/css/            ← Fichiers CSS
    migrations/            ← Fichiers de migration de la BDD
```

### Concepts clés :
- **`settings.py`** : fichier central de configuration. `INSTALLED_APPS` liste les apps activées.
- **`urls.py`** : associe une URL à une vue (fonction Python).
- **`views.py`** : contient les fonctions qui traitent les requêtes HTTP et renvoient des réponses.
- **`models.py`** : définit la structure des tables en BDD avec des classes Python.
- **`templates/`** : fichiers HTML avec la syntaxe `{% %}` et `{{ }}` de Django.

---

## 2. Correction du cache CSS

### Problème
Les modifications CSS n'apparaissaient pas dans le navigateur.

### Cause
Le navigateur **met en cache** les fichiers statiques (CSS, JS, images). Même après modification du fichier, le navigateur utilise l'ancienne version en cache.

### Solution
Faire un **rechargement forcé** dans le navigateur :
- **Ctrl + Shift + R** (Linux/Windows)
- **Cmd + Shift + R** (Mac)

### Alternative technique (cache-busting)
On peut ajouter un paramètre de version dans le lien CSS :
```html
<!-- Avant -->
<link rel="stylesheet" href="{% static 'css/style.css' %}">

<!-- Après (avec cache-busting) -->
<link rel="stylesheet" href="{% static 'css/style.css' %}?v=2">
```
À chaque modification, on incrémente le numéro. Le navigateur voit une "nouvelle" URL et re-télécharge le fichier.

---

## 3. Correction d'URL (NoReverseMatch)

### Problème
```
NoReverseMatch at /films05/
Reverse for 'film_detail' not found.
```

### Cause
Dans le template `films05_list.html`, on utilisait `{% url 'film_detail' %}` mais le nom déclaré dans `urls.py` était `film_details` (avec un **s**).

### Leçon Django : le système d'URLs

```python
# urls.py
path('films/<str:title>/', film_details, name='film_details')
#                                              ^^^^^^^^^^^^
#                              Ce "name" est utilisé dans les templates
```

```html
<!-- Template -->
{% url 'film_details' title=film.title %}
<!--   ^^^^^^^^^^^^^  Ce nom DOIT correspondre exactement -->
```

### Règle
Le `name=` dans `path()` et le nom dans `{% url '...' %}` doivent être **identiques**. Une simple faute de frappe provoque `NoReverseMatch`.

---

## 4. Système d'authentification (login/logout)

### Problème initial
```
TypeError: login() missing 1 required positional argument: 'user'
```

### Cause (piège classique !)
```python
from django.contrib.auth import login  # ← Importe la fonction "login" de Django

def login(request):  # ← ÉCRASE la fonction importée !
    ...
    login(request, user)  # ← Appelle CETTE fonction, pas celle de Django !
```

La vue `login` avait le **même nom** que la fonction `django.contrib.auth.login`. Python remplace l'import par la définition locale.

### Solution
**Renommer l'import** avec un alias :
```python
from django.contrib.auth import login as auth_login, logout as auth_logout

def login_view(request):  # ← Nom différent de l'import
    form = AuthenticationForm()
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                auth_login(request, user)  # ← Utilise l'alias
                return redirect('welcome')
    return render(request, 'login.html', {'form': form})
```

### Concepts clés :
- **`AuthenticationForm`** : formulaire Django intégré pour le login (username + password).
- **`authenticate()`** : vérifie les identifiants en BDD, retourne le `User` ou `None`.
- **`auth_login(request, user)`** : crée la session utilisateur (cookie de session).
- **`auth_logout(request)`** : détruit la session.
- **`redirect('nom_url')`** : redirige vers une URL nommée.

### La vue logout :
```python
def logout_view(request):
    auth_logout(request)      # Détruit la session
    return redirect('login')  # Redirige vers la page de connexion
```

---

## 5. Page d'inscription (signup)

### Formulaire personnalisé (`forms.py`)
```python
from django.contrib.auth.forms import UserCreationForm

class SignUpForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        fields = UserCreationForm.Meta.fields + ("email",)
```

### Concepts :
- **`UserCreationForm`** : formulaire Django intégré (username, password1, password2).
- **`class Meta`** : configuration du formulaire. On hérite de `UserCreationForm.Meta` et on ajoute le champ `email`.
- **Héritage** : `SignUpForm` hérite de `UserCreationForm`, donc on récupère toute la logique de validation (mot de passe trop court, etc.).

### Vue signup :
```python
def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()              # Crée l'utilisateur en BDD
            auth_login(request, user)       # Connecte automatiquement
            return redirect('film_list_template')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})
```

### Pattern important : GET vs POST
```
1. L'utilisateur arrive sur /signup/ → GET → on affiche le formulaire vide
2. L'utilisateur remplit et soumet → POST → on valide et crée le compte
3. Si erreurs → on ré-affiche le formulaire avec les erreurs
4. Si OK → on redirige
```

Ce pattern **GET/POST** est utilisé dans presque toutes les vues avec formulaire en Django.

---

## 6. Page d'accueil + Navbar conditionnelle

### Page d'accueil (`welcome`)
```python
def welcome(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'welcome.html')
```

`request.user` est **toujours disponible** dans Django. Si l'utilisateur n'est pas connecté, `request.user` est un `AnonymousUser` et `.is_authenticated` vaut `False`.

### Navbar conditionnelle (`base.html`)
```html
{% if user.is_authenticated %}
    <span class="nav-user">👤 {{ user.username }}</span>
    <a href="{% url 'logout' %}" class="nav-logout">Déconnexion</a>
{% else %}
    <a href="{% url 'login' %}" class="nav-login">Connexion</a>
{% endif %}
```

### Concepts :
- **`{% if %}`** : condition dans un template Django.
- **`{{ user.username }}`** : affiche le nom de l'utilisateur connecté.
- **`user`** est automatiquement disponible dans tous les templates grâce au context processor `django.contrib.auth.context_processors.auth` (activé par défaut).
- **Template inheritance** : `{% extends "base.html" %}` et `{% block content %}` permettent d'avoir un layout commun (navbar, footer) sur toutes les pages.

---

## 7. Modèle Watchlist (par utilisateur)

### Le modèle (`models.py`)
```python
class WatchlistItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='watchlist')
    title = models.CharField(max_length=200)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-added_at']
        unique_together = ['user', 'title']
```

### Concepts clés :

#### ForeignKey (clé étrangère)
```python
user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='watchlist')
```
- Chaque `WatchlistItem` est lié à **un** `User`.
- `on_delete=models.CASCADE` : si l'utilisateur est supprimé, ses items de watchlist le sont aussi.
- `related_name='watchlist'` : permet d'accéder aux items depuis l'utilisateur : `user.watchlist.all()`.

#### unique_together
```python
unique_together = ['user', 'title']
```
Un même utilisateur ne peut pas ajouter deux fois le même film. La BDD refuse le doublon.

#### auto_now_add
```python
added_at = models.DateTimeField(auto_now_add=True)
```
La date est automatiquement remplie à la **création** de l'objet.

#### ordering
```python
ordering = ['-added_at']
```
Les résultats sont triés par date d'ajout décroissante par défaut (`-` = descendant).

### Migrations
Après avoir modifié `models.py`, il faut créer et appliquer les migrations :
```bash
python manage.py makemigrations   # Génère le fichier de migration
python manage.py migrate          # Applique les changements à la BDD
```

**Important** : ne jamais modifier la BDD directement. Toujours passer par les migrations.

---

## 8. Popup modale avec films de la BDD

### Vue (`views.py`)
```python
def film_list_template(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.method == "POST":
        action = request.POST.get("action")
        title = request.POST.get("film_title", "").strip()

        if action == "add" and title:
            WatchlistItem.objects.get_or_create(user=request.user, title=title)
        elif action == "remove":
            item_id = request.POST.get("item_id")
            WatchlistItem.objects.filter(id=item_id, user=request.user).delete()

        return redirect('film_list_template')

    items = WatchlistItem.objects.filter(user=request.user)
    watchlist_titles = items.values_list('title', flat=True)
    available_films = Film.objects.exclude(title__in=watchlist_titles).order_by('title')
    return render(request, "films_list.html", {"items": items, "available_films": available_films})
```

### Concepts ORM (Object-Relational Mapping) :

```python
# Filtrer : récupère les items de l'utilisateur connecté
items = WatchlistItem.objects.filter(user=request.user)

# values_list : récupère seulement les titres (pas les objets complets)
watchlist_titles = items.values_list('title', flat=True)
# Résultat : ['Inception', 'Interstellar', ...]

# exclude : récupère les films qui NE SONT PAS dans la liste
available_films = Film.objects.exclude(title__in=watchlist_titles)
# → Films de la BDD que l'utilisateur n'a pas encore ajoutés

# get_or_create : crée l'objet s'il n'existe pas, sinon le récupère
WatchlistItem.objects.get_or_create(user=request.user, title=title)
# Retourne (objet, created) → created est True/False
```

### Pattern PRG (Post/Redirect/Get)
```python
if request.method == "POST":
    # ... traiter le formulaire ...
    return redirect('film_list_template')  # ← Redirect après POST
```
Après un POST, on **redirige** (code 302) au lieu de rendre directement la page. Cela évite qu'un rechargement de page (F5) re-soumette le formulaire.

### Modale HTML/CSS (sans JavaScript de bibliothèque)
```html
<!-- Bouton qui ouvre la modale -->
<button onclick="document.getElementById('addModal').style.display='flex'">
    ➕ Ajouter un film
</button>

<!-- La modale (cachée par défaut) -->
<div id="addModal" class="modal-overlay" style="display:none">
    <div class="modal-card">
        <!-- Contenu -->
        <button onclick="document.getElementById('addModal').style.display='none'">
            ✕ Fermer
        </button>
    </div>
</div>
```

### Recherche/filtre en JavaScript (côté client)
```javascript
function filterFilms() {
    const query = document.getElementById('filmSearch').value.toLowerCase();
    document.querySelectorAll('.film-option').forEach(item => {
        // Affiche/masque chaque film selon le texte tapé
        item.style.display = item.textContent.toLowerCase().includes(query) ? '' : 'none';
    });
}
```

---

## 9. Page détails d'un film (revamp complet)

### Vue avec `get_object_or_404`
```python
def film_details(request, title):
    film = get_object_or_404(Film, title=title)
    # ...
```

#### `get_object_or_404(Model, **kwargs)`
- Cherche un objet en BDD correspondant aux critères.
- Si trouvé → retourne l'objet.
- Si non trouvé → lève une erreur **404 Not Found** automatiquement.
- Beaucoup plus propre que :
```python
try:
    film = Film.objects.get(title=title)
except Film.DoesNotExist:
    raise Http404
```

### URL avec paramètre dynamique
```python
# urls.py
path('films/<str:title>/', film_details, name='film_details')
```
- `<str:title>` capture une partie de l'URL et la passe en argument à la vue.
- Exemple : `/films/Inception/` → `film_details(request, title="Inception")`

### Template avec conditions
```html
{% if user.is_authenticated %}
    {% if in_watchlist %}
        <form method="post">
            {% csrf_token %}
            <input type="hidden" name="action" value="remove">
            <button type="submit">Retirer de ma watchlist</button>
        </form>
    {% else %}
        <form method="post">
            {% csrf_token %}
            <input type="hidden" name="action" value="add">
            <button type="submit">Ajouter à ma watchlist</button>
        </form>
    {% endif %}
{% endif %}
```

#### `{% csrf_token %}`
Obligatoire dans tout formulaire POST en Django. C'est une protection contre les attaques **CSRF** (Cross-Site Request Forgery). Django vérifie que le formulaire vient bien de votre site.

---

## 10. CSS moderne avec animations

### Animations CSS (`@keyframes`)
```css
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(20px); }
    to   { opacity: 1; transform: translateY(0); }
}

.detail-container {
    animation: fadeIn 0.6s ease-out;
}
```
- `@keyframes` définit une animation étape par étape.
- `animation: nom durée timing;` applique l'animation.

### Dégradés (`linear-gradient`)
```css
.detail-banner {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
```
Crée un fond qui passe progressivement d'une couleur à une autre.

### Transitions au survol
```css
.info-item:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 15px rgba(0,0,0,0.15);
}
```
- `transform: translateY(-2px)` : déplace l'élément vers le haut.
- `transition: all 0.3s ease` (défini sur l'élément) : rend le changement progressif.

### Variables CSS (bonnes pratiques)
```css
:root {
    --primary-color: #667eea;
    --border-radius: 12px;
}

.card {
    border-radius: var(--border-radius);
    background: var(--primary-color);
}
```
Les variables permettent de changer un style à un seul endroit et que ça se propage partout.

---

## Résumé des fichiers modifiés/créés

| Fichier | Action | Description |
|---------|--------|-------------|
| `films/models.py` | Modifié | Ajout du modèle `WatchlistItem` |
| `films/views.py` | Modifié | Toutes les vues (login, logout, signup, welcome, watchlist, détails) |
| `films/forms.py` | Créé | `SignUpForm` pour l'inscription |
| `films/admin.py` | Modifié | Enregistrement de `Film` et `WatchlistItem` |
| `filmexplorer/urls.py` | Modifié | Toutes les routes du projet |
| `films/templates/base.html` | Modifié | Navbar avec login/logout conditionnel |
| `films/templates/login.html` | Modifié | Page de connexion |
| `films/templates/signup.html` | Créé | Page d'inscription |
| `films/templates/welcome.html` | Créé | Page d'accueil |
| `films/templates/films_list.html` | Modifié | Watchlist avec modale d'ajout |
| `films/templates/film_details.html` | Modifié | Page détails d'un film |
| `films/templates/films05_list.html` | Modifié | Correction URL `film_details` |
| `films/static/css/filmDetails.css` | Modifié | CSS animé pour les détails film |
| `films/static/css/films.css` | Modifié | CSS pour la watchlist + modale |
| `films/static/css/style.css` | Modifié | CSS global + navbar |
| `films/static/css/signup.css` | Créé | CSS pour la page inscription |
| `films/migrations/0002_*` | Créé | Migration pour `WatchlistItem` |

---

## Commandes Django utiles

```bash
# Lancer le serveur de développement
python manage.py runserver

# Créer les migrations après modification de models.py
python manage.py makemigrations

# Appliquer les migrations à la BDD
python manage.py migrate

# Créer un super-utilisateur (accès admin)
python manage.py createsuperuser

# Ouvrir le shell Django (pour tester des requêtes ORM)
python manage.py shell

# Vérifier les problèmes du projet
python manage.py check
```

---

## Pièges courants à éviter

1. **Nommage des imports** : ne jamais donner à une vue le même nom qu'une fonction importée (`login`, `logout`).
2. **`{% csrf_token %}`** : obligatoire dans tout `<form method="post">`, sinon erreur 403.
3. **Cache navigateur** : Ctrl+Shift+R pour forcer le rechargement des fichiers statiques.
4. **`NoReverseMatch`** : vérifier que le `name=` dans `urls.py` correspond exactement au `{% url '...' %}`.
5. **Migrations oubliées** : après toute modification de `models.py`, faire `makemigrations` + `migrate`.
6. **`redirect()` après POST** : toujours rediriger après un POST pour éviter la re-soumission.
