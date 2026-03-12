#!/usr/bin/env python3
"""
Sora LMS - Setup Script
Jalankan script ini untuk setup awal database dan superuser admin
"""
import os
import sys
import subprocess

def run(cmd):
    print(f"  >> {cmd}")
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        print(f"  [ERROR] Perintah gagal: {cmd}")
        sys.exit(1)

print("\n" + "="*55)
print("  🎓 SORA LMS - Setup Database & Admin")
print("="*55 + "\n")

#print("📦 [1/4] Install dependencies...")
#run("pip install -r requirements.txt")

print("\n🗄️  [2/4] Membuat database migrations...")
run("python manage.py makemigrations")

print("\n🗄️  [3/4] Menjalankan migrasi database...")
run("python manage.py migrate")

print("\n👤 [4/4] Membuat akun admin pertama...")
print("\nMasukkan data untuk akun Admin Sora LMS:\n")

from django.conf import settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sora_lms.settings')

import django
django.setup()

from apps.accounts.models import User

username = input("  Username admin [admin]: ").strip() or "admin"
email = input("  Email admin [admin@sora.id]: ").strip() or "admin@sora.id"
password = input("  Password admin [admin123]: ").strip() or "admin123"

if User.objects.filter(username=username).exists():
    print(f"\n  ⚠️  User '{username}' sudah ada, melewati pembuatan admin.")
else:
    user = User.objects.create_superuser(
        username=username,
        email=email,
        password=password,
        first_name="Admin",
        role="admin"
    )
    print(f"\n  ✅ Admin berhasil dibuat!")
    print(f"     Username : {username}")
    print(f"     Email    : {email}")
    print(f"     Password : {password}")

print("\n" + "="*55)
print("  ✅ Setup selesai!")
print("="*55)
print("\n  Jalankan server dengan:")
print("  >> python manage.py runserver")
print("\n  Akses di: http://127.0.0.1:8000")
print("  Admin Django: http://127.0.0.1:8000/admin/")
print("\n" + "="*55 + "\n")
