from rest_framework.permissions import BasePermission


class ProductPermission(BasePermission):
    def has_permission(self,request,view):
        if request.method == 'GET':
            return True
        if request.method == 'POST':
            return request.user.is_authenticated
        if  request.method in ["PUT","PATCH"]:
            return request.user.is_authenticated
        if request.method == "DELETE":
            return request.user.is_superuser
        return False