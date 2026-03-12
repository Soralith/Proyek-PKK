from django.contrib import admin
from .models import Assignment, Submission


class SubmissionInline(admin.TabularInline):
    model = Submission
    extra = 0
    readonly_fields = ('submitted_at',)


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'due_date', 'max_score', 'is_published')
    list_filter = ('is_published', 'course')
    search_fields = ('title', 'course__title')
    inlines = [SubmissionInline]


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('student', 'assignment', 'status', 'score', 'submitted_at')
    list_filter = ('status',)
    search_fields = ('student__username', 'assignment__title')
