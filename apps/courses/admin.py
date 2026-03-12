from django.contrib import admin
from .models import Course, Module, Material, Enrollment, Category, Announcement


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)


class ModuleInline(admin.TabularInline):
    model = Module
    extra = 1


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'teacher', 'category', 'status', 'created_at')
    list_filter = ('status', 'category')
    search_fields = ('title', 'teacher__username')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ModuleInline]


class MaterialInline(admin.TabularInline):
    model = Material
    extra = 1


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order')
    inlines = [MaterialInline]


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'enrolled_at', 'progress', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('student__username', 'course__title')


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'author', 'created_at')
