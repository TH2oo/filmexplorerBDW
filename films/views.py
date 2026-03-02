from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required

from .models import Film, WatchlistItem
from .forms import SignUpForm

def film_details(request, title):
    film = get_object_or_404(Film, title=title)
    in_watchlist = False
    if request.user.is_authenticated:
        in_watchlist = WatchlistItem.objects.filter(user=request.user, title=film.title).exists()

        if request.method == 'POST':
            action = request.POST.get('action')
            if action == 'add':
                WatchlistItem.objects.get_or_create(user=request.user, title=film.title)
            elif action == 'remove':
                WatchlistItem.objects.filter(user=request.user, title=film.title).delete()
            return redirect('film_details', title=film.title)

    return render(request, 'film_details.html', {
        'film': film,
        'in_watchlist': in_watchlist,
    })

def films_database():
    films = [
        "Inception", "Interstellar", "The Matrix", "Pulp Fiction", 
        "The Godfather", "The Dark Knight", "Schindler's List", 
        "The Lord of the Rings", "Fight Club", "Forrest Gump", 
        "The Empire Strikes Back", "Goodfellas", "The Silence of the Lambs", 
        "Seven", "The Usual Suspects", "Léon: The Professional", 
        "Saving Private Ryan", "The Green Mile", "Parasite", 
        "Spirited Away", "Interstellar", "Gladiator", "The Prestige"
    ]
    return films

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
    # Films de la BDD pas encore dans la watchlist de l'utilisateur
    watchlist_titles = items.values_list('title', flat=True)
    available_films = Film.objects.exclude(title__in=watchlist_titles).order_by('title')
    return render(request, "films_list.html", {"items": items, "available_films": available_films})


def film_list(request):
    html = """
    <html><body>
        <h1>Film Explorer</h1>
        <p>Explore films here!</p>
        <ul>
            <li>Inception</li>
            <li>The Matrix</li>
            <li>Interstellar</li>
        </ul>
    </body></html>
    """
    return HttpResponse(html)

def film_base(request):
    # On récupère TOUS les films de la base de données
    films_db = Film.objects.all() 
    
    # Si la base est vide, films_db sera une liste vide []
    return render(request, "films02_list.html", {"films": films_db})

def film_browse(request):
    films = films_database()
    return render(request, 'films_browse.html', {'films': films})

def login_view(request):
    form = AuthenticationForm()
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                auth_login(request, user)
                return redirect('welcome')
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    auth_logout(request)
    return redirect('login')

def welcome(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'welcome.html')

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('film_list_template')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})

def films05_list(request):
    films_db = Film.objects.all()
    return render(request, 'films05_list.html', {'films': films_db})


# Create your views here.
