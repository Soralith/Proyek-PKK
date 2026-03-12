from django.contrib import admin
from .models import Quiz, Question, Answer, QuizAttempt, StudentAnswer


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 4


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'is_published', 'time_limit', 'passing_score', 'created_at')
    list_filter = ('is_published', 'course')
    inlines = [QuestionInline]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'quiz', 'question_type', 'points', 'order')
    inlines = [AnswerInline]


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ('student', 'quiz', 'status', 'score', 'percentage', 'started_at')
    list_filter = ('status',)
