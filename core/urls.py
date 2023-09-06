"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from rest_framework.routers import DefaultRouter

from requisitions.views import (
    ProjectViewSet,
    DeliveryViewSet,
    RequisitionViewSet,
    RequisitionEventViewSet,
    RequisitionStatusViewSet,
    RequisitionTagViewSet,
    StatisticsViewSet
)

from users.views import (
    UserAuthenticationView,
    ProfileViewSet,
    TokenVerifierView,
    InstituteViewSet,
    DepartmentViewSet
)


router = DefaultRouter()

router.register(r"requisitions", RequisitionViewSet, basename="requisition")
router.register(r"events", RequisitionEventViewSet, basename="events")
router.register(r"status", RequisitionStatusViewSet, basename="status")
router.register(r"tags", RequisitionTagViewSet, basename="tags")
router.register(r"profiles", ProfileViewSet, basename="profiles")
router.register(r"projects", ProjectViewSet, basename="projects")
router.register(r"deliveries", DeliveryViewSet, basename="deliveries")
router.register(r"departments", DepartmentViewSet, basename="departments")
router.register(r"institutes", InstituteViewSet, basename="institutes")
router.register(r"statistics", StatisticsViewSet, basename="statistics")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
    path("get-token/", UserAuthenticationView.as_view(), name="get-token"),
    path("verify-token/", TokenVerifierView.as_view(), name="verify-token"),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
