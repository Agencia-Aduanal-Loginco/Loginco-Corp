from django.views.generic import DetailView, ListView

from .models import Category, Post


class PostListView(ListView):
    model = Post
    template_name = "blog/post_list.html"
    context_object_name = "posts"
    paginate_by = 12

    def get_queryset(self):
        return (
            Post.objects.filter(status=Post.STATUS_PUBLISHED)
            .select_related("category", "author", "featured_image")
            .prefetch_related("tags", "site_targets")
            .order_by("-published_at")
        )


class PostDetailView(DetailView):
    model = Post
    template_name = "blog/post_detail.html"
    context_object_name = "post"

    def get_queryset(self):
        return Post.objects.filter(status=Post.STATUS_PUBLISHED).select_related(
            "category", "author", "featured_image"
        )


class CategoryDetailView(DetailView):
    model = Category
    template_name = "blog/category_detail.html"
    context_object_name = "category"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["posts"] = (
            self.object.posts.filter(status=Post.STATUS_PUBLISHED)
            .select_related("featured_image")
            .order_by("-published_at")
        )
        return ctx
