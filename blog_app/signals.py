from django.db.models import signals
from django.dispatch import receiver
from django.contrib.auth.models import User

from blog_app.models import Profile


@receiver(signals.post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(
            user=instance,
            username=instance.username,
        )
