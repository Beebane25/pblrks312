from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now
from django.contrib import messages
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth import login, logout as auth_logout, authenticate
from .models import Client, LoginHistory
import requests
import logging

logger = logging.getLogger(__name__)

# Helper untuk mendapatkan IP address dari request.
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

# Google reCAPTCHA Secret Key
RECAPTCHA_SECRET_KEY = '6Lcp34AqAAAAAHN4g87bwjPMoBa8vMoscNWguAOX'

# View untuk signup
def signup_view(request):
    if request.method == 'POST':
        logger.debug(f"Request POST data: {request.POST}")
        # Jika form signup dikirim
        if 'signup' in request.POST:
            username = request.POST.get('username')
            email = request.POST.get('email')
            password = request.POST.get('password')
            password2 = request.POST.get('password2')
            recaptcha_token = request.POST.get('g-recaptcha-response')

            # Verifikasi Google reCAPTCHA
            recaptcha_url = 'https://www.google.com/recaptcha/api/siteverify'
            recaptcha_data = {
                'secret': RECAPTCHA_SECRET_KEY,
                'response': recaptcha_token,
            }
            recaptcha_response = requests.post(recaptcha_url, data=recaptcha_data)
            result = recaptcha_response.json()

            if not result.get('success'):
                messages.error(request, 'Invalid reCAPTCHA. Please try again.')
                return redirect('signup')

            # Validasi data
            if not username or not email or not password:
                messages.error(request, 'Semua kolom wajib diisi.')
                return redirect('signup')

            if password != password2:
                messages.error(request, 'Password tidak cocok.')
                return redirect('signup')

            # Simpan data ke database
            try:
                # Pastikan username tidak duplikat
                if Client.objects.filter(username=username).exists():
                    messages.error(request, 'Username already exists.')
                    return redirect('signup')

                # Simpan user baru
                user = Client.objects.create(
                    username=username,
                    email=email,
                    password=make_password(password),  # Hash password sebelum disimpan
                )
                messages.success(request, 'Registration successful!')
                
            except Exception as e:
                logger.error(f"Error occurred during signup: {str(e)}")
                messages.success(request, 'An error occurred. Please try again.')

    

        # Jika form login dikirim
        elif 'login' in request.POST:
            username = request.POST.get('username')
            password = request.POST.get('password')

            # Autentikasi user
            user = authenticate(request, username=username, password=password)
        
            if user is not None:
                login(request, user)
                Client.objects.filter(username=username).update(last_login=now())  # Update last_login
                return redirect('home')  # Ganti 'home' dengan nama URL tujuan setelah login
            else:
                messages.error(request, 'Invalid username or password')

    return render(request, 'registrasi.html')

# View untuk logout
def logout_view(request):
    client_id = request.session.get('client_id')
    if client_id:
        try:
            client = Client.objects.get(id=client_id)
            ip_address = get_client_ip(request)
            # Simpan history logout
            LoginHistory.objects.create(client=client, ip_address=ip_address, status='LOGOUT', timestamp=now())
        except Client.DoesNotExist:
            pass
        request.session.flush()
        messages.success(request, 'Logout successful!')
        return redirect('/')
    messages.error(request, 'User not logged in.')
