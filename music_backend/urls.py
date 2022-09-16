"""music_backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from api import views as api_views
from rest_framework.routers import SimpleRouter


router = SimpleRouter()
router.register(r"note", api_views.NoteViewSet)
router.register(r"practices", api_views.PracticeLogViewSet)
router.register(r"tags", api_views.TagView)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
    path("api-auth/", include("rest_framework.urls")),
    path("auth/", include("djoser.urls")),
    path("auth/", include("djoser.urls.authtoken")),
    path(
        "auth/users/",
        api_views.DjoserUserViewSet.as_view({"get": "list"}),
        name="register-new-user",
    ),
    path("auth/users/me/", api_views.ProfileViewSet.as_view(), name="profile"),
    path("api/upcoming/", api_views.LessonViewSet.as_view(), name="lesson-list"),
    path("api/lessons/", api_views.LessonViewSet.as_view(), name="lesson-add"),
    path(
        "api/assignments/<int:student_pk>/",
        api_views.StudentLessonsListViewSet.as_view(),
        name="assignments-list",
    ),
    path(
        "api/lessons/<int:pk>/",
        api_views.LessonDetailViewSet.as_view(),
        name="lesson-detail",
    ),
    path(
        "api/assignments/<int:student_pk>/previous/<int:pk>/",
        api_views.PreviousLessonViewSet.as_view(),
        name="lesson-previous",
    ),
    path(
        "staff/studio/",
        api_views.StudioViewSet.as_view(),
        name="instructor-studio",
    ),
    path(
        "staff/studio/<int:pk>/",
        api_views.RemoveStudentFromStudio.as_view(),
        name="instructor-remove",
    ),
    path(
        "api/users/<int:pk>/",
        api_views.SharedProfileViewSet.as_view({"get": "retrieve"}),
        name="shared-profile",
    ),
    path(
        "api/documents/",
        api_views.DocumentCreateView.as_view({"get": "list", "post": "create"}),
        name="documents-create",
    ),
    path(
        "api/documents/<int:pk>/",
        api_views.DocumentDetailViewSet.as_view(
            {"get": "retrieve", "delete": "destroy", "patch": "partial_update"}
        ),
        name="document-details",
    ),
    path(
        "api/documents/<int:pk>/upload/",
        api_views.FileUploadView.as_view(),
        name="document-update",
    ),
    path(
        "api/users/students/<int:pk>/",
        api_views.StudentSignupViewSet.as_view({"post": "create"}),
        name="student-signup",
    ),
    path("api/mail/send/", api_views.EmailViewSet.as_view(), name="send-email"),
]