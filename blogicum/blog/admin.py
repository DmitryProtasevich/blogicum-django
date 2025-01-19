from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group, User

from .models import Category, Location, Post

admin.site.unregister(Group)
admin.site.unregister(User)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    @admin.display(description='Кол-во постов у пользователя')
    def posts_count(self, obj):
        return obj.posts.count()
    list_display = BaseUserAdmin.list_display + ('posts_count',)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'title', 'author', 'location', 'category',
        'is_published', 'pub_date', 'created_at'
    )
    list_display_links = ('title',)
    search_fields = (
        'title', 'text', 'author__username',
        'category__title', 'location__name'
    )
    list_filter = ('is_published', 'created_at', 'category', 'location')


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'is_published', 'created_at')
    list_display_links = ('name',)
    search_fields = ('name',)
    list_filter = ('name', 'is_published')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'slug', 'is_published', 'created_at')
    list_display_links = ('title',)
    search_fields = ('title', 'slug')
    list_filter = ('is_published',)
