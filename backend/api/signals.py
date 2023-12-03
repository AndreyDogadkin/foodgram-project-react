# flake8: noqa
from django.db.models.signals import post_delete
from django.dispatch.dispatcher import receiver

from recipes.models import Recipe


@receiver(post_delete, sender=Recipe)
def del_image(sender, instance: Recipe, *args, **kwargs):
    if instance.image.name:
        instance.image.delete(False)
