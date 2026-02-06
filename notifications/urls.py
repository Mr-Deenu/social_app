from django.urls import path
from . import views

urlpatterns = [
    path("", views.notifications_list, name="notifications_list"),
    path("read/<int:notif_id>/", views.mark_read, name="notif_read"),
    path("read-all/", views.mark_all_read, name="notif_read_all"),
    path("mark-read/", views.mark_notifications_read, name="mark_notifications_read"),
    path("open/<int:notif_id>/", views.open_notification, name="open_notification"),

]
