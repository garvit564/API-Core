from django.urls import path

from api3.views import (
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
        "products/<int:id>/",
        ProductDetailView.as_view()
    ),
]