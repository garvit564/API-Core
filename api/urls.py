from django.urls import path

from .views import (
    ProductListView,
    ProductDetailView
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView
)


urlpatterns = [
    path("login/", TokenObtainPairView.as_view()),
    path("token/refresh/", TokenRefreshView.as_view()),

    path(
        "products/",
        ProductListView.as_view()
    ),

    path(
        "products/<int:pk>/",
        ProductDetailView.as_view()
    ),

]