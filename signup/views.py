from django.shortcuts import render, redirect
from django.utils.timezone import now
from django.contrib import messages
from django.contrib.auth.hashers import check_password, make_password
from .models import Client, LoginHistory
from django.urls import reverse
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
        logger.debug(f"Data POST/GET: {request.POST or request.GET}")
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

    return render(request, 'registrasi.html')

def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        next_url = request.GET.get('next') or reverse('home')

        try:
            logger.debug(f"Attempting login with email: {email}")
            client = Client.objects.filter(email=email).first()
            if client and check_password(password, client.password):
                # Update session
                request.session['is_logged_in'] = True
                request.session['username'] = client.username

                # Update last_login
                client.last_login = now()
                client.save()

                logger.info(f"Login successful for user: {client.username}")
                return redirect(next_url)
            else:
                logger.warning(f"Invalid login attempt with email: {email}")
                messages.error(request, 'Invalid email or password')
        except Exception as e:
            logger.error(f"Error occurred during login: {str(e)}")
            messages.error(request, 'An error occurred. Please try again.')

    return redirect('signup')
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
