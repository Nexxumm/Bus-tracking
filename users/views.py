from django.core.mail import send_mail
from django.shortcuts import render,redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.utils import timezone
from Bus.models import *
from Bus.services import generate_otp, verify_otp_for_user
from Dvm import settings
from .forms import *
from django.contrib.auth.decorators import login_required

def register(request):
    if request.method == 'POST':

        form = UserRegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password1']

            if User.objects.filter(username=username).exists():
                messages.error(request, f'Username:{username} already exists')
                return render(request, 'users/register.html', {'form': UserRegisterForm()})

            user = User.objects.create_user(username=username, email=email, password=password)
            user.is_active = False
            email_otp = generate_otp()
            user.profile.email_otp = email_otp
            user.profile.save()
            user.save()

            send_mail(
                'Email Verification OTP',
                f'Your OTP for email verification is: {email_otp}',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )


            messages.success(request, f'Email sent to {email} for {username}, Verify')
            return redirect('verify_otp', user_id=user.id)

    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})


def verify_otp(request, user_id):
    user = User.objects.get(id=user_id)

    if request.method == 'POST':
        email_otp = request.POST['email_otp']


        if verify_otp_for_user(email_otp, user.profile.email_otp) :
            user.is_active = True
            user.profile.email_otp = None
            user.save()
            messages.success(request,  f'email verified , you may now login')
            return redirect('login')
        else:
            messages.error(request, f'OTP is invalid')
            return render(request, 'users/verify_otp.html', {'error': 'Invalid OTP'})

    return render(request, 'users/verify_otp.html')

def login(request):
    return render(request, 'users/login.html')

def logout(request):
    return render(request, 'users/logout.html')

@login_required(login_url='login')
def profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    context = {
        'wallet_balance': profile.wallet_balance,

        'upcoming_trips' : request.user.bookings.filter(
            travel_date__gte=timezone.now().date(),
            status = 'Accepted',
        ),
        'past_trips' : request.user.bookings.filter(
            travel_date__lte=timezone.now().date(),
        )
    }


    return render(request, 'users/profile.html', context)


@login_required
def wallet_topup(request):
    if request.method == 'POST':
        form = WalletTopupForm(request.POST , user=request.user)
        if form.is_valid():
            request.user.profile.wallet_balance += form.cleaned_data['amount']
            request.user.profile.save()
            return redirect('profile')
    else:
        form = WalletTopupForm(user=request.user)

    return render(request, 'users/wallet_topup.html', {'form': form})
