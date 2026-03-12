from django.db import models
from apps.accounts.models import User


class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Kategori'
        verbose_name_plural = 'Kategori'
        ordering = ['name']

    def __str__(self):
        return self.name


class Course(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Aktif'),
        ('archived', 'Diarsipkan'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=220)
    description = models.TextField()
    cover_image = models.ImageField(upload_to='courses/covers/', null=True, blank=True)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='taught_courses')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    enrollment_key = models.CharField(max_length=50, blank=True, help_text='Kode untuk mendaftar ke kelas')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Kelas'
        verbose_name_plural = 'Kelas'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_student_count(self):
        return self.enrollments.filter(is_active=True).count()

    def get_completion_rate(self):
        enrollments = self.enrollments.filter(is_active=True)
        if not enrollments.exists():
            return 0
        completed = enrollments.filter(progress=100).count()
        return round((completed / enrollments.count()) * 100)


class Module(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Modul'
        verbose_name_plural = 'Modul'
        ordering = ['order', 'created_at']

    def __str__(self):
        return f"{self.course.title} - {self.title}"


class Material(models.Model):
    TYPE_CHOICES = [
        ('video', 'Video'),
        ('document', 'Dokumen'),
        ('presentation', 'Presentasi'),
        ('link', 'Tautan Eksternal'),
        ('text', 'Teks/Artikel'),
    ]

    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='materials')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    material_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='document')
    file = models.FileField(upload_to='courses/materials/', null=True, blank=True)
    url = models.URLField(blank=True, help_text='URL untuk video/tautan eksternal')
    content = models.TextField(blank=True, help_text='Konten teks/artikel')
    order = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Materi'
        verbose_name_plural = 'Materi'
        ordering = ['order', 'created_at']

    def __str__(self):
        return f"{self.module.title} - {self.title}"

    def get_file_size(self):
        if self.file:
            try:
                return self.file.size
            except:
                return 0
        return 0

    def get_file_size_display(self):
        size = self.get_file_size()
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size // 1024} KB"
        else:
            return f"{size // (1024 * 1024)} MB"


class Enrollment(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    progress = models.FloatField(default=0)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Pendaftaran'
        verbose_name_plural = 'Pendaftaran'
        unique_together = ('student', 'course')

    def __str__(self):
        return f"{self.student.username} - {self.course.title}"


class MaterialProgress(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('student', 'material')

    def __str__(self):
        return f"{self.student.username} - {self.material.title}"


class Announcement(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='announcements')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Pengumuman'
        verbose_name_plural = 'Pengumuman'
        ordering = ['-created_at']

    def __str__(self):
        return self.title
