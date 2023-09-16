from django.shortcuts import render, get_object_or_404
from django.views import View
from .models import Post
from django.core.paginator import Paginator

from .forms import SigUpForm, SignInForm, FeedBackForm
from django.contrib.auth import login, authenticate
from django.http import HttpResponseRedirect
from django.db.models import Q

from django.http import HttpResponse
from django.core.mail import send_mail, BadHeaderError


class MainView(View):
    def get(self, request, *args, **kwargs):
        posts = Post.objects.all() # type: ignore
        paginator = Paginator(posts, 6)
        
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        return render(request, 'app/home.html', context={
            'page_obj': page_obj,
        })

class PostDetailView(View):
    def get(self, request, slug, *args, **kwargs):
        post = get_object_or_404(Post, url=slug)

        return render(request, 'app/post_detail.html', context={
            'post': post,
        })

class SignUpView(View):
    def get(self, request, *args, **kwargs):
        form = SigUpForm()
        return render(request, 'app/signup.html', context={
            'form': form,
        })

    def post(self, request, *args, **kwargs):
        form = SigUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            if user is not None:
                login(request, user)
                return HttpResponseRedirect('/')
        return render(request, 'app/signup.html', context={
            'form': form,
        })

class SignInView(View):
    def get(self, request, *args, **kwargs):
        form = SignInForm()
        return render(request, 'app/signin.html', context={
            'form': form,
        })

    def post(self, request, *args, **kwargs):
        form = SignInForm(request.POST)
        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return HttpResponseRedirect('/')
        return render(request, 'app/signin.html', context={
            'form': form,
        })

class FeedBackView(View):
    def get(self, request, *args, **kwargs):
        form = FeedBackForm()
        return render(request, 'app/contact.html', context={
            'form': form,
            'title': 'Написать мне',
        })

    def post(self, request, *args, **kwargs):
        form = FeedBackForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']

            message_text = f'E-mail: {email}\n{message}'
            try:
                send_mail(f'От {name} | {subject}', message_text, email, ['django.ppp@gmail.com'])
            except BadHeaderError:
                return HttpResponse('Невалидный заголовок') # type: ignore
            return HttpResponseRedirect('success')
        return render(request, 'myblog/contact.html', context={
            'form': form,
        })

class SuccessView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'app/success.html', context={
            'title': 'Спасибо'
        })

class SearchResultsView(View):
    def get(self, request, *args, **kwargs):
        query = request.GET.get('q')
        results = ''
        if query:
            results = Post.objects.filter( # type: ignore
                Q(h1__iregex=query) | Q(content__iregex=query)
            )

        return render(request, 'app/search.html', context={
            'title': 'Поиск',
            'results': results,
            'count': len(results),
        })
