from django.shortcuts import render, redirect
from django.http import request, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.db import IntegrityError
from .models import User, Image
from .forms import ImageForm
# Create your views here.

class HttpResponseSeeOthers(HttpResponseRedirect):
    status_code = 303

login_required = login_required(login_url='/login')

def index(request):
    if request.user.is_authenticated:
        images = Image.objects.filter(owner=request.user)
        return render(request, 'snoopy_images/index.html', {'images': images})
    return render(request, 'snoopy_images/index.html', {'images': []})
  
def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        try:
            user = User.objects.create_user(username=username, password=password)
        except IntegrityError:
            return render(request, 'snoopy_images/signup.html', {'error': 'Username is already taken'})
        login(request, user)
        return HttpResponseSeeOthers(reverse('index'))
    return render(request, 'snoopy_images/signup.html')
  
def login_view(request):
    if request.method == 'POST':
      username = request.POST['username']
      password = request.POST['password']
      user = authenticate(request, username=username, password=password)
      if user is not None:
          login(request, user)
          return HttpResponseSeeOthers(reverse('index'))
    return render(request, 'snoopy_images/login.html')

@login_required
def logout_view(request):
    logout(request)
    return HttpResponseSeeOthers(reverse('index'))

@login_required
def upload(request):
    if request.method == 'POST':
        try:
            form = ImageForm(request.POST, request.FILES)
            if form.is_valid():
                image = form.save(commit=False)
                image.owner = request.user
                image.save()
                return HttpResponseSeeOthers(reverse('index'))
        except Exception as e:
            print(e)
            return render(request, 'snoopy_images/upload.html', {'form': ImageForm(), 'error': str(e)})
    form = ImageForm()
    return render(request, 'snoopy_images/upload.html', {'form': form})

