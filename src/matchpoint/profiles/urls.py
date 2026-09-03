from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import AvatarViewset


router = DefaultRouter()
router.register(r"avatar", AvatarViewset)

urlpatterns = [path("<int:pk>/", include(router.urls))]
