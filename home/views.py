from django.shortcuts import render, get_object_or_404
from .models import PostMenu, Rating
from django.http import JsonResponse

def home(request):
    makanan_list = PostMenu.objects.all()  # Fetch all food items
    range_angka = list(range(1, 6))  # List of numbers from 1 to 5

    # Convert kepuasan to float for each makanan
    for makanan in makanan_list:
        makanan.kepuasan = float(makanan.kepuasan) if makanan.kepuasan is not None else 0.0

    return render(request, 'home1.html', {'makanan_list': makanan_list, 'range_angka': range_angka})

def menu_detail(request, menu_id):
    post_menu = get_object_or_404(PostMenu, pk=menu_id)
    ratings = Rating.objects.filter(post_menu=post_menu)
    rating_count = ratings.count()
    average_rating = sum(rating.nilai for rating in ratings) / rating_count if rating_count > 0 else 0

    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            rating_value = int(request.POST.get('rating'))
            if 1 <= rating_value <= 5:
                Rating.objects.create(post_menu=post_menu, nilai=rating_value)
                post_menu.update_kepuasan()  # Ensure this method exists
                return JsonResponse({'success': True, 'message': 'Rating berhasil ditambahkan'})
            else:
                return JsonResponse({'success': False, 'message': 'Rating harus antara 1 dan 5'})
        except ValueError:
            return JsonResponse({'success': False, 'message': 'Rating tidak valid'})

    return render(request, 'home1.html', {
        'post_menu': post_menu,
        'average_rating': average_rating,
        'rating_count': rating_count
    })
