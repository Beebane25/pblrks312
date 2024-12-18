from django.db import models

class PostMenu(models.Model):
    nama_menu = models.CharField(max_length=255)
    kategori = models.CharField(max_length=255)
    harga = models.DecimalField(max_digits=10, decimal_places=2)
    gambar = models.ImageField(upload_to='media/menu_images/')
    created_at = models.DateTimeField(auto_now_add=True)
    kepuasan = models.FloatField(default=0.0)

    def __str__(self):
        return self.nama_menu

    def update_kepuasan(self):
        ratings = self.rating_set.all()
        total_ratings = ratings.count()
        if total_ratings > 0:
            average_rating = sum(rating.nilai for rating in ratings) / total_ratings
            self.kepuasan = (average_rating / 5) * 100
            self.save()

class Rating(models.Model):
    post_menu = models.ForeignKey(PostMenu, related_name='rating_set', on_delete=models.CASCADE)
    nilai = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Rating {self.nilai} for {self.post_menu.nama_menu}"
    
class Cart(models.Model):
    from signup.models import Client
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart milik {self.client.username}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    menu = models.ForeignKey(PostMenu, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.menu.nama_menu} (Keranjang {self.cart.client.username})"

    def get_total_price(self):
        return self.quantity * self.menu.harga
