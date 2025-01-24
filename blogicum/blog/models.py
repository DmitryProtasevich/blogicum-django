from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse

from .constants import Constants

User = get_user_model()


class AbstsractCreatedAt(models.Model):
    created_at = models.DateTimeField('Добавлено', auto_now_add=True)

    class Meta:
        abstract = True
        ordering = ('created_at',)


class AbstractPublishedCreated(AbstsractCreatedAt):
    is_published = models.BooleanField(
        'Опубликовано', default=True,
        help_text='Снимите галочку, чтобы скрыть публикацию.'
    )

    class Meta:
        abstract = True

    def __str__(self):
        return (
            (self.title[:Constants.MAX_TITLE_LENGTH] + '...')
            if len(self.title) > Constants.MAX_TITLE_LENGTH else self.title
        )


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

    class Meta(AbstsractCreatedAt.Meta):
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'


class Location(AbstractPublishedCreated):
    name = models.CharField(
        'Название места', max_length=Constants.MAX_CHAR_FIELD_LENGTH
    )

    class Meta(AbstsractCreatedAt.Meta):
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
        User, on_delete=models.CASCADE,
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

    def get_absolute_url(self):
        return reverse('blog:post_detail', kwargs={'post_id': self.pk})

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        ordering = ('-pub_date',)
        default_related_name = 'posts'


class Comment(AbstsractCreatedAt):
    text = models.TextField('Текст комментария')
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        verbose_name='Публикация',
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        verbose_name='Автор комментария',
    )

    class Meta(AbstsractCreatedAt.Meta):
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'
        default_related_name = 'comments'

    def __str__(self):
        return (
            (self.text[:Constants.MAX_TITLE_LENGTH] + '...')
            if len(self.text) > Constants.MAX_TITLE_LENGTH else self.text
        )
