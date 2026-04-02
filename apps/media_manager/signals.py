import logging
from django.db.models.signals import post_save
from django.dispatch import receiver

logger = logging.getLogger(__name__)


@receiver(post_save, sender="media_manager.MediaFile")
def pre_generate_webp_specs(sender, instance, created, **kwargs):
    """
    Pre-genera las versiones WebP al subir una imagen nueva.
    imagekit genera los archivos de forma lazy; este signal los fuerza
    para que estén disponibles de inmediato sin esperar la primera visita.
    """
    if not created or not instance.is_image or not instance.image:
        return

    specs = [instance.image_thumb_webp, instance.image_md_webp, instance.image_lg_webp]
    for spec in specs:
        try:
            spec.generate()
        except Exception as exc:
            logger.warning("WebP pre-generation failed for MediaFile %s: %s", instance.pk, exc)
