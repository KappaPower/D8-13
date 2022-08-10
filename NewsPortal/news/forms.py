from django import forms
from django.core.exceptions import ValidationError

from .models import Post, User


class PostForm(forms.ModelForm):
    article_header = forms.CharField(min_length=20)

    class Meta:
        model = Post
        fields = [
            'article_header',
            'article_text',
            'author',
        ]

    def clean(self):
        cleaned_data = super().clean()
        article_header = cleaned_data.get("article_header")
        article_text = cleaned_data.get("article_text")

        if article_header == article_text:
            raise ValidationError(
                "Текст не должен быть идентичен названию статьи"
            )

        return cleaned_data

class UserForm(forms.ModelForm):
    article_header = forms.CharField(min_length=20)

    class Meta:
        model = User
        fields = '__all__'
