from rest_framework import permissions



class IsStaffAndLessonOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff == True:
            return True
        if obj.author == request.user:
            return True
        return False


class IsStaffOfStudent(permissions.BasePermission):
    message = "must be the staff of this student."

    def has_permission(self, request, view):
        if request.user.is_staff:
            return True
        return False

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        if request.user.is_staff == True:
            return True
        if obj.author == request.user:
            return True
        if obj.staff != request.user:
            return False
        return False

class IsStudentStaff(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return True
        return False

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        if request.user in obj.author.student.all():
            return True
        return False

class IsStudentOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return True
        return False

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        if request.user.is_staff == False:
            return True
        if obj.author == request.user:
            return True
        return False
