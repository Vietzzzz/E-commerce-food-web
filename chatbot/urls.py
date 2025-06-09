# chatbot/urls.py
from django.urls import path
from . import views

app_name = "chatbot"

urlpatterns = [
    path("", views.chatbot_view, name="chatbot_interface"),
    path("get-response/", views.get_chatbot_response, name="get_chatbot_response"),
]
