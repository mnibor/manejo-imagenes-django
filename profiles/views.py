from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Profile

@login_required
def profile(request):
    return render(request, 'profiles/profile.html')
