
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)

from .constants import Constants
from .form import CommentForm, PostForm
from .models import Category, Comment, Post, User


class PostMixin:
    model = Post
    paginate_by = Constants.POSTS_LIMIT

    def filter_published_posts(self, post_objects):
        return post_objects.filter(
            pub_date__lte=timezone.now(),
            is_published=True,
            category__is_published=True
        ).prefetch_related('author', 'location', 'category', 'post_comment')


class PostFormMixin:
    model = Post
    fields = ['text', 'title', 'category', 'location', 'pub_date', 'image']
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'


class PageListView(PostMixin, ListView):
    template_name = 'blog/index.html'

    def get_queryset(self):
        return self.filter_published_posts(Post.objects)


class CategoryPostListView(PostMixin, ListView):
    template_name = 'blog/category.html'

    def get_queryset(self):
        self.category_slug = self.kwargs.get('category_slug')
        self.category = get_object_or_404(
            Category, slug=self.category_slug, is_published=True
        )
        return self.filter_published_posts(self.category.posts)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


class ProfileDetailView(LoginRequiredMixin, PostMixin, DetailView):
    model = User
    template_name = 'blog/profile.html'
    context_object_name = 'profile'

    def get_object(self):
        return get_object_or_404(User, username=self.kwargs['username'])

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_posts = Post.objects.filter(author=self.object)
        if self.request.user == self.object:
            user_posts = self.filter_published_posts(user_posts)
        user_posts = (
            user_posts.select_related('author', 'location', 'category')
            .prefetch_related('post_comment')
        )
        paginator = Paginator(user_posts, Constants.POSTS_LIMIT)
        page_number = self.request.GET.get('page')
        context['page_obj'] = paginator.get_page(page_number)
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    fields = ['first_name', 'last_name', 'email']
    template_name = 'blog/user.html'
    success_url = reverse_lazy('blog:index')

    def get_object(self):
        return self.request.user


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'
    context_object_name = 'post'

    def get_queryset(self):
        return (
            Post.objects.select_related('author')
            .prefetch_related('post_comment__author')
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = self.object.post_comment.all()
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    template_name = 'blog/create.html'
    form_class = PostForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile', kwargs={'username': self.request.user.username}
        )


class PostUpdateView(LoginRequiredMixin, PostFormMixin, UpdateView):
    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if self.request.user == obj.author:
            return obj

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail', kwargs={'post_id': self.object.id}
        )


class PostDeleteView(LoginRequiredMixin, PostFormMixin, DeleteView):
    success_url = reverse_lazy('blog:index')


class CommentMixin:
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def dispatch(self, request, *args, **kwargs):
        comment = get_object_or_404(
            Comment.objects.select_related('author', 'post_comment'),
            pk=kwargs[self.pk_url_kwarg]
        )
        if comment.author != request.user:
            return redirect(
                'blog:post_detail', post_id=comment.post_comment.id
            )
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse(
            'blog:post_detail', kwargs={'post_id': self.kwargs['post_id']}
        )


class CommentUpdateView(LoginRequiredMixin, CommentMixin, UpdateView):
    pass


class CommentDeleteView(LoginRequiredMixin, CommentMixin, DeleteView):
    pass


class CommentCreateView(LoginRequiredMixin, CreateView):
    form_class = CommentForm
    template_name = 'blog/comment.html'

    def dispatch(self, request, *args, **kwargs):
        self.post_comment = get_object_or_404(Post, pk=self.kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post_comment = self.post_comment
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail', kwargs={'post_id': self.kwargs['post_id']}
        )
