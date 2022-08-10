from django.contrib.auth.models import User
from django.db.models import Sum

from django.db import models


class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_rating = models.SmallIntegerField(default=0)

    # def __str__(self):
    #     return f'{self.authorUsername}'

    def update_rating(self):
        post_rang = self.post_set.aggregate(postRating=Sum('article_rating'))
        temp_rang = 0
        temp_rang += post_rang.get("postRating")

        comment_rang = self.user.comment_set.aggregate(commentRating=Sum('comment_rating'))
        temp_comment = 0
        temp_comment += comment_rang.get("commentRating")

        self.range_author = temp_rang * 3 + temp_comment
        self.save()


class Category(models.Model):
    category_name = models.CharField(max_length=50, unique=True)
    subscribe = models.ManyToManyField(User, through='UserCategory')


class UserCategory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)


class Post(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE)

    NEWS = 'NW'
    ARTICLE = 'AR'
    CATEGORY_CHOICES = (
        (NEWS, 'Новость'),
        (ARTICLE, 'Статья'),
    )

    choice_field = models.CharField(max_length=2, choices=CATEGORY_CHOICES, default=ARTICLE)
    creation_date = models.DateTimeField(auto_now_add=True)

    category = models.ManyToManyField(Category, through="PostCategory")

    article_header = models.CharField(max_length=128, default='Нет названия')
    article_text = models.TextField()
    article_rating = models.IntegerField(default=0)

    def like(self):
        self.article_rating += 1
        self.save()

    def dislike(self):
        self.article_rating -= 1
        self.save()

    def preview(self):
        return f'{self.article_text[0:123]}...Рейтинг {self.article_rating}'

    def get_absolute_url(self):
        return f'/news/{self.id}'


class PostCategory(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment_text = models.TextField()
    comment_date = models.DateTimeField(auto_now_add=True)
    comment_rating = models.IntegerField(default=0)

    def like(self):
        self.comment_rating += 1
        print(self.comment_rating)
        self.save()

    def dislike(self):
        self.comment_rating -= 1
        print(self.comment_rating)
        self.save()
