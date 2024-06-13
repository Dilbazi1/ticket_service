from ticketapp.apps import TicketappConfig
from django.urls import path
from ticketapp import views

from rest_framework_simplejwt.views import (
    TokenRefreshView,
)
app_name = TicketappConfig.name
urlpatterns = [
    path('room/<int:pk>/', views.room, name='room'),
    path('', views.index, name='index'),
    # path("", views.index, name="index"),
    # path("<str:room_name>/", views.room, name="room"),
    path('token/', views.MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', views.RegisterView.as_view(), name='auth_register'),
    path('test/', views.testEndPoint, name='test'),
    path('/getroutes', views.getRoutes),



    path("my-messages/<user_id>/", views.MyInbox.as_view()),
    path("get-messages/<sender_id>/<reciever_id>/", views.GetMessages.as_view()),
    path("send-messages/", views.SendMessages.as_view()),
    path("tasklist/", views.TaskList.as_view()),
    path("taskdetail/<int:pk>", views.TaskDetail.as_view()),

    # Get profile
    path("profile/<int:pk>/", views.ProfileDetail.as_view()),
    path("search/<username>/", views.SearchUser.as_view()),
    path('test1/', views.test),
    path('1/',views.messagelist)
    
]

    
