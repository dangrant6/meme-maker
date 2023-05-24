from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.http import Http404, HttpResponseNotFound, HttpResponseRedirect, HttpResponse
from mememaker.forms import MemeInput
from mememaker.models import Meme
from mememaker.forms import LoginForm
from mememaker.forms import RegisterForm

# Create your views here.
def home(request):
    return render(request, 'mememaker/home.html')

def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')  # Redirect to the Home View after successful login
            else:
                form.add_error(None, "Invalid username or password.")
    else:
        form = LoginForm()
    
    return render(request, 'mememaker/login.html', {'form': form})

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            # You can also include additional fields like email, name, etc.
            user = User.objects.create_user(username=username, password=password)
            # Additional code to save any additional user information
            return redirect('home')  # Redirect to the Home View after successful registration
    else:
        form = RegisterForm()
    
    return render(request, 'mememaker/register.html', {'form': form})

def make_meme(request):
    if request.method == 'POST':
        form = MemeInput(request.POST)
        if form.is_valid():
            words = form.cleaned_data['words']
            return redirect('memes')
    else:
        form = MemeInput()
    return render(request, 'mememaker/home.html')

def save_meme(request):
    if request.method == 'POST':
        # Retrieve the necessary data from the request (e.g., meme image URL)
        # Save the data to the database or storage location
        return redirect('memes')  # Redirect to the Memes View
    
    # Render the save_meme.html template if the request is not POST
    return render(request, 'mememaker/save_meme.html')
