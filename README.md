# 🎓 Sora LMS
**Learning Management System berbasis Django + MySQL**

---

## 📋 Fitur Utama

- **👤 Autentikasi & Role** — Login, Register, 3 role: Admin, Guru, Siswa
- **📚 Manajemen Kelas** — Buat kelas, modul bertingkat, upload materi (file/video/teks/link)
- **📝 Tugas & Penilaian** — Buat tugas, upload jawaban, nilai + feedback dari guru
- **🧠 Kuis/Ujian Online** — Pilihan ganda, benar/salah, esai, timer, batas percobaan
- **📊 Progress Tracking** — Tracking per materi, laporan progres siswa per kelas
- **📢 Pengumuman** — Guru bisa buat pengumuman di tiap kelas
- **🔐 Kode Pendaftaran** — Kelas bisa dikunci dengan enrollment key
- **⚙️ Panel Admin** — Kelola semua user, kelas, dan data via dashboard admin

---

## ⚙️ Persyaratan Sistem

- Python 3.10+
- MySQL 8.0+ (via XAMPP/phpMyAdmin)
- pip

---

## 🚀 Cara Setup

### Langkah 1 — Buat Database di phpMyAdmin

1. Buka `http://127.0.0.1/phpmyadmin`
2. Klik **New** → beri nama: `sora_lms`
3. Collation: `utf8mb4_unicode_ci` → klik **Create**

### Langkah 2 — Konfigurasi Database (opsional)

Edit file `sora_lms/settings.py` jika username/password MySQL Anda berbeda:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'sora_lms',
        'USER': 'root',       # ganti jika perlu
        'PASSWORD': '',       # isi jika ada password
        'HOST': '127.0.0.1',
        'PORT': '3306',
    }
}
```

### Langkah 3 — Install & Migrasi

```bash
# Install semua dependencies
pip install -r requirements.txt

# Buat tabel database
python manage.py makemigrations
python manage.py migrate

# Buat akun admin
python manage.py createsuperuser
# atau gunakan:
python setup.py
```

### Langkah 4 — Jalankan Server

```bash
python manage.py runserver
```

Buka browser: **http://127.0.0.1:8000**

---

## 👤 Akun Default (jika pakai setup.py)

| Role | Username | Password |
|------|----------|----------|
| Admin | admin | admin123 |

---

## 🗂️ Struktur Project

```
sora_lms/
├── manage.py
├── requirements.txt
├── setup.py
├── sora_lms/              # Konfigurasi Django utama
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── apps/
│   ├── accounts/          # User, Login, Register
│   ├── courses/           # Kelas, Modul, Materi
│   ├── assignments/       # Tugas & Penilaian
│   ├── quizzes/           # Kuis & Ujian
│   └── dashboard/         # Dashboard & Progress
├── templates/             # HTML Templates
│   ├── base.html
│   ├── accounts/
│   ├── courses/
│   ├── assignments/
│   ├── quizzes/
│   └── dashboard/
├── static/                # CSS, JS, Gambar
└── media/                 # File upload
```

---

## 🎨 Alur Penggunaan

### Admin
1. Login → Dashboard admin dengan statistik
2. Kelola pengguna: tambah/edit/hapus guru & siswa
3. Monitor semua kelas dan aktivitas

### Guru
1. Buat kelas baru → tambah modul → upload materi
2. Buat tugas dengan deadline dan nilai maks
3. Buat kuis/ujian dengan berbagai tipe soal
4. Nilai pengumpulan tugas siswa
5. Pantau progress siswa di tiap kelas

### Siswa
1. Daftar akun → login
2. Jelajahi dan daftar ke kelas
3. Belajar materi per modul (progress otomatis tercatat)
4. Kumpulkan tugas (upload file atau teks)
5. Kerjakan kuis online dengan timer
6. Pantau nilai dan progress belajar

---

## 📦 Dependencies

```
Django==4.2.11
mysqlclient==2.2.4
Pillow==10.2.0
```

---

## 🔧 Perintah Berguna

```bash
# Buat migration baru setelah edit models
python manage.py makemigrations

# Terapkan migration
python manage.py migrate

# Buat superuser baru
python manage.py createsuperuser

# Kumpulkan static files (untuk production)
python manage.py collectstatic

# Shell Django
python manage.py shell
```

---

**Sora LMS** © 2024 — Dibuat dengan ❤️ menggunakan Django
