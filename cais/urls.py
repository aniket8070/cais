from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from chatbot import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path("login/", auth_views.LoginView.as_view(template_name="login.html")),
    path("", views.chat_page),
    path("upload", views.upload_pdf),
    path("chat", views.chat_message),
    path("sector", views.sector_detail),
    path('download-notes/', views.download_notes_pdf, name='download_notes'),
    path('send-email/', views.send_email_summary, name='send_email'),
]