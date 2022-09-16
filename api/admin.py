from django.contrib import admin
from .models import Document, PracticeLog, Tag, User, Lesson, Note


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = [
        "pk",
        "username",
        "first_name",
        "last_name",
        "is_staff",
        "staff",
        "active_in_studio",
    ]


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ["pk", "lesson_date", "lesson_time", "student", "plan"]


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ["pk", "body", "created_at"]


@admin.register(PracticeLog)
class PracticeAdmin(admin.ModelAdmin):
    list_display = ["pk", "body", "author", "created_at"]


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ["pk", "title", "author", "uploaded_at"]


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ["pk", "slug", "created_by"]