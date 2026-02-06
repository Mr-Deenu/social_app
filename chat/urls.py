from django.urls import path
from . import views

app_name = "chat"   # ✅ name nahi, app_name

urlpatterns = [
    path("", views.inbox, name="chat_inbox"),
    path("room/<int:convo_id>/", views.chat_room, name="chat_room"),
    path("share/<int:post_id>/<str:username>/", views.share_post_to_user, name="share_post_to_user"),
    path("delete/<int:msg_id>/", views.delete_message, name="delete_message"),
    path("message/<int:msg_id>/delete/", views.delete_message, name="delete_message"),
    # APIs
    path("api/messages/<int:convo_id>/", views.api_messages, name="api_messages"),
    path("api/typing/<int:convo_id>/", views.api_typing, name="api_typing"),
    path("api/typing/<int:convo_id>/set/", views.api_set_typing, name="api_set_typing"),
    
]
