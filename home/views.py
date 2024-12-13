from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt
import json
from django.contrib.auth import logout
from .models import PostMenu, Rating
from django.http import JsonResponse
from django.db.models import Avg
from signup.models import Client
def home(request):
    # Periksa apakah user sudah login
    if not request.session.get('is_logged_in', False):
        return redirect('signup')  # Redirect ke halaman signup jika belum login

    # Ambil daftar makanan dari model PostMenu
    makanan_list = PostMenu.objects.all()
    range_angka = list(range(1, 6))

    # Proses data makanan untuk kepuasan
    for makanan in makanan_list:
        makanan.kepuasan = float(makanan.kepuasan) if makanan.kepuasan is not None else 0.0

    # Render halaman home
    return render(request, 'home1.html', {
        'makanan_list': makanan_list,
        'range_angka': range_angka,
        'is_logged_in': request.session.get('is_logged_in', False),
    })

def menu_detail(request, menu_id):
    post_menu = get_object_or_404(PostMenu, pk=menu_id)
    ratings = Rating.objects.filter(post_menu=post_menu)
    makanan_list = PostMenu.objects.all()
    average_rating = ratings.aggregate(average=Avg('nilai'))['average'] or 0
    rating_count = ratings.count()

    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if not request.session.get('is_logged_in', False):
            return JsonResponse({'success': False, 'message': 'Anda harus login untuk memberikan rating'})
        try:
            rating_value = int(request.POST.get('rating'))
            if 1 <= rating_value <= 5:
                Rating.objects.create(post_menu=post_menu, nilai=rating_value)
                post_menu.update_kepuasan()  # Ensure this method exists
                return JsonResponse({'success': True, 'message': 'Rating berhasil ditambahkan'})
            else:
                return JsonResponse({'success': False, 'message': 'Rating harus antara 1 dan 5'})
        except (ValueError, TypeError):
            return JsonResponse({'success': False, 'message': 'Rating tidak valid'})

    return render(request, 'home1.html', {
        'post_menu': post_menu,
        'average_rating': average_rating,
        'rating_count': rating_count,
        'makanan_list': makanan_list
    })

@csrf_exempt
def update_rating(request, menu_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            rating_value = int(data.get('rating'))

            if rating_value < 1 or rating_value > 5:
                return JsonResponse({'success': False, 'message': 'Invalid rating value.'}, status=400)

            # Ambil menu berdasarkan ID
            post_menu = PostMenu.objects.get(id=menu_id)

            # Simpan rating ke database
            Rating.objects.create(post_menu=post_menu, nilai=rating_value)

            # Update kepuasan
            post_menu.update_kepuasan()

            return JsonResponse({'success': True, 'message': 'Rating berhasil ditambahkan dan kepuasan diperbarui.'})
        except PostMenu.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Menu tidak ditemukan.'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=500)
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=405)
def Profile(request):
    if not request.session.get('is_logged_in', False):
        return redirect('signup')  # Redirect ke signup jika belum login

    # Ambil user berdasarkan username dari session
    username = request.session.get('username')
    user = Client.objects.get(username=username)  # Asumsikan 'Client' adalah model user

    return render(request, 'profile.html', {'user': user})

from django.contrib.auth import logout

def logout_view(request):
    logout(request)  # Fungsi ini akan menghapus sesi pengguna
    return redirect('signup')  # Redirect ke halaman home setelah logout