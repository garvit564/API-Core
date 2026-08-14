"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)


urlpatterns = [

    path("admin/", admin.site.urls),

    path("api/",include("api.urls")),
    path("api1/", include("api1.urls")),
    path("api2/", include("api2.urls")),
    path("api3/", include("api3.urls")),
    path("api4/", include("api4.urls")),
    path("api5/", include("api5.urls")),
    path("api6/", include("api6.urls")),
    path("api7/", include("api7.urls")),
    path("api8/", include("api8.urls")),

    path("api/schema/",SpectacularAPIView.as_view(),name="schema"),

    # Swagger UI
    path("api/docs/",SpectacularSwaggerView.as_view(url_name="schema"),name="swagger-ui"),
    

]