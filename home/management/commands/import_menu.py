import csv
from datetime import datetime
from django.core.management.base import BaseCommand
from home.models import PostMenu  # Ganti "yourapp" dengan nama aplikasi Anda

class Command(BaseCommand):
    help = 'Import data dari CSV ke model PostMenu'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path ke file CSV')

    def handle(self, *args, **kwargs):
        csv_file = kwargs['csv_file']
        self.stdout.write(f"Importing data dari {csv_file}...")

        with open(csv_file, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                menu = PostMenu(
                    nama_menu=row['nama_menu'],
                    kategori=row['kategori'],
                    harga=float(row['harga']),
                    gambar=row['gambar'],
                    created_at=datetime.strptime(row['created_at'] or datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), '%Y-%m-%d %H:%M:%S.%f'),
                    kepuasan=float(row['kepuasan']) if row['kepuasan'] else 0  # Tangani jika kepuasan kosong
                )
                menu.save()

        self.stdout.write(self.style.SUCCESS('Data import selesai.'))
