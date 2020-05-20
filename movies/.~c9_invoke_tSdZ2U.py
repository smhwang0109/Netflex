from django.shortcuts import render, redirect, get_object_or_404
from .models import Movie, Review, Comment
from .forms import MovieForm, ReviewForm, CommentForm
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Avg
from django.core.paginator import Paginator
from django.http import JsonResponse


def index(request):
    movies = Movie.objects.order_by('-popularity')
    paginator = Paginator(movies, 20)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'movies': movies,
        'page_obj': page_obj,
    }
    return render(request, 'movies/index.html', context)

@login_required
def movie_create(request):
    if request.user.is_staff:
        if request.method == 'POST':
            movie_form = MovieForm(request.POST)
            if movie_form.is_valid():
                movie = movie_form.save()
                return redirect('movies:movie_detail', movie.pk)
        else:
            movie_form = MovieForm()
        context = {
            'form': movie_form
        }
        return render(request, 'movies/form.html', context)
    else:
        return redirect('movies:index')


def movie_detail(request, movie_pk):
    movie = get_object_or_404(Movie, pk=movie_pk)
    lang = movie.original_language
    lang_dict = {
        'en': '영어', 'jn': '일본어', 'es': '스페인어', 'fr':'프랑스어', 'ko':'한국어', 'da': '덴마크어',
        'pt': '포르투갈어', 'cn': '중국어', 'it': '이탈리아어', 'de': '독일어',
    }
    lang = lang_dict[lang]
    genre = movie.genres
    genres = []

    reviews_aggregate = Review.objects.filter(movie=movie).aggregate(Avg('rank'))
    context = {
        'movie': movie,
        'review_rank': reviews_aggregate['rank__avg'],
        'lang':lang,
    }
    return render(request, 'movies/movie_detail.html', context)

@login_required
def movie_update(request, movie_pk):
    if request.user.is_staff:
        movie = get_object_or_404(Movie, pk=movie_pk)
        if request.method=='POST': # 관리자 권한이 있을 때만 수정 가능
            form = MovieForm(request.POST, instance=movie)
            if form.is_valid():
                movie = form.save()
                return redirect('movies:movie_detail', movie.pk)
        else:
            form = MovieForm(instance=movie)
        context = {
            'form':form,
        }
        return render(request, 'movies/form.html', context)
    return redirect('movies:index')

@require_POST
@login_required
def movie_delete(request, movie_pk):
    if request.user.is_staff:
        movie = get_object_or_404(Movie, pk=movie_pk)
        movie.delete()
    return redirect('movies:index')


@login_required
def review_create(request, movie_pk):
    movie = get_object_or_404(Movie, pk=movie_pk)
    if request.method == 'POST':
        review_form = ReviewForm(request.POST)
        if review_form.is_valid():
            review = review_form.save(commit=False)
            review.movie = movie
            review.author = request.user
            review.save()
            return redirect('movies:review_detail', movie.pk, review.pk)
    else:
        review_form = ReviewForm()
    context = {
        'form': review_form
    }
    return render(request, 'movies/form.html', context)

def review_detail(request, movie_pk, review_pk):
    review = get_object_or_404(Review, pk=review_pk)
    comment_form = CommentForm()
    context = {
        'review': review,
        'comment_form': comment_form,
    }
    return render(request, 'movies/review_detail.html', context)


@login_required
def review_update(request, movie_pk, review_pk):
    movie = get_object_or_404(Movie, pk=movie_pk)
    review = get_object_or_404(Review, pk=review_pk)
    if request.user == review.author:
        if request.method == 'POST':
            review_form = ReviewForm(request.POST, instance=review)
            if review_form.is_valid():
                review = review_form.save(commit=False)
                review.movie = movie
                review.author = request.user
                review.save()
                return redirect('movies:review_detail', movie.pk, review.pk)
        else:
            review_form = ReviewForm(instance=review)
        context = {
            'form':review_form
        }
        return render(request, 'movies/form.html', context)
    else:
        return redirect('movies:review_detail', movie.pk, review.pk)

@require_POST
@login_required
def review_delete(request, movie_pk, review_pk):
    review = get_object_or_404(Review, pk=review_pk)
    if request.user == review.author:
        review.delete()
        return redirect('movies:movie_detail', movie_pk)
    return redirect('movies:review_detail', movie_pk, review.pk)

@require_POST
@login_required
def comment_create(request, movie_pk, review_pk):
    review = get_object_or_404(Review, pk=review_pk)
    comment_form = CommentForm(request.POST)
    if comment_form.is_valid():
        comment = comment_form.save(commit=False)
        comment.author = request.user
        comment.review = review
        comment.save()
    return redirect('movies:review_detail', movie_pk, review.pk)

@login_required
def comment_update(request, movie_pk, review_pk, comment_pk):
    review = get_object_or_404(Review, pk=review_pk)
    comment = get_object_or_404(Comment, pk=comment_pk)
    if request.method == 'POST':
        if request.user == comment.author:
            comment_form = CommentForm(request.POST, instance=comment)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.author = request.user
                comment.review = review
                comment.save()
        return redirect('movies:review_detail', movie_pk, review.pk)
    else:
        comment_form = CommentForm(instance=comment)
    context = {
        'review': review,
        'comment_form': comment_form
    }
    return render(request, 'movies/review_detail.html', context)

@require_POST
@login_required
def comment_delete(request, movie_pk, review_pk, comment_pk):
    comment = get_object_or_404(Comment, pk=comment_pk)
    if request.user == comment.author:
        comment.delete()
    return redirect('movies:review_detail', movie_pk, review_pk)

def review_like(request, movie_pk, review_pk):
    review = get_object_or_404(Review, pk=review_pk)
    if review.like_users.filter(id=request.user.pk).exists():
        review.like_users.remove(request.user)
    else:
        review.like_users.add(request.user)
    return redirect('movies:review_detail', movie_pk, review_pk)

def search(request):
    keyword = request.GET.get('keyword')
    movies = Movie.objects.filter(Q(title__icontains=keyword)|Q(overview__icontains=keyword))
    context = {
        'movies': movies,
        'keyword': keyword,
    }
    return render(request, 'movies/index.html', context)

def recommendation(request):
    import random
    movies = Movie.objects.order_by('-popularity')[:100]
    random_movies = random.sample(list(movies), 20)
    context = {
        'random_movies': random_movies,
    }
    return render(request, 'movies/recommendation.html', context)

@login_required
def like(request, movie_pk):
    user = request.user
    movie = get_object_or_404(Movie, pk=movie_pk)

    if movie.like_users.filter(pk=user.pk).exists():
        movie.like_users.remove(user)
        liked = False
    else:
        movie.like_users.add(user)
        liked = True

    context = {
        'liked':liked,
    }
    return JsonResponse(context)