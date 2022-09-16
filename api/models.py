from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractUser
from ckeditor.fields import RichTextField
from django.db.models.deletion import CASCADE




class User(AbstractUser):
    USER_CREATE_PASSWORD_RETYPE = True
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = [
        "first_name",
        "last_name",
        "email",
        "phone",
        "is_staff",
        "emergency_contact_name",
        "emergency_contact_phone",

    ]

    phone_regex = RegexValidator(
        regex=r"^\+?1?\d{9,15}$",
        message="Phone number must be entered in the format: '+996'. Up to 15 digits allowed.",
    )
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(blank=True, null=False)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    phone = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    emergency_contact_name = models.CharField(max_length=100)
    emergency_contact_phone = models.CharField(validators=[phone_regex], max_length=20)
    staff = models.ForeignKey("self", null=True, on_delete=models.CASCADE, related_name="students" )
    is_staff = models.BooleanField(default=True)
    active_in_studio = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Абонент"
        verbose_name_plural = "Абоненты"
        ordering = ["-created_at"]

    def __repr__(self):
        return f"{self.username}"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"



class Tag(models.Model):
    slug = models.CharField(max_length=120, unique=True, null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tags")



    def __str__(self):
        return self.slug



    def __repr__(self):
        return f"<Tag={self.slug}"

    class Meta:
        verbose_name = "Тэг"
        verbose_name_plural = "Тэги"




class Lesson(models.Model):
    lesson_date = models.DateField(auto_now_add=False, auto_now=False)
    lesson_time = models.TimeField(auto_now_add=False, auto_now=False)
    plan = RichTextField()
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="lesson")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="lessons")
    created_at = models.DateTimeField(auto_now_add=True, blank=True)


    class Meta:
        verbose_name = "Урок"
        verbose_name_plural = "Уроки"
        ordering = ["lesson_date", "lesson_time"]

    def __str__(self):
        return f"{self.lesson_date} {self.student}"



class Note(models.Model):
    body = RichTextField()
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="note")
    is_assignment = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"{self.body}"





class PracticeLog(models.Model):
    body = RichTextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="practice")
    time_practiced = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)


    class Meta:
        verbose_name = "Практика"
        verbose_name_plural = "Практики"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.body}"


class Document(models.Model):
    uploaded = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=255)
    uploaded_at = models.FileField(blank=True, null=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="documents", blank=True, null=True)
    students = models.ManyToManyField(User, blank=True, related_name="documents_students")
    tags = models.ManyToManyField(Tag, blank=True, related_name="documents_tags")

    class Meta:
        verbose_name = "Документ"
        verbose_name_plural = "Документы"
        ordering = ["-uploaded_at"]




