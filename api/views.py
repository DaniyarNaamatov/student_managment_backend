from datetime import date, timedelta
from djoser.views import UserViewSet as DjoserUserViewSet

from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.contrib.postgres.search import SearchVector
from django.db.models import Q
from rest_framework.generics import CreateAPIView, ListAPIView, ListCreateAPIView, RetrieveUpdateAPIView,RetrieveUpdateDestroyAPIView

from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ParseError
from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response
from .permissions import IsStaffOfStudent
from .models import Document, PracticeLog, Tag, User, Lesson, Note
from api.serializers import *


class UserViewSet(DjoserUserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_serializer_class(self):
        serializer_class = self.serializer_class
        if not self.request.user.is_staff:
            serializer_class = StudentProfileSerializers
        return serializer_class

class SharedProfileViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = StudentProfileSerializers
    permission_classes = [IsAuthenticated]


class LessonViewSet(ListCreateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = AddLessonSerializers
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff == True:
            queryset = Lesson.objects.filter(
                author=self.request.user, lesson_date=date.today()
            )
        if self.request.user.is_staff == False:
            queryset = Lesson.objects.filter(student=self.request.user).order_by(
                "-lesson_date", "-lesson_time"
            )
        return queryset

    def get_serializer_class(self):
        serializer_class = self.serializer_class
        if self.request.method == "GET":
            serializer_class = ListLessonsSerializer
        if self.request.method == "POST":
            serializer_class = AddLessonSerializers
        if self.request.user.is_staff == False:
            serializer_class = StudentLessonSerializer
        return serializer_class

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


    def put(self, request, pk, format=None):
        lesson = self.get_object(pk)
        serializer = LessonSerializer(lesson, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StudentLessonsListViewSet(ListAPIView):
    queryset = Lesson.objects.all()
    serializer_class = StudentLessonSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Lesson.objects.filter(student=self.kwargs["student_pk"]).order_by(
            "-lesson_date", "-lesson_time"
        )
        return queryset


class PreviousLessonViewSet(ListAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        lesson = get_object_or_404(Lesson, pk=self.kwargs["pk"])
        queryset = (
            Lesson.objects.filter(student=self.kwargs["student_pk"])
            .order_by("-lesson_date", "-lesson_time")
            .exclude(lesson_date__gt=lesson.lesson_date)[:5]
        )
        return queryset


class LessonDetailViewSet(RetrieveUpdateDestroyAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class ProfileViewSet(RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = StudentProfileSerializers

    def get_serializer_class(self):
        serializer_class = self.serializer_class
        if self.request.user.is_staff == True:
            serializer_class = ProfileSerializersBackends
        return serializer_class


class NoteViewSet(ModelViewSet):
    queryset = Note.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = NoteSerializersBackends

    def perform_create(self, serializer):
        serializer.save()

class StudioViewSet(ListAPIView):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated, IsStaffOfStudent]
    serializers_class = StudioSerializers

    def get_queryset(self):
        queryset = self.request.user.students.filter(active_in_studio=True)
        if self.request.query_params.get("search"):
            search_term = self.request.query_params.get("search")
            queryset = (
                self.request.user.students.filter(active_in_studio=True)
                .annotate(search=SearchVector("first_name", "last_name", "username"))
                .filter(search_icontains=search_term)
            )
            return queryset
        return queryset


class PracticeLogViewSet(ModelViewSet):
    queryset = PracticeLog.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = PracticeLogSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class DocumentCreateView(ModelViewSet):
    queryset = Document.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = DocumentSerializers

    def get_queryset(self):
        queryset = self.request.user.documents.all()
        if self.request.query_params.get("search"):
            search_term = self.request.query_params.get("search")
            queryset = (
                self.request.user.documents.all()
                .annotate(search=SearchVector("title", "students", "tags"))
                .filter(search_icontains=search_term)
            )
            return queryset
        if self.request.user.is_staff == True:
            queryset = Document.objects.filter(author=self.request.user)
        if self.request.user.is_staff == False:
            queryset = Document.objects.filter(students=self.request.user)
        return queryset

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)



class StudentSignupViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = StudentSignupSerializer
    permission_classes = [AllowAny]


    def perform_create(self, serializer):
        is_staff = False
        staff = User.objects.get(pk=self.kwargs["pk"])
        username = serializer.validated_data["username"]
        serializer.save(is_staff=is_staff, staff=staff)
        user = User.objects.get(username=username)
        user.set_password(self.request.data["password"])
        user.save()



class FileUploadView(RetrieveUpdateAPIView):
    parser_classes = (FileUploadParser, )

    def put(self, request, pk, format=None):
        if "file" not in request.data:
            raise ParseError("Empty content")

        f = request.data["file"]
        document = get_object_or_404(Document, pk=pk)
        document.upload.save(f.name, f, save=True)
        return Response(status=status.HTTP_201_CREATED)


class DocumentDetailViewSet(ModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializers
    permission_classes = [IsAuthenticated]


    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


    def partial_update(self, request, *args, **kwargs):
        document = get_object_or_404(Document, pk=self.kwargs.get("pk"))
        title = document.title
        kwargs["partial"] = True
        if self.request.data.get("tags") != None:
            add_tags = self.request.data.get("tags")
            for tag in add_tags:
                tags = document.tags.add(tag)
            return self.update(
                request,
                title,
                tags,
                *args,
                **kwargs,
            )
        if self.request.data.get("students") != None:
            add_students = self.request.data.get("students")
            for student in add_students:
                students = document.students.add(student)
            return self.update(
                request,
                title,
                students,
                *args,
                **kwargs,
            )
        return self.update(
            request,
            title,
            *args,
            **kwargs,

        )


class TagView(ModelViewSet):
    queryset = Tag.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = TagSerializers



class EmailViewSet(CreateAPIView):
    serializer_class = EmailCreateSerializer()

    def post(self, request, *args, **kwargs):
        serializer = EmailCreateSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            email = data.get("email")
            name = data.get("name")
            staff_url = data.get("staff_url")
            send_mail(
            "Привет,, {} sзарегистрируйтесь Educate.kg".format(name),
            "Вот ваша персональная ссылка для регистрации у вашего инструктора: {}".format(
                staff_url
            ),
            "mrnaamatov79@gmail.com",
            [
                email,
            ],
            fail_silently=False,
        )
            return Response({"успешно": "Отправлено"})
        return Response({"успешно": "Не отправлено"}, status=status.HTTP_400_BAD_REQUEST)


class RemoveStudentFromStudio(RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = StudentLessonSerializer

    def partial_update(self, request, *args, **kwargs):
        kwargs["partial"] = True
        student = get_object_or_404(User, pk=self.kwargs.get("pk"))
        return self.update(
            request,
            student,
            *args,
            **kwargs
        )

