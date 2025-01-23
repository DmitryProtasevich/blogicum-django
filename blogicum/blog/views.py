from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from .constants import Constants
from .form import CommentForm, PostForm, UserForm
from .mixins import AuthorPermissionMixin, CommentMixin, PostMixin
from .models import Category, Comment, Post, User


def annotate_posts(queryset):
    return (
        queryset.annotate(comment_count=Count('post'))
        .select_related('author', 'location', 'category')
        .prefetch_related('post')
    ).order_by('-pub_date')


def filter_posts(queryset):
    return queryset.filter(
        pub_date__lte=timezone.now(),
        is_published=True,
        category__is_published=True
    )


class PageListView(ListView):
    template_name = 'blog/index.html'
    model = Post
    paginate_by = Constants.POSTS_LIMIT

    def get_queryset(self):
        return annotate_posts(filter_posts(Post.objects))


class CategoryPostListView(ListView):
    template_name = 'blog/category.html'
    model = Post
    paginate_by = Constants.POSTS_LIMIT
    category = None

    def get_category(self):
        if self.category is None:
            self.category = get_object_or_404(
                Category, slug=self.kwargs.get('category_slug'),
                is_published=True
            )
        return self.category

    def get_queryset(self):
        return annotate_posts(filter_posts(self.get_category().posts))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.get_category()
        return context


class ProfileListView(ListView):
    model = User
    template_name = 'blog/profile.html'
    context_object_name = 'profile'
    paginate_by = Constants.POSTS_LIMIT
    author = None

    def get_author(self):
        if self.author is None:
            self.author = get_object_or_404(
                User, username=self.kwargs.get('username'))
        return self.author

    def get_queryset(self):
        author = self.get_author()
        posts = annotate_posts(author.posts)
        if self.request.user != author:
            posts = filter_posts(posts)
        return posts

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.get_author()
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    form_class = UserForm
    template_name = 'blog/user.html'

    def get_object(self):
        return self.request.user

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile', kwargs={'username': self.request.user.username}
        )


class PostListView(ListView):
    model = Comment
    template_name = 'blog/detail.html'
    context_object_name = 'page_obj'
    paginate_by = Constants.POSTS_LIMIT
    pk_url_kwarg = 'post_id'
    post = None

    def get_post(self):
        if self.post is None:
            self.post = get_object_or_404(
                Post.objects.select_related('author'),
                pk=self.kwargs[self.pk_url_kwarg]
            )
            if (
                not self.post.is_published
                and self.post.author != self.request.user
            ):
                raise Http404('This post is not available to you.')
        return self.post

    def get_queryset(self):
        return self.get_post().post.select_related('author')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post'] = self.get_post()
        context['form'] = CommentForm()
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    template_name = 'blog/create.html'
    form_class = PostForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile', kwargs={'username': self.request.user.username}
        )


class PostUpdateView(PostMixin, UpdateView):
    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail', kwargs={'post_id': self.kwargs['post_id']}
        )


class PostDeleteView(PostMixin, DeleteView):
    pass


class CommentUpdateView(CommentMixin, AuthorPermissionMixin, UpdateView):
    pass


class CommentDeleteView(CommentMixin, AuthorPermissionMixin, DeleteView):
    pass


class CommentCreateView(CommentMixin, CreateView):
    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        return super().form_valid(form)
