from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import PostMenu, Rating
from django.http import JsonResponse
from django.urls import reverse
from django.db.models import Avg

def home(request):
    if not request.user.is_authenticated:
        return redirect('signup')
    makanan_list = PostMenu.objects.all()
    range_angka = list(range(1, 6))

    for makanan in makanan_list:
        makanan.kepuasan = float(makanan.kepuasan) if makanan.kepuasan is not None else 0.0
    if request.path == reverse('home') and not request.user.is_authenticated:
        return redirect(reverse('signup'))
    return render(request, 'home1.html', {'makanan_list': makanan_list, 'range_angka': range_angka, 'is_logged_in': request.user.is_authenticated})

def menu_detail(request, menu_id):
    post_menu = get_object_or_404(PostMenu, pk=menu_id)
    ratings = Rating.objects.filter(post_menu=post_menu)
    average_rating = ratings.aggregate(average=Avg('nilai'))['average'] or 0
    rating_count = ratings.count()

    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if not request.user.is_authenticated:
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
        'rating_count': rating_count
    })

def update_kepuasan(self):
    ratings = self.rating_set.aggregate(average=Avg('nilai'))['average'] or 0
    self.kepuasan = ratings
    self.save()

@login_required(login_url='/signup/')  # Ganti dengan URL login Anda
def Profile(request):
    # Halaman profile Anda
    return render(request, 'profile.html')