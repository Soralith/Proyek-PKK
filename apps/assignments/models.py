from django.db import models
from apps.accounts.models import User
from apps.courses.models import Course


class Assignment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='assignments')
    title = models.CharField(max_length=200)
    description = models.TextField()
    attachment = models.FileField(upload_to='assignments/files/', null=True, blank=True)
    due_date = models.DateTimeField()
    max_score = models.PositiveIntegerField(default=100)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Tugas'
        verbose_name_plural = 'Tugas'
        ordering = ['-due_date']

    def __str__(self):
        return f"{self.course.title} - {self.title}"

    def is_overdue(self):
        from django.utils import timezone
        return timezone.now() > self.due_date

    def get_submission_count(self):
        return self.submissions.count()


class Submission(models.Model):
    STATUS_CHOICES = [
        ('submitted', 'Dikumpulkan'),
        ('graded', 'Dinilai'),
        ('returned', 'Dikembalikan'),
        ('late', 'Terlambat'),
    ]

    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submissions')
    file = models.FileField(upload_to='assignments/submissions/', null=True, blank=True)
    text_answer = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='submitted')
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    feedback = models.TextField(blank=True)
    graded_at = models.DateTimeField(null=True, blank=True)
    graded_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='graded_submissions'
    )

    class Meta:
        verbose_name = 'Pengumpulan Tugas'
        verbose_name_plural = 'Pengumpulan Tugas'
        unique_together = ('assignment', 'student')
        ordering = ['-submitted_at']

    def __str__(self):
        return f"{self.student.username} - {self.assignment.title}"

    def get_score_display_value(self):
        if self.score is not None:
            return f"{self.score}/{self.assignment.max_score}"
        return "Belum dinilai"

    def get_percentage(self):
        if self.score is not None:
            return round((float(self.score) / self.assignment.max_score) * 100, 1)
        return None
