from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from Bus.models import Profile

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

def save_profile(sender, instance, **kwargs):
    instance.profile.save()

@receiver(post_save, sender=User)
def send_verification_email(sender, instance, created, **kwargs):
    if created:
        otp = OTP.objects.create(
            user=instance,
            secret=pyotp.random_base32(),
            expires_at=timezone.now() + timezone.timedelta(minutes=5)
        )
        instance.email_user(
            subject='Verify Your Email',
            message=f'Your OTP is: {otp.generate_otp()}'
        )