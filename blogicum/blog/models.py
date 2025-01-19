from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse

from .constants import Constants

User = get_user_model()


class AbstractPublishedCreated(models.Model):
    is_published = models.BooleanField(
        'Опубликовано', default=True,
        help_text='Снимите галочку, чтобы скрыть публикацию.'
    )
    created_at = models.DateTimeField('Добавлено', auto_now_add=True)

    class Meta:
        abstract = True


class Category(AbstractPublishedCreated):
    title = models.CharField(
        'Заголовок', max_length=Constants.MAX_CHAR_FIELD_LENGTH
    )
    description = models.TextField('Описание')
    slug = models.SlugField(
        'Идентификатор', unique=True,
        help_text=(
            'Идентификатор страницы для URL; разрешены символы '
            'латиницы, цифры, дефис и подчёркивание.'
        )
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return (
            (self.title[:Constants.MAX_TITLE_LENGTH] + '...')
            if len(self.title) > Constants.MAX_TITLE_LENGTH else self.title
        )


class Location(AbstractPublishedCreated):
    name = models.CharField(
        'Название места', max_length=Constants.MAX_CHAR_FIELD_LENGTH
    )

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        return (
            (self.name[:Constants.MAX_TITLE_LENGTH] + '...')
            if len(self.name) > Constants.MAX_TITLE_LENGTH else self.name
        )


class Post(AbstractPublishedCreated):
    title = models.CharField(
        'Заголовок', max_length=Constants.MAX_CHAR_FIELD_LENGTH
    )
    text = models.TextField('Текст')
    pub_date = models.DateTimeField(
        'Дата и время публикации',
        help_text=(
            'Если установить дату и время в будущем — можно '
            'делать отложенные публикации.'
        )
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, null=False, blank=False,
        verbose_name='Автор публикации',
    )
    location = models.ForeignKey(
        Location, on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name='Местоположение',
    )
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True,
        verbose_name='Категория',
    )
    image = models.ImageField(
        'Изображение', upload_to='posts_images', blank=True
    )

    def comment_count(self):
        return self.post_comment.count()

    def get_absolute_url(self):
        return reverse('blog:post_detail', kwargs={'pk': self.pk})

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        ordering = ('-pub_date',)
        default_related_name = 'posts'

    def __str__(self):
        return (
            (self.title[:Constants.MAX_TITLE_LENGTH] + '...')
            if len(self.title) > Constants.MAX_TITLE_LENGTH else self.title
        )


class Comment(models.Model):
    text = models.TextField('Текст комментария')
    post_comment = models.ForeignKey(
        Post,
        on_delete=models.CASCADE, related_name='post_comment'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=False)

    class Meta:
        ordering = ('created_at',)
