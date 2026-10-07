"""
Tests de humo para las páginas estáticas.
"""

from django.test import TestCase
from django.urls import reverse


class PagesSmokeTest(TestCase):
    def test_home_returns_200(self):
        response = self.client.get(reverse("pages:home"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pages/home.html")

    def test_about_returns_200(self):
        response = self.client.get(reverse("pages:about"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pages/about.html")
        self.assertContains(response, "img/about-team-480.webp")
        self.assertContains(response, "img/about-team-800.webp")
        self.assertContains(response, "img/about-team-800.jpg")
        self.assertNotContains(response, "images.unsplash.com")

    def test_contact_returns_200(self):
        response = self.client.get(reverse("pages:contact"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pages/contact.html")

    def test_robots_txt_returns_correct_content(self):
        response = self.client.get(reverse("pages:robots_txt"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/plain; charset=utf-8")
        content = response.content.decode()
        self.assertIn("User-agent: *", content)
        self.assertIn("Disallow: /admin/", content)
        self.assertIn("Sitemap:", content)


class GoneRoutesTest(TestCase):
    """
    Verifica que las rutas heredadas devuelvan 410 Gone.
    """
    def test_gone_routes_return_410(self):
        routes = ["/shopping/", "/authentic/", "/shop/", "/header.php", "/https:/"]
        for route in routes:
            response = self.client.get(route)
            self.assertEqual(response.status_code, 410, f"Route {route} should return 410")


class PublicRoutesTest(TestCase):
    """
    Verifica que las rutas públicas devuelvan 200 OK.
    """
    def test_public_routes_return_200(self):
        routes = [
            reverse("pages:home"),
            reverse("pages:about"),
            reverse("pages:contact"),
            reverse("services:index"),
            reverse("blog:post_list"),
            "/sitemap.xml"
        ]
        for route in routes:
            response = self.client.get(route)
            self.assertEqual(response.status_code, 200, f"Route {route} should return 200")


class ServicesPageTest(TestCase):
    def test_services_returns_200(self):
        response = self.client.get(reverse("services:index"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "services/index.html")


class SitemapTest(TestCase):
    def test_sitemap_returns_200(self):
        response = self.client.get("/sitemap.xml")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"urlset", response.content)
