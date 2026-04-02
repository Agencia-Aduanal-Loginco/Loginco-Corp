import logging
from django.utils import timezone

logger = logging.getLogger(__name__)


def publish_scheduled_posts():
    """
    Job APScheduler — corre cada minuto.
    Publica los Posts con status='scheduled' cuya published_at ya llegó.
    """
    from apps.blog.models import Post

    now = timezone.now()
    queryset = Post.objects.filter(status=Post.STATUS_SCHEDULED, published_at__lte=now)
    count = queryset.update(status=Post.STATUS_PUBLISHED)

    if count:
        logger.info("APScheduler: %d post(s) publicado(s) automáticamente.", count)
