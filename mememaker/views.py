from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import Http404, HttpResponseNotFound, HttpResponseRedirect, HttpResponse
from django.contrib.auth.views import PasswordResetForm
from mememaker.forms import MemeInput
from mememaker.models import Meme
from mememaker.forms import LoginForm
from mememaker.forms import RegistrationForm
from django.contrib.auth.forms import UserCreationForm
from dotenv import load_dotenv
import psycopg2
import requests
import random
import openai
import os
import uuid
import environ
env = environ.Env()
environ.Env.read_env()
load_dotenv()

# Create your views here.
def home(request):
    return render(request, 'mememaker/home.html')

def login_page(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        pass1 = request.POST.get('pass')
        user = authenticate(username=username, password=pass1)
        if user is not None:
            login(request,user)
            return redirect('mkmeme')
        else:
            return HttpResponse("Invalid username or password.")
        form = LoginForm(request.POST)
        '''
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
    '''
    #return render(request, 'mememaker/login.html', {'form': form})
    return render(request, 'mememaker/login.html')

def register_page(request):
    if request.method == 'POST':
        uname = request.POST.get('username')
        email = request.POST.get('email')
        pass1 = request.POST.get('password1')
        pass2 = request.POST.get('password2')
        form = UserCreationForm(request.POST)
        if pass1 != pass2:
            return ("Passwords do not match.")
        else:
            my_user = User.objects.create_user(uname, email, pass1)
            my_user.save()
            return redirect('mkmeme')
        '''    
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('mkmeme.html')  # Replace 'mkmeme' with the URL name of your meme page
    else:
        form = UserCreationForm()
        '''
    #return render(request, 'mememaker/register.html', {'form': form})
    return render(request, 'mememaker/register.html')

def logout_page(request):
    logout(request)
    return redirect('login')

def generate_meme_text(word_input):
    openai.api_key = os.getenv("AIKEY")
    response = openai.Completion.create(
        engine='davinci',
        #engine='davinci:ft-personal-2023-05-26-06-05-49',
        #prompt=f"Make a meme caption based off the word {word_input}.",
        prompt=f"Make a funny meme caption using the word {word_input}",
        max_tokens=50,
        n=1,
        stop=None,
        temperature=0.7
    )
    meme_text = response.choices[0].text.strip()
    return meme_text

def generate_meme(word_input):
    templates_response = requests.get('https://api.memegen.link/templates/')
    templates = templates_response.json()
    random_template = random.choice(templates)
    template_name = random_template['id']
    meme_url = f"https://api.memegen.link/{template_name}/{word_input}.png"
    return meme_url

def make_meme(request):
    if request.method == 'POST':
        word_input = request.POST.get('word_input')
        meme_text = generate_meme_text(word_input)
        meme_url = generate_meme(meme_text)
        save_meme(meme_url)
        user_memes = Meme(user=request.user, url=meme_url)
        user_memes.save()
        saved_memes = get_saved_memes()
        return render(request, 'mememaker/community.html', {'saved_memes': saved_memes})
    return render(request, 'mememaker/mkmeme.html')

def community_page(request):
    saved_memes = get_saved_memes()
    return render(request, 'mememaker/community.html', {'saved_memes': saved_memes})

def create_meme_table():
    conn = psycopg2.connect(
        host=os.getenv("HOST"),
        port=os.getenv("PORT"),
        database=os.getenv("DATABASE"),
        user=os.getenv("NAME"),
        password=os.getenv("PASSWORD")
    )
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS memes (
            id SERIAL PRIMARY KEY,
            url TEXT
        );
    ''')
    conn.commit()
    cursor.close()
    conn.close()
    
def save_meme(meme_url):
    conn = psycopg2.connect(
        host=os.getenv("HOST"),
        port=os.getenv("PORT"),
        database=os.getenv("DATABASE"),
        user=os.getenv("NAME"),
        password=os.getenv("PASSWORD")
    )
    cursor = conn.cursor()
    cursor.execute("INSERT INTO memes (url) VALUES (%s)", (meme_url,))
    conn.commit()
    cursor.close()
    conn.close()

def generate_unique_filename():
    unique_filename = str(uuid.uuid4()) + '.jpg'
    return unique_filename

def get_saved_memes():
    conn = psycopg2.connect(
        host=os.getenv("HOST"),
        port=os.getenv("PORT"),
        database=os.getenv("DATABASE"),
        user=os.getenv("NAME"),
        password=os.getenv("PASSWORD")
    )
    cursor = conn.cursor()
    cursor.execute("SELECT url FROM memes")
    saved_memes = cursor.fetchall()
    cursor.close()
    conn.close()
    return saved_memes

def account_page(request):
    user_id = request.user.id
    the_user_memes = Meme.objects.filter(user_id=user_id).order_by('-created_at')
    '''
    user = request.user
    the_user_memes = Meme.objects.filter(user=user).order_by('-created_at')
    '''
    return render(request, 'mememaker/account.html', {'user': user_id, 'memes': the_user_memes})

def forgot_pass(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            form.save(
                request=request,
                from_email='your_email@example.com',  # Replace with your email address
                email_template_name='resetemail.html',  # Replace with your email template
                subject_template_name='password_reset_subject.txt'  # Replace with your subject template
            )
            return redirect('passdone')
    else:
        form = PasswordResetForm()
    
    return render(request, 'mememaker/reset.html', {'form': form})

def password_reset_email_sent(request):
    return render(request, 'mememaker/passdone.html')