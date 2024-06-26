from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Q, OuterRef, Subquery

from ticketapp.models import User,  Profile, ChatMessage, CreateTask

from ticketapp.serializers import ProfileSerializer, MyTokenObtainPairSerializer, RegisterSerializer, CreateTaskSerializer, MessageSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from asgiref.sync import sync_to_async
from django.shortcuts import render, reverse, get_object_or_404
from django.views.generic import TemplateView
from django.http import HttpResponseRedirect
from .models import User, Room, ChatMessage

def index(request):
    return render(request, "ticketapp/index.html")
def room(request, room_name):
    return render(request, "chat/room.html", {"room_name": room_name})
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer


# Get All Routes

@api_view(['GET'])
def getRoutes(request):
    routes = [
        '/api/token/',
        '/api/register/',
        '/api/token/refresh/'
    ]
    return Response(routes)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def testEndPoint(request):
    if request.method == 'GET':
        data = f"Congratulation {request.user}, your API just responded to GET request"
        return Response({'response': data}, status=status.HTTP_200_OK)
    elif request.method == 'POST':
        text = "Hello buddy"
        data = f'Congratulation your API just responded to POST request with text: {text}'
        return Response({'response': data}, status=status.HTTP_200_OK)
    return Response({}, status.HTTP_400_BAD_REQUEST)





class MyInbox(generics.ListAPIView):
    serializer_class = MessageSerializer

    def get_queryset(self):
        user_id = self.kwargs['user_id']

        messages = ChatMessage.objects.filter(
            id__in=Subquery(
                User.objects.filter(
                    Q(sender__reciever=user_id) |
                    Q(reciever__sender=user_id)
                ).distinct().annotate(
                    last_msg=Subquery(
                        ChatMessage.objects.filter(
                            Q(sender=OuterRef('id'), reciever=user_id) |
                            Q(reciever=OuterRef('id'), sender=user_id)
                        ).order_by('-id')[:1].values_list('id', flat=True)
                    )
                ).values_list('last_msg', flat=True).order_by("-id")
            )
        ).order_by("-id")

        return messages


class GetMessages(generics.ListAPIView):
    serializer_class = MessageSerializer

    def get_queryset(self):
        sender_id = self.kwargs['sender_id']
        self.id_ = self.kwargs['reciever_id']
        reciever_id = self.id_
        messages = ChatMessage.objects.filter(sender__in=[sender_id, reciever_id],
                                              reciever__in=[sender_id, reciever_id])
        return messages


class SendMessages(generics.CreateAPIView):
    serializer_class = MessageSerializer


class ProfileDetail(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    queryset = Profile.objects.all()
    permission_classes = [IsAuthenticated]


class SearchUser(generics.ListAPIView):
    serializer_class = ProfileSerializer
    queryset = Profile.objects.all()

    # permission_classes=[IsAuthenticated]
    def list(self, request, *args, **kwargs):
        username = self.kwargs['username']
        logged_in_user = self.request.user
        users = Profile.objects.filter(Q(user__username__icontains=username) |
                                       Q(full_name__icontains=username) |
                                       Q(user__email__icontains=username))
        # ~Q(user=logged_in_user)
        # )
        if not users.exists():
            return Response(
                {
                    'detail': "No users found."},
                status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(users, many=True)
        return Response(serializer.data)


        return Response(serializer.data)
class TaskList(generics.CreateAPIView, generics.ListAPIView):
    serializer_class = CreateTaskSerializer
    queryset = CreateTask.objects.all()
    # permission_classes = [IsAuthenticated]


class TaskDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CreateTaskSerializer
    queryset = CreateTask.objects.all()
    # permission_classes = [IsAuthenticated]




def index(request):
    if request.method == "POST":
        name = request.POST.get("name", None)
        if name:
            room = Room.objects.create(name=name, host=request.user)
            print(room.pk)
            return HttpResponseRedirect(reverse("ticketapp:room", kwargs={"pk": room.pk}))
    return render(request, 'ticketapp/index.html')


def room(request, pk):
    room: Room = get_object_or_404(Room, pk=pk)
    messages:ChatMessage=ChatMessage.objects.filter(room=room.pk)
    print(messages)
    print('here')
    return render(request, 'ticketapp/room.html', {
        "room": room,
        'messages':messages
    })


def test(request):
    return render(request, 'ticketapp/test.html')  
def messagelist(request):
    return render(request, 'ticketapp/1.html')  