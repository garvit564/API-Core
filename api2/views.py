from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from rest_framework.permissions import BasePermission
from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView
)
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import ProductSerializer
from api.models import Product


class ProductPermission(BasePermission):
    def has_permission(self,request,view):
        if request.method == "GET":
            return True
        if request.method == "POST":
            return request.user.is_authenticated
        if request.method in ["PUT","PATCH"]:
            return request.user.is_authenticated
        if request.method == "DELETE":
            return request.user.is_superuser
        return False
    
    def has_object_permission(self, request, view, obj):

        if request.method in ["PUT", "PATCH"]:
            return (
                request.user.is_superuser
                or obj.owner == request.user
            )

        return True


# class ProductListView(ListCreateAPIView):
#     queryset = Product.objects.all()
#     permission_classes = [ProductPermission]
#     serializer_class = ProductSerializer

# class ProductDetailView(RetrieveUpdateDestroyAPIView):
#     queryset = Product.objects.all()
#     permission_classes = [ProductPermission]
#     serializer_class = ProductSerializer

class ProductListView(APIView):
    permission_classes = [ProductPermission]

    def get(self,request):
        products = Product.objects.all()
        serializer = ProductSerializer(products,many=True)
        return Response(serializer.data)
    def post(self,request):
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(owner=request.user)
            return Response(serializer.data,status=201)
        return Response(serializer.errors,status=400)
    
    
class ProductDetailView(APIView):    
    permission_classes = [ProductPermission]

    def put(self,request,id):
        products = Product.objects.get(id=id)
        self.check_object_permissions(request, products)
        serializer = ProductSerializer(products,data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=200)
        return Response(serializer.errors,status=400)
    def patch(self,request,id):
            products = Product.objects.get(id=id)
            self.check_object_permissions(request, products)
            serializer = ProductSerializer(products,data=request.data,partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data,status=200)
            return Response(serializer.errors,status=400)
    def delete(self,request,id):
        products = Product.objects.get(id=id)
        products.delete()
        return Response({"message:product deleted sucsessfully"},status=204)




