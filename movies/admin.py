from django.contrib import admin
from .models import Genre, Movie, Review, Comment

admin.site.register(Genre)
admin.site.register(Movie)
admin.site.register(Review)
admin.site.register(Comment)