from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Comment


@receiver(post_save, sender=Comment)
def notify_pending_comment(sender, instance, created, **kwargs):
    if created and not instance.is_approved:
        send_mail("New comment awaiting approval", f"A new comment was left on {instance.post.title}.", "noreply@devfolio.local", ["owner@devfolio.local"], fail_silently=True)
