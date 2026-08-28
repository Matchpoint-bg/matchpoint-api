from django.urls import include, path
from internal.views import user_has_access_to_club

urlpatterns = [path("club_access/<int:pk>/", user_has_access_to_club)]
