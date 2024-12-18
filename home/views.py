from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import user_passes_test, login_required
import json
from django.contrib.auth import logout
from .models import PostMenu, Rating, Cart, CartItem
from django.http import JsonResponse
from django.db.models import Avg
from signup.models import Client
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from signup.models import Client, Transaksi
from decimal import Decimal



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
class TopUpView(APIView):
    def post(self, request):
        client_id = request.data.get('client_id')
        nominal = request.data.get('nominal')

        try:
            client = Client.objects.get(id=client_id)
        except Client.DoesNotExist:
            return Response({"error": "Client not found"}, status=status.HTTP_404_NOT_FOUND)

        transaksi = Transaksi.objects.create(client=client, jenis='topup', nominal=nominal)
        # Simulasi admin memverifikasi transaksi
        client.saldo += Decimal(nominal)
        client.save()
        transaksi.status = 'berhasil'
        transaksi.save()

        return Response({"message": "Top-up berhasil", "saldo": client.saldo}, status=status.HTTP_200_OK)

from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from signup.models import Client, Transaksi
from decimal import Decimal

@staff_member_required
def topup_balance(request):
    if request.method == 'POST':
        # Ambil data yang dikirimkan dari form
        client_id = request.POST.get('client_id')
        nominal = request.POST.get('nominal')

        try:
            client = Client.objects.get(id=client_id)
        except Client.DoesNotExist:
            messages.error(request, "Pengguna tidak ditemukan.")
            return redirect('topup_balance')

        try:
            nominal = Decimal(nominal)
            if nominal <= 0:
                raise ValueError("Nominal harus lebih besar dari 0.")
        except ValueError as e:
            messages.error(request, f"Error: {str(e)}")
            return redirect('topup_balance')

        # Tambahkan saldo ke akun pengguna
        client.saldo += nominal
        client.save()

        # Catat transaksi top-up
        transaksi = Transaksi.objects.create(
            client=client,
            jenis='topup',
            nominal=str(nominal),
            status='berhasil'
        )

        messages.success(request, f"Saldo pengguna {client.username} berhasil diisi sebesar {nominal}.")
        return redirect('topup_balance')

    # Ambil semua pengguna untuk dipilih admin
    users = Client.objects.all()
    return render(request, 'topup_balance.html', {'users': users})

def admin_required(function):
    return user_passes_test(lambda u: u.is_staff)(function)

@admin_required
def topup_page(request):
    return render(request, 'topup.html')
class PembelianView(APIView):
    def post(self, request):
        client_id = request.data.get('client_id')
        menu_id = request.data.get('menu_id')

        try:
            client = Client.objects.get(id=client_id)
            menu = PostMenu.objects.get(id=menu_id)
        except (Client.DoesNotExist, PostMenu.DoesNotExist):
            return Response({"error": "Client atau Menu tidak ditemukan"}, status=status.HTTP_404_NOT_FOUND)

        if client.saldo < menu.harga:
            return Response({"error": "Saldo tidak mencukupi"}, status=status.HTTP_400_BAD_REQUEST)

        # Lakukan pembelian
        client.saldo -= menu.harga
        client.save()

        # Buat catatan transaksi
        transaksi = Transaksi.objects.create(
            client=client,
            jenis='pembelian',
            nominal=menu.harga,
            status='berhasil',
            menu=menu
        )

        return Response({
            "message": "Pembelian berhasil",
            "saldo_tersisa": client.saldo,
            "menu": menu.nama_menu
        }, status=status.HTTP_200_OK)
    
def pembelian_page(request):
    return render(request, 'pembelian.html')


def get_user_cart(request):
    """Fungsi ini mengembalikan keranjang pengguna saat ini."""
    client_id = request.session.get('client_id')  # Pastikan sesi memiliki ID pengguna
    if not client_id:
        return None  # Jika tidak ada ID pengguna dalam sesi
    try:
        client = Client.objects.get(id=client_id)
    except Client.DoesNotExist:
        return None  # Jika pengguna tidak ditemukan
    cart, created = Cart.objects.get_or_create(client=client)
    return cart

def add_to_cart(request, menu_id):
    if request.method == 'POST':
        client_id = request.session.get('client_id')  # Ambil ID pengguna dari sesi

        if not client_id:
            return redirect(f'/signup/?next={request.path}')  # Redirect ke halaman signup dengan next URL

        try:
            menu = PostMenu.objects.get(id=menu_id)
            cart, created = Cart.objects.get_or_create(client_id=client_id)
            cart.items.create(menu=menu)

            return JsonResponse({'success': True, 'message': 'Item added to cart'})
        except PostMenu.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Menu not found'})
def update_cart_item(request, item_id):
    """Perbarui jumlah item dalam keranjang"""
    if request.method == 'POST':
        cart_item = get_object_or_404(CartItem, id=item_id)
        quantity = int(request.POST.get('quantity', 1))
        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
            return JsonResponse({'success': True, 'message': 'Jumlah item diperbarui'})
        else:
            cart_item.delete()
            return JsonResponse({'success': True, 'message': 'Item dihapus dari keranjang'})

    return JsonResponse({'success': False, 'message': 'Metode request tidak valid'})

def remove_from_cart(request, item_id):
    """Hapus item dari keranjang"""
    if request.method == 'POST':
        cart_item = get_object_or_404(CartItem, id=item_id)
        cart_item.delete()
        return JsonResponse({'success': True, 'message': 'Item dihapus dari keranjang'})

    return JsonResponse({'success': False, 'message': 'Metode request tidak valid'})

def view_cart(request):
    """Lihat isi keranjang"""
    cart = get_user_cart(request)
    if not cart:
        return JsonResponse({'success': False, 'message': 'Keranjang kosong'})

    items = cart.items.all().values(
        'id', 'menu__nama_menu', 'menu__harga', 'quantity'
    )
    return JsonResponse({'success': True, 'items': list(items)})