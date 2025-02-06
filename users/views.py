from django.shortcuts import render,redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.utils import timezone
from Bus.models import Booking
from .forms import *
from django.contrib.auth.decorators import login_required

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}, you are now able to log in.')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})

def login(request):
    return render(request, 'users/login.html')
@login_required(login_url='login')
def profile(request):

    context = {
        'upcoming_trips' : request.user.Bookings.filter(
            travel_date__gte=timezone.now().date(),
            status = 'Accepted',
        ),
        'past_trips' : request.user.Bookings.filter(
            travel_date__lte=timezone.now().date(),
        )
    }


    return render(request, 'users/profile.html', context)


@login_required
def wallet_topup(request):
    if request.method == 'POST':
        form = WalletTopupForm(request.POST , user=request.user)
        if form.is_valid():
            request.user.wallet_balance += form.cleaned_data['amount']
            request.user.save()
            return redirect('dashboard')
    else:
        form = WalletTopupForm(user=request.user)

    return render(request, 'accounts/wallet_topup.html', {'form': form})
