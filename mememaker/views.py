from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.contrib.auth.views import PasswordResetForm
# from mememaker.forms import MemeInput
from mememaker.models import Meme
# from mememaker.forms import LoginForm
# from mememaker.forms import RegistrationForm
# from django.contrib.auth.forms import UserCreationForm
from dotenv import load_dotenv
from transformers import GPT2LMHeadModel, GPT2Tokenizer
import psycopg2
import requests
import random
import urllib.parse
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
            login(request, user)
            return redirect('mkmeme')
        else:
            return HttpResponse("Invalid username or password.")
    return render(request, 'mememaker/login.html')

def register_page(request):
    if request.method == 'POST':
        uname = request.POST.get('username')
        email = request.POST.get('email')
        pass1 = request.POST.get('password1')
        pass2 = request.POST.get('password2')
        if pass1 != pass2:
            return HttpResponse("Passwords do not match.")
        else:
            my_user = User.objects.create_user(uname, email, pass1)
            my_user.save()
            return redirect('login')
    return render(request, 'mememaker/register.html')

def logout_page(request):
    logout(request)
    return redirect('login')

# switched to free model since project is old and not in use
# def generate_meme_text(word_input):
#     openai.api_key = os.getenv("AIKEY")
#     response = openai.Completion.create(
#         engine='davinci-002',
#         #engine='davinci:ft-personal-2023-05-26-06-05-49', # fine-tuned model but oudated as of 2024 so switched to davinci-002
#         prompt=f"Make a funny meme caption using the word {word_input}",
#         max_tokens=50,
#         n=1,
#         stop=None,
#         temperature=0.7
#     )
#     meme_text = response.choices[0].text.strip()
#     return meme_text

def generate_meme_text(word_input):
    model_name = "gpt2"
    tokenizer = GPT2Tokenizer.from_pretrained(model_name)
    model = GPT2LMHeadModel.from_pretrained(model_name)
    prompt = f"Create a funny meme caption using the word '{word_input}'. Here is a funny meme caption:"

    inputs = tokenizer.encode(prompt, return_tensors='pt')
    outputs = model.generate(inputs, max_length=50, num_return_sequences=1, temperature=0.4, top_p=0.9, do_sample=True)

    meme_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    meme_text = meme_text.replace(prompt, "").strip()

    return meme_text

def generate_meme(word_input):
    formatted_text = urllib.parse.quote(word_input.replace(' ', '_'))
    templates_response = requests.get('https://api.memegen.link/templates/')
    templates = templates_response.json()
    random_template = random.choice(templates)
    template_name = random_template['id']
    meme_url = f"https://api.memegen.link/{template_name}/{formatted_text}.png"
    return meme_url

def make_meme(request):
    if request.method == 'POST':
        word_input = request.POST.get('word_input')
        meme_text = generate_meme_text(word_input)
        meme_url = generate_meme(meme_text)
        user_memes = Meme(user=request.user, url=meme_url)
        user_memes.save()
        saved_memes = Meme.objects.all()
        return render(request, 'mememaker/community.html', {'saved_memes': saved_memes})
    return render(request, 'mememaker/mkmeme.html')

def community_page(request):
    saved_memes = Meme.objects.all()
    return render(request, 'mememaker/community.html', {'saved_memes': saved_memes})

def account_page(request):
    user_id = request.user.id
    the_user_memes = Meme.objects.filter(user_id=user_id).order_by('-created_at')
    return render(request, 'mememaker/account.html', {'user': request.user, 'memes': the_user_memes})

def forgot_pass(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            return redirect('passdone')
    else:
        form = PasswordResetForm()
    
    return render(request, 'mememaker/reset.html', {'form': form})

def password_reset_email_sent(request):
    return render(request, 'mememaker/passdone.html')