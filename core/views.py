import json
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.utils.dateparse import parse_datetime
from .models import GameScore

def register_view(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('game')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

@login_required
def game_view(request):
    # Trang này sẽ chứa iframe game
    return render(request, 'game_container.html')

@login_required
def save_score_api(request):
    """API nhận dữ liệu từ Game (JS) gửi về"""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            score = data.get('score')
            start_time = data.get('start_time') # ISO format string
            end_time = data.get('end_time')     # ISO format string
            duration = data.get('duration')
            game_mode = data.get('game_mode', 'EASY')
            
            GameScore.objects.create(
                user=request.user,
                score=score,
                start_time=parse_datetime(start_time),
                end_time=parse_datetime(end_time),
                duration_seconds=duration,
                game_mode=game_mode
            )
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'invalid method'}, status=405)