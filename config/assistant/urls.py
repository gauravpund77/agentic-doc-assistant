from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView, LoginView, LogoutView, ProfileView,
    UploadDocumentView, AskQuestionView,
    ChatHistoryView, NewSessionView, HealthCheckView
)

urlpatterns = [
    # Auth
    path('auth/register/', RegisterView.as_view()),
    path('auth/login/', LoginView.as_view()),
    path('auth/logout/', LogoutView.as_view()),
    path('auth/refresh/', TokenRefreshView.as_view()),
    path('auth/profile/', ProfileView.as_view()),

    # Documents
    path('upload/', UploadDocumentView.as_view()),

    # Chat
    path('session/new/', NewSessionView.as_view()),
    path('ask/', AskQuestionView.as_view()),
    path('history/<str:session_id>/', ChatHistoryView.as_view()),

    # Health
    path('health/', HealthCheckView.as_view()),
]