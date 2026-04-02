"""
Tests básicos para la app blog.
Cubre: modelos, vistas públicas y sitemap.
"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Category, Post, SiteTarget, Tag

User = get_user_model()


def make_user(**kwargs):
    defaults = {"username": "testuser", "password": "pass1234"}
    defaults.update(kwargs)
    return User.objects.create_user(**defaults)


def make_site_target(**kwargs):
    defaults = {
        "name": "Agencia Aduanal",
        "domain": "https://agencia-aduanal.loginco.com.mx",
        "slug": "agencia-aduanal",
    }
    defaults.update(kwargs)
    return SiteTarget.objects.create(**defaults)


def make_category(**kwargs):
    defaults = {"name": "Aduanas", "slug": "aduanas"}
    defaults.update(kwargs)
    return Category.objects.create(**defaults)


def make_post(author, category, **kwargs):
    defaults = {
        "title": "Guía rápida de importación",
        "slug": "guia-rapida-importacion",
        "excerpt": "Todo lo que necesitas saber para importar.",
        "body": "<p>Contenido del artículo.</p>",
        "category": category,
        "author": author,
        "status": Post.STATUS_PUBLISHED,
        "published_at": timezone.now(),
    }
    defaults.update(kwargs)
    post = Post.objects.create(**defaults)
    return post


# ---------------------------------------------------------------------------
# Modelo
# ---------------------------------------------------------------------------

class PostModelTest(TestCase):

    def setUp(self):
        self.user = make_user()
        self.category = make_category()
        self.post = make_post(self.user, self.category)

    def test_str_returns_title(self):
        self.assertEqual(str(self.post), self.post.title)

    def test_reading_time_calculated_on_save(self):
        # 200 palabras → 1 minuto
        body = "<p>" + "palabra " * 200 + "</p>"
        self.post.body = body
        self.post.save()
        self.assertEqual(self.post.reading_time, 1)

    def test_published_at_set_on_publish(self):
        post = Post.objects.create(
            title="Nuevo post",
            slug="nuevo-post",
            excerpt="Excerpt.",
            body="<p>Body.</p>",
            category=self.category,
            author=self.user,
            status=Post.STATUS_PUBLISHED,
        )
        self.assertIsNotNone(post.published_at)

    def test_get_absolute_url(self):
        url = self.post.get_absolute_url()
        self.assertIn(self.post.slug, url)

    def test_effective_meta_title_fallback_to_title(self):
        self.assertEqual(self.post.get_effective_meta_title(), self.post.title)

    def test_effective_meta_title_uses_meta_title_when_set(self):
        self.post.meta_title = "SEO Title"
        self.post.save()
        self.assertEqual(self.post.get_effective_meta_title(), "SEO Title")


class CategoryModelTest(TestCase):

    def test_str_returns_name(self):
        cat = make_category()
        self.assertEqual(str(cat), cat.name)

    def test_get_absolute_url(self):
        cat = make_category()
        url = cat.get_absolute_url()
        self.assertIn(cat.slug, url)


# ---------------------------------------------------------------------------
# Vistas
# ---------------------------------------------------------------------------

class PostListViewTest(TestCase):

    def setUp(self):
        self.user = make_user()
        self.category = make_category()
        self.url = reverse("blog:post_list")

    def test_empty_list_returns_200(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_only_published_posts_appear(self):
        published = make_post(self.user, self.category, title="Publicado", slug="publicado")
        draft = make_post(
            self.user, self.category,
            title="Borrador", slug="borrador",
            status=Post.STATUS_DRAFT,
        )
        response = self.client.get(self.url)
        posts = list(response.context["posts"])
        self.assertIn(published, posts)
        self.assertNotIn(draft, posts)

    def test_template_used(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "blog/post_list.html")


class PostDetailViewTest(TestCase):

    def setUp(self):
        self.user = make_user()
        self.category = make_category()
        self.post = make_post(self.user, self.category)
        self.url = self.post.get_absolute_url()

    def test_published_post_returns_200(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_draft_post_returns_404(self):
        draft = make_post(
            self.user, self.category,
            title="Borrador", slug="borrador-privado",
            status=Post.STATUS_DRAFT,
        )
        url = draft.get_absolute_url()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_context_contains_post(self):
        response = self.client.get(self.url)
        self.assertEqual(response.context["post"], self.post)

    def test_template_used(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "blog/post_detail.html")


class CategoryDetailViewTest(TestCase):

    def setUp(self):
        self.user = make_user()
        self.category = make_category()
        self.url = self.category.get_absolute_url()

    def test_returns_200(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_only_published_posts_in_context(self):
        published = make_post(self.user, self.category, title="Pub", slug="pub")
        draft = make_post(
            self.user, self.category,
            title="Draft", slug="draft",
            status=Post.STATUS_DRAFT,
        )
        response = self.client.get(self.url)
        posts = list(response.context["posts"])
        self.assertIn(published, posts)
        self.assertNotIn(draft, posts)

    def test_template_used(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "blog/category_detail.html")
