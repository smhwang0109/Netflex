from django import forms
from .models import Movie, Review, Comment

class MovieForm(forms.ModelForm):
    class Meta:
        model = Movie
        exclude = ('created_at', 'updated_at')

class ReviewForm(forms.ModelForm):
    rank = forms.IntegerField(
        widget = forms.NumberInput(
            attrs={
                'min':'1',
                'max':'10',
            }
            )
        )
    class Meta:
        model = Review
        exclude = ('movie', 'author', 'created_at', 'updated_at', 'like_users')

class CommentForm(forms.ModelForm):
    content = forms.CharField(
        label='',
        widget=forms.Textarea(
            attrs={
                'placeholder': '댓글을 작성해주세요.',
                'rows': 3,
            }
            )
        )
    class Meta:
        model = Comment
        fields = ['content']