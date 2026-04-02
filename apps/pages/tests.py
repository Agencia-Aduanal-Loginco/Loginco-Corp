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
