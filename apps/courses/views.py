from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.text import slugify
from django.utils import timezone
from django.db.models import Q
from .models import Course, Module, Material, Enrollment, MaterialProgress, Category, Announcement
from .forms import CourseForm, ModuleForm, MaterialForm, AnnouncementForm
import uuid


@login_required
def course_list(request):
    query = request.GET.get('q', '')
    category_id = request.GET.get('category', '')

    if request.user.is_admin:
        courses = Course.objects.all()
    elif request.user.is_teacher:
        courses = Course.objects.filter(teacher=request.user)
    else:
        # Siswa: tampilkan kelas yang dienroll + kelas aktif lainnya
        enrolled_ids = list(Enrollment.objects.filter(
            student=request.user, is_active=True
        ).values_list('course_id', flat=True))
        from django.db.models import Q as DQ
        courses = Course.objects.filter(
            DQ(id__in=enrolled_ids) | DQ(status='active')
        ).distinct()

    if query:
        courses = courses.filter(Q(title__icontains=query) | Q(description__icontains=query))
    if category_id:
        courses = courses.filter(category_id=category_id)

    categories = Category.objects.all()

    # Untuk siswa, tandai kelas mana saja yang sudah dienroll
    enrolled_ids = []
    if request.user.is_student:
        enrolled_ids = list(Enrollment.objects.filter(
            student=request.user, is_active=True
        ).values_list('course_id', flat=True))

    return render(request, 'courses/course_list.html', {
        'courses': courses,
        'query': query,
        'categories': categories,
        'category_id': category_id,
        'enrolled_ids': enrolled_ids,
    })


@login_required
def course_detail(request, slug):
    course = get_object_or_404(Course, slug=slug)
    enrollment = None
    is_enrolled = False

    if request.user.is_student:
        enrollment = Enrollment.objects.filter(student=request.user, course=course).first()
        is_enrolled = enrollment is not None and enrollment.is_active

        if not is_enrolled and course.status != 'active':
            messages.error(request, 'Kelas ini tidak tersedia.')
            return redirect('courses:course_list')

    modules = course.modules.prefetch_related('materials').all()

    return render(request, 'courses/course_detail.html', {
        'course': course,
        'modules': modules,
        'enrollment': enrollment,
        'is_enrolled': is_enrolled,
        'announcements': course.announcements.all()[:5],
    })


@login_required
def course_create(request):
    if not (request.user.is_teacher or request.user.is_admin):
        messages.error(request, 'Hanya guru yang dapat membuat kelas.')
        return redirect('courses:course_list')

    form = CourseForm(request.POST or None, request.FILES or None)
    if request.method == 'POST':
        if form.is_valid():
            course = form.save(commit=False)
            course.teacher = request.user
            base_slug = slugify(course.title)
            slug = base_slug
            counter = 1
            while Course.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            course.slug = slug
            course.save()
            messages.success(request, 'Kelas berhasil dibuat!')
            return redirect('courses:course_detail', slug=course.slug)

    return render(request, 'courses/course_form.html', {'form': form, 'action': 'Buat'})


@login_required
def course_edit(request, slug):
    course = get_object_or_404(Course, slug=slug)
    if not (request.user == course.teacher or request.user.is_admin):
        messages.error(request, 'Akses ditolak.')
        return redirect('courses:course_list')

    form = CourseForm(request.POST or None, request.FILES or None, instance=course)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, 'Kelas berhasil diperbarui!')
            return redirect('courses:course_detail', slug=course.slug)

    return render(request, 'courses/course_form.html', {'form': form, 'action': 'Edit', 'course': course})


@login_required
def course_delete(request, slug):
    course = get_object_or_404(Course, slug=slug)
    if not (request.user == course.teacher or request.user.is_admin):
        messages.error(request, 'Akses ditolak.')
        return redirect('courses:course_list')

    if request.method == 'POST':
        course.delete()
        messages.success(request, 'Kelas berhasil dihapus.')
        return redirect('courses:course_list')

    return render(request, 'courses/course_confirm_delete.html', {'course': course})


@login_required
def manage_enrollments(request, slug):
    """Halaman kelola pendaftaran siswa — hanya admin/guru"""
    course = get_object_or_404(Course, slug=slug)
    if not (request.user == course.teacher or request.user.is_admin):
        messages.error(request, 'Akses ditolak.')
        return redirect('courses:course_detail', slug=slug)

    from apps.accounts.models import User
    # Siswa yang belum terdaftar di kelas ini
    enrolled_student_ids = Enrollment.objects.filter(
        course=course, is_active=True
    ).values_list('student_id', flat=True)
    available_students = User.objects.filter(role='student').exclude(id__in=enrolled_student_ids)
    enrollments = Enrollment.objects.filter(course=course, is_active=True).select_related('student')

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'add':
            student_ids = request.POST.getlist('student_ids')
            added = 0
            for sid in student_ids:
                student = User.objects.filter(pk=sid, role='student').first()
                if student:
                    Enrollment.objects.get_or_create(student=student, course=course, defaults={'is_active': True})
                    added += 1
            messages.success(request, f'{added} siswa berhasil didaftarkan ke kelas ini.')
            return redirect('courses:manage_enrollments', slug=slug)

        elif action == 'remove':
            enrollment_id = request.POST.get('enrollment_id')
            enrollment = Enrollment.objects.filter(pk=enrollment_id, course=course).first()
            if enrollment:
                enrollment.delete()
                messages.success(request, f'{enrollment.student.get_full_name() or enrollment.student.username} berhasil dikeluarkan dari kelas.')
            return redirect('courses:manage_enrollments', slug=slug)

    return render(request, 'courses/manage_enrollments.html', {
        'course': course,
        'enrollments': enrollments,
        'available_students': available_students,
    })

@login_required
def module_create(request, slug):
    course = get_object_or_404(Course, slug=slug)
    if not (request.user == course.teacher or request.user.is_admin):
        messages.error(request, 'Akses ditolak.')
        return redirect('courses:course_detail', slug=slug)

    form = ModuleForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        module = form.save(commit=False)
        module.course = course
        module.save()
        messages.success(request, 'Modul berhasil ditambahkan!')
        return redirect('courses:course_detail', slug=slug)

    return render(request, 'courses/module_form.html', {'form': form, 'course': course, 'action': 'Tambah'})


@login_required
def module_edit(request, pk):
    module = get_object_or_404(Module, pk=pk)
    if not (request.user == module.course.teacher or request.user.is_admin):
        messages.error(request, 'Akses ditolak.')
        return redirect('courses:course_list')

    form = ModuleForm(request.POST or None, instance=module)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Modul berhasil diperbarui!')
        return redirect('courses:course_detail', slug=module.course.slug)

    return render(request, 'courses/module_form.html', {
        'form': form, 'course': module.course, 'module': module, 'action': 'Edit'
    })


@login_required
def module_delete(request, pk):
    module = get_object_or_404(Module, pk=pk)
    course = module.course
    if not (request.user == course.teacher or request.user.is_admin):
        messages.error(request, 'Akses ditolak.')
        return redirect('courses:course_list')

    if request.method == 'POST':
        module.delete()
        messages.success(request, 'Modul berhasil dihapus.')
    return redirect('courses:course_detail', slug=course.slug)


@login_required
def material_create(request, module_pk):
    module = get_object_or_404(Module, pk=module_pk)
    if not (request.user == module.course.teacher or request.user.is_admin):
        messages.error(request, 'Akses ditolak.')
        return redirect('courses:course_list')

    form = MaterialForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        material = form.save(commit=False)
        material.module = module
        material.save()
        messages.success(request, 'Materi berhasil ditambahkan!')
        return redirect('courses:course_detail', slug=module.course.slug)

    return render(request, 'courses/material_form.html', {
        'form': form, 'module': module, 'action': 'Tambah'
    })


@login_required
def material_detail(request, pk):
    material = get_object_or_404(Material, pk=pk)
    course = material.module.course

    if request.user.is_student:
        enrollment = get_object_or_404(Enrollment, student=request.user, course=course, is_active=True)

    if request.user.is_student:
        progress, _ = MaterialProgress.objects.get_or_create(
            student=request.user, material=material
        )
        if not progress.is_completed:
            progress.is_completed = True
            progress.completed_at = timezone.now()
            progress.save()
            update_course_progress(request.user, course)

    return render(request, 'courses/material_detail.html', {'material': material, 'course': course})


@login_required
def material_edit(request, pk):
    material = get_object_or_404(Material, pk=pk)
    if not (request.user == material.module.course.teacher or request.user.is_admin):
        messages.error(request, 'Akses ditolak.')
        return redirect('courses:course_list')

    form = MaterialForm(request.POST or None, request.FILES or None, instance=material)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Materi berhasil diperbarui!')
        return redirect('courses:course_detail', slug=material.module.course.slug)

    return render(request, 'courses/material_form.html', {
        'form': form, 'module': material.module, 'material': material, 'action': 'Edit'
    })


@login_required
def material_delete(request, pk):
    material = get_object_or_404(Material, pk=pk)
    course = material.module.course
    if not (request.user == course.teacher or request.user.is_admin):
        messages.error(request, 'Akses ditolak.')
        return redirect('courses:course_list')

    if request.method == 'POST':
        material.delete()
        messages.success(request, 'Materi berhasil dihapus.')
    return redirect('courses:course_detail', slug=course.slug)


@login_required
def announcement_create(request, slug):
    course = get_object_or_404(Course, slug=slug)
    if not (request.user == course.teacher or request.user.is_admin):
        messages.error(request, 'Akses ditolak.')
        return redirect('courses:course_detail', slug=slug)

    form = AnnouncementForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        ann = form.save(commit=False)
        ann.course = course
        ann.author = request.user
        ann.save()
        messages.success(request, 'Pengumuman berhasil diterbitkan!')
        return redirect('courses:course_detail', slug=slug)

    return render(request, 'courses/announcement_form.html', {'form': form, 'course': course})


def update_course_progress(student, course):
    total_materials = Material.objects.filter(
        module__course=course, is_published=True
    ).count()
    if total_materials == 0:
        return
    completed = MaterialProgress.objects.filter(
        student=student,
        material__module__course=course,
        is_completed=True
    ).count()
    progress = (completed / total_materials) * 100
    enrollment = Enrollment.objects.filter(student=student, course=course).first()
    if enrollment:
        enrollment.progress = round(progress, 2)
        if progress >= 100:
            enrollment.completed_at = timezone.now()
        enrollment.save()
