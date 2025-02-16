import pyotp
from allauth.socialaccount.signals import social_account_added
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.utils import timezone
from Bus.models import Profile


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

def save_profile(sender, instance, **kwargs):
    instance.profile.save()




@receiver(social_account_added)
def create_google_profile(request, sociallogin, **kwargs):
    user = sociallogin.user

    profile, created = Profile.objects.get_or_create(user=user)
    profile.google_id = sociallogin.account.uid
    profile.save()
    if not user.email:
        user.email = sociallogin.extra_data.get('email')
        user.save()