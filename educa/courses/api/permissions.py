from rest_framework.permissions import BasePermission


class IsEnrolled(BasePermission):
    # 判断该学生是否注册该课程
    def has_object_permission(self, request, view, obj):
        return obj.students.filter(id=request.user.id).exists()
