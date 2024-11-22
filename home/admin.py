from django.contrib import admin
from .models import PostMenu, Rating

class RatingInline(admin.TabularInline):
    model = Rating
    extra = 0  # Menentukan seberapa banyak baris kosong yang akan ditampilkan di form admin

class PostMenuAdmin(admin.ModelAdmin):
    list_display = ('nama_menu', 'kategori', 'harga', 'created_at', 'kepuasan')
    search_fields = ('nama_menu', 'kategori')
    def save_model(self, request, obj, form, change):
        # Save the object first to ensure it has a primary key
        super().save_model(request, obj, form, change)
        # Now you can safely call update_kepuasan
        obj.update_kepuasan()

class RatingAdmin(admin.ModelAdmin):
    list_display = ('post_menu', 'nilai', 'created_at')  # Menampilkan rating dan tanggal pembuatan
    list_filter = ('nilai', 'created_at')  # Menyaring berdasarkan nilai dan tanggal
    search_fields = ('post_menu__nama_menu',)  # Mencari berdasarkan nama menu terkait rating

# Registrasi model untuk admin
admin.site.register(PostMenu, PostMenuAdmin)
admin.site.register(Rating, RatingAdmin)