from django.contrib.sitemaps import Sitemap
from django.urls import reverse

_STATIC_PAGES = [
    ("pages:home",     1.0, "daily"),
    ("services:index", 0.9, "weekly"),
    ("blog:post_list", 0.8, "daily"),
    ("pages:about",    0.5, "monthly"),
    ("pages:contact",  0.5, "monthly"),
]


class StaticViewSitemap(Sitemap):
    protocol = "https"

    def items(self):
        return _STATIC_PAGES

    def location(self, item):
        url_name, _priority, _changefreq = item
        return reverse(url_name)

    def priority(self, item):
        return item[1]

    def changefreq(self, item):
        return item[2]
