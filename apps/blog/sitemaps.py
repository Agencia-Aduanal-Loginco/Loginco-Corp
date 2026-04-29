from django.contrib.sitemaps import Sitemap

from .models import Category, Post


class PostSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.7
    protocol = "https"

    def items(self):
        return Post.objects.filter(status=Post.STATUS_PUBLISHED).order_by("-published_at")

    def lastmod(self, obj):
        return obj.updated_at


class CategorySitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.5
    protocol = "https"

    def items(self):
        return (
            Category.objects.filter(
                posts__status=Post.STATUS_PUBLISHED
            )
            .distinct()
            .order_by("name")
        )

    def lastmod(self, obj):
        latest = obj.posts.filter(status=Post.STATUS_PUBLISHED).order_by("-updated_at").first()
        return latest.updated_at if latest else None
