from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Q
from datetime import datetime, date
from .models import Word, Game, Guess
from .forms import RegistrationForm
import random
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
import csv
from datetime import datetime, date, timedelta
from django.db.models import Count
from django.contrib.auth.models import User
from django.db.models import Prefetch
from django.shortcuts import render
# --- Auth views ---
def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            u = form.save(commit=False)
            pwd = form.cleaned_data['password']
            u.set_password(pwd)
            u.save()
            messages.success(request, "Registration successful. Please login.")
            return redirect('game:login')
    else:
        form = RegistrationForm()
    return render(request, 'game/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect('game:dashboard')
        else:
            messages.error(request, "Invalid credentials")
    return render(request, 'game/login.html')

def logout_view(request):
    auth_logout(request)
    return redirect('game:login')

# --- Helpers ---
def daily_games_count(user, for_date=None):
    if for_date is None:
        for_date = date.today()
    start = datetime.combine(for_date, datetime.min.time())
    end = datetime.combine(for_date, datetime.max.time())
    return Game.objects.filter(user=user, started_at__range=(start, end)).count()

def evaluate_guess(secret: str, guess: str):
    # both are 5-letter uppercase strings
    status = ['grey'] * 5
    secret_list = list(secret)
    guess_list = list(guess)
    # first pass: greens
    for i in range(5):
        if guess_list[i] == secret_list[i]:
            status[i] = 'green'
            secret_list[i] = None  # consume
            guess_list[i] = None
    # second pass: oranges
    for i in range(5):
        if guess_list[i] is not None and guess_list[i] in secret_list:
            status[i] = 'orange'
            # consume the matched letter in secret_list (first occurrence)
            idx = secret_list.index(guess_list[i])
            secret_list[idx] = None
    return status

# --- Game views ---
@login_required
def dashboard(request):
    # If user is admin/staff, show admin dashboard (two report buttons)
    if request.user.is_staff or request.user.is_superuser:
        return render(request, 'game/admin_dashboard.html')

    # Regular player dashboard
    recent = Game.objects.filter(user=request.user).order_by('-started_at')[:10]
    today_count = daily_games_count(request.user)
    return render(request, 'game/dashboard.html', {'recent': recent, 'today_count': today_count})

@login_required
def start_game(request):
    # enforce max 3 games per day
    if daily_games_count(request.user) >= 3:
        messages.error(request, "You have reached maximum 3 games today. Try tomorrow.")
        return redirect('game:dashboard')
    # pick a random word not previously attempted today (optional)
    word = random.choice(list(Word.objects.all()))
    game = Game.objects.create(user=request.user, word=word)
    return redirect('game:play', game_id=game.id)

@login_required
def play_game(request, game_id):
    game = get_object_or_404(Game, id=game_id, user=request.user)
    if game.finished:
        messages.info(request, "This game is finished.")
        return redirect('game:dashboard')

    if request.method == 'POST':
        guess_text = request.POST.get('guess', '').strip().upper()
        # validate input
        if len(guess_text) != 5 or not guess_text.isalpha():
            messages.error(request, "Please enter a 5-letter word (A-Z only).")
            return redirect('game:play', game_id=game.id)
        if game.guesses_used >= game.guesses_allowed:
            messages.error(request, "No more guesses allowed for this game.")
            return redirect('game:play', game_id=game.id)

        # evaluate
        secret = game.word.text
        status = evaluate_guess(secret, guess_text)
        Guess.objects.create(game=game, text=guess_text, status=status)
        game.guesses_used += 1
        # check win
        if guess_text == secret:
            game.win = True
            game.finished = True
            game.save()
            messages.success(request, "Congratulations! You guessed the word.")
            return redirect('game:dashboard')
        else:
            if game.guesses_used >= game.guesses_allowed:
                game.finished = True
                game.save()
                messages.info(request, f'Better luck next time! The word was {secret}.')
                return redirect('game:dashboard')
            game.save()
            return redirect('game:play', game_id=game.id)

    # build paired display data: list of list of (char, status)
    guesses = list(game.guesses.order_by('attempted_at'))
    guesses_display = []
    for g in guesses:
        # g.text is string length 5, g.status is list length 5
        pairs = []
        for idx, ch in enumerate(g.text):
            st = None
            try:
                st = g.status[idx]
            except Exception:
                st = 'grey'
            pairs.append((ch, st))
        guesses_display.append(pairs)

    return render(request, 'game/game.html', {
        'game': game,
        'guesses': guesses,            # kept in case you need it
        'guesses_display': guesses_display,
    })

# --- Admin reports ---
def is_admin(user):
    return user.is_staff or user.is_superuser

@staff_member_required
def admin_dashboard(request):
    return render(request, 'game/admin_dashboard.html')

from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
import csv
from datetime import datetime, date
from django.db.models import Count
from .models import Game

@staff_member_required
def report_day(request):
    # parse date param or use today
    d = request.GET.get('date')
    if d:
        report_date = datetime.strptime(d, '%Y-%m-%d').date()
    else:
        report_date = date.today()

    start = datetime.combine(report_date, datetime.min.time())
    end = datetime.combine(report_date, datetime.max.time())

    # games started that day with related user and word, and count guesses
    games_qs = Game.objects.filter(started_at__range=(start, end)) \
                .select_related('user', 'word') \
                .annotate(guesses_count=Count('guesses')) \
                .order_by('-started_at')

    users_count = games_qs.values('user').distinct().count()
    games_count = games_qs.count()
    correct_guesses = games_qs.filter(win=True).count()

    # CSV export: if ?export=csv&detail=1 produce detailed CSV otherwise aggregate
    if request.GET.get('export') == 'csv':
        detail = request.GET.get('detail') == '1'
        response = HttpResponse(content_type='text/csv')
        fname = f'report_day_{report_date}.csv'
        response['Content-Disposition'] = f'attachment; filename="{fname}"'
        writer = csv.writer(response)

        if detail:
            # header for detailed report per game
            writer.writerow(['game_id','username','word','started_at','guesses_count','win'])
            for g in games_qs:
                writer.writerow([
                    g.id,
                    g.user.username,
                    g.word.text if g.word else '',
                    g.started_at.isoformat(),
                    g.guesses_count,
                    'YES' if g.win else 'NO'
                ])
        else:
            # aggregated summary
            writer.writerow(['report_date', 'users_count', 'games_count', 'correct_guesses'])
            writer.writerow([report_date.isoformat(), users_count, games_count, correct_guesses])
        return response

    ctx = {
        'report_date': report_date,
        'users_count': users_count,
        'games_count': games_count,
        'correct_guesses': correct_guesses,
        'games': games_qs,
    }
    return render(request, 'game/reports_day.html', ctx)

@staff_member_required
def report_user(request):
    username = request.GET.get('username')
    report = None
    if username:
        try:
            u = User.objects.get(username=username)
        except User.DoesNotExist:
            messages.error(request, "User not found")
            return redirect('game:report_day')

        # get all games for the user (order desc)
        games = Game.objects.filter(user=u).order_by('-started_at') \
                 .prefetch_related('guesses')

        # build a simple report list
        report = []
        for g in games:
            report.append({
                'game_id': g.id,
                'date': g.started_at.date(),
                'words_tried': g.guesses.count(),   # guesses saved
                'correct': g.win,
            })

        # CSV export
        if request.GET.get('export') == 'csv':
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="report_user_{u.username}.csv"'
            writer = csv.writer(response)
            writer.writerow(['game_id','date','words_tried','correct'])
            for row in report:
                writer.writerow([row['game_id'], row['date'].isoformat(), row['words_tried'], row['correct']])
            return response

    return render(request, 'game/reports_user.html', {'report': report, 'username': username})
