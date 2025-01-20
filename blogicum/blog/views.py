from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)

from .constants import Constants
from .form import CommentForm, PostForm, UserForm
from .models import Category, Comment, Post, User


class CommentMixin:
    model = Comment
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


class CommentPostUrlMixin:
    form_class = CommentForm
    template_name = 'blog/comment.html'

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail', kwargs={'post_id': self.kwargs['post_id']}
        )


class FilterPostMixin:
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
    template_name = 'blog/create.html'
    form_class = PostForm
    pk_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs):
        post = get_object_or_404(Post.objects.select_related(
            'author'), id=kwargs['post_id'])
        if post.author != request.user:
            return redirect('blog:post_detail', post_id=post.id)
        return super().dispatch(request, *args, **kwargs)


class FormValidMixin:
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostProfileUrlMixin:
    def get_success_url(self):
        return reverse_lazy(
            'blog:profile', kwargs={'username': self.request.user.username}
        )


class PageListView(FilterPostMixin, ListView):
    template_name = 'blog/index.html'

    def get_queryset(self):
        return self.filter_published_posts(Post.objects)


class CategoryPostListView(FilterPostMixin, ListView):
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


class ProfileDetailView(FilterPostMixin, FormValidMixin, DetailView):
    model = User
    template_name = 'blog/profile.html'
    context_object_name = 'profile'
    form_class = UserForm

    def get_object(self):
        return get_object_or_404(User, username=self.kwargs['username'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = self.object
        context['profile'] = profile
        user_posts = Post.objects.filter(author=profile)
        if self.request.user == profile:
            user_posts = user_posts.select_related(
                'author', 'location', 'category'
            ).prefetch_related('post_comment')
        else:
            user_posts = self.filter_published_posts(user_posts)
        paginator = Paginator(user_posts, Constants.POSTS_LIMIT)
        page_number = self.request.GET.get('page')
        context['page_obj'] = paginator.get_page(page_number)
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'blog/user.html'
    success_url = reverse_lazy('blog:index')
    form_class = UserForm

    def get_object(self):
        return self.request.user


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'
    context_object_name = 'post'

    def get_queryset(self):
        queryset = Post.objects.select_related(
            'author').prefetch_related('post_comment__author')
        post = queryset.filter(id=self.kwargs['post_id']).first()
        if post:
            if not post.is_published and post.author != self.request.user:
                raise Http404('This post is not available to you.')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = self.object.post_comment.all()
        return context


class PostCreateView(
    LoginRequiredMixin, FormValidMixin, PostProfileUrlMixin, CreateView
):
    template_name = 'blog/create.html'
    form_class = PostForm


class PostUpdateView(PostFormMixin, UpdateView):
    pass


class PostDeleteView(
    LoginRequiredMixin, PostFormMixin, PostProfileUrlMixin, DeleteView
):
    pass


class CommentUpdateView(
    LoginRequiredMixin, CommentMixin, CommentPostUrlMixin, UpdateView
):
    pass


class CommentDeleteView(
    LoginRequiredMixin, CommentMixin, CommentPostUrlMixin, DeleteView
):
    pass


class CommentCreateView(LoginRequiredMixin, CommentPostUrlMixin, CreateView):

    def dispatch(self, request, *args, **kwargs):
        self.post_comment = get_object_or_404(Post, pk=self.kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post_comment = self.post_comment
        return super().form_valid(form)
