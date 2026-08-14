from django.urls import path

from api4.views import (
    ProductListView,
    ProductDetailView
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView
)
from .views import LoginView
from .views import LogoutView


urlpatterns = [
    path("login/", LoginView.as_view()),
    path("logout/",LogoutView.as_view()),
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