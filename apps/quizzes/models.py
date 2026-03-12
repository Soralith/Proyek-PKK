from django.db import models
from apps.accounts.models import User
from apps.courses.models import Course


class Quiz(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='quizzes')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    time_limit = models.PositiveIntegerField(default=60, help_text='Waktu dalam menit (0 = tidak terbatas)')
    passing_score = models.PositiveIntegerField(default=70, help_text='Nilai minimum lulus (%)')
    max_attempts = models.PositiveIntegerField(default=1, help_text='0 = tidak terbatas')
    shuffle_questions = models.BooleanField(default=False)
    show_results = models.BooleanField(default=True)
    is_published = models.BooleanField(default=False)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Kuis/Ujian'
        verbose_name_plural = 'Kuis/Ujian'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.course.title} - {self.title}"

    def get_question_count(self):
        return self.questions.count()

    def get_total_points(self):
        return sum(q.points for q in self.questions.all())


class Question(models.Model):
    TYPE_CHOICES = [
        ('multiple_choice', 'Pilihan Ganda'),
        ('true_false', 'Benar/Salah'),
        ('short_answer', 'Jawaban Singkat'),
        ('essay', 'Esai'),
    ]

    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    question_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='multiple_choice')
    points = models.PositiveIntegerField(default=1)
    order = models.PositiveIntegerField(default=0)
    explanation = models.TextField(blank=True, help_text='Penjelasan jawaban (ditampilkan setelah kuis)')

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f"Q{self.order}: {self.text[:50]}"


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    text = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.text} ({'✓' if self.is_correct else '✗'})"


class QuizAttempt(models.Model):
    STATUS_CHOICES = [
        ('in_progress', 'Sedang Dikerjakan'),
        ('completed', 'Selesai'),
        ('abandoned', 'Ditinggalkan'),
    ]

    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='attempts')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_attempts')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress')
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Percobaan Kuis'
        verbose_name_plural = 'Percobaan Kuis'
        ordering = ['-started_at']

    def __str__(self):
        return f"{self.student.username} - {self.quiz.title} - {self.status}"

    def is_passed(self):
        if self.percentage is None:
            return False
        return float(self.percentage) >= self.quiz.passing_score


class StudentAnswer(models.Model):
    attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE, related_name='student_answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_answer = models.ForeignKey(Answer, on_delete=models.SET_NULL, null=True, blank=True)
    text_answer = models.TextField(blank=True)
    is_correct = models.BooleanField(null=True, blank=True)
    points_earned = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    class Meta:
        unique_together = ('attempt', 'question')
