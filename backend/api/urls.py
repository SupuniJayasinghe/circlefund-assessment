from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView
from .views import MeView, RegisterView
from . import views

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='login'),
    path('me/', MeView.as_view(), name='me'),
    path("circles/create/", views.create_circle),
    path("circles/join/", views.join_circle),   
    path("rounds/contribute/", views.contribute),
    path("rounds/approve/", views.approve_payout),
    path(
"rounds/current/",
views.current_round
)
]