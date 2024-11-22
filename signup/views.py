from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.hashers import check_password, make_password
from .models import Client, LoginHistory
import requests
import logging

logger = logging.getLogger(__name__)


def get_client_ip(request):
    """Helper untuk mendapatkan IP address dari request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

# Google reCAPTCHA Secret Key
RECAPTCHA_SECRET_KEY = '6Lcp34AqAAAAAHN4g87bwjPMoBa8vMoscNWguAOX'

def signup_view(request):
    if request.method == 'POST':
        logger.debug(f"Request POST data: {request.POST}")
        # Jika form login dikirim
        if 'login' in request.POST:
            username = request.POST.get('username')
            password = request.POST.get('password')

            # Autentikasi user
            try:
                client = Client.objects.get(username=username)
                ip_address = get_client_ip(request)
                logger.debug(f"Attempting login for username: {username}")
                logger.debug(f"Stored password (hashed): {client.password}")
                logger.debug(f"Entered password: {password}")
                if check_password(password, client.password):
                    # Simpan history login (berhasil)
                    LoginHistory.objects.create(
                        client=client,
                        ip_address=ip_address,
                        status='SUCCESS'
                    )

                    # Simpan user ke session
                    request.session['client_id'] = client.id
                    return JsonResponse({'message': 'Login successful!'}, status=200)
                else:
                    # Simpan history login (gagal)
                    LoginHistory.objects.create(
                        client=client,
                        ip_address=ip_address,
                        status='FAIL'
                    )
                    return JsonResponse({'error': 'Invalid username or password.'}, status=400)
            except Client.DoesNotExist:
                return JsonResponse({'error': 'Invalid username or password.'}, status=400)
        # Jika form signup dikirim
        elif 'signup' in request.POST:
            username = request.POST.get('username')
            email = request.POST.get('email')
            password = request.POST.get('password')
            full_name = request.POST.get('full_name')
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
                return JsonResponse({'error': 'Invalid reCAPTCHA. Please try again.'}, status=400)

            # Validasi data
            if not username or not email or not password:
                return JsonResponse({'error': 'All fields are required.'}, status=400)

            # Simpan data ke database
            try:
                # Pastikan username tidak duplikat
                if Client.objects.filter(username=username).exists():
                    return JsonResponse({'error': 'Username already exists.'}, status=400)

                # Buat user baru
                user = Client.objects.create(
                    username=username,
                    email=email,
                    password=make_password(password),
                    full_name=full_name,
                )
                user.save()
                return JsonResponse({'message': 'Registration successful!'}, status=201)
                
            except Exception as e:
                logger.error(f"Error occurred during signup: {str(e)}")
                return JsonResponse({'error': 'An error occurred. Please try again.'}, status=400)

    return render(request, 'registrasi.html')
