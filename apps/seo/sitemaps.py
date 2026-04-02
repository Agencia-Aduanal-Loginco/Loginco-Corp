from django.contrib.sitemaps import Sitemap
from django.urls import reverse


class StaticViewSitemap(Sitemap):
    priority = 1.0
    changefreq = "weekly"
    protocol = "https"

    def items(self):
        return ["pages:home", "pages:about", "pages:contact", "services:index"]

    def location(self, item):
        return reverse(item)
