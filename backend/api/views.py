from rest_framework import generics, status
from rest_framework.response import Response
from django.contrib.auth.models import User
from .serializers import RegisterSerializer
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import Circle, Membership
from .serializers import CircleSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({'username': request.user.username})

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response(
            {
                'message': 'User created successfully',
                'username': user.username,
            },
            status=status.HTTP_201_CREATED
        )

# create circle API   
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_circle(request):
    serializer = CircleSerializer(data=request.data)

    if serializer.is_valid():
        circle = serializer.save(admin=request.user)

        Membership.objects.create(
            user=request.user,
            circle=circle,
            position=1
        )

        return Response(CircleSerializer(circle).data, status=201)

    return Response(serializer.errors, status=400)

# join circle API
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def join_circle(request):
    invite_code = request.data.get("invite_code")

    try:
        circle = Circle.objects.get(invite_code=invite_code)
    except Circle.DoesNotExist:
        return Response({"error": "Invalid invite code"}, status=404)

    if Membership.objects.filter(circle=circle, user=request.user).exists():
        return Response({"error": "Already a member"}, status=400)

    member_count = Membership.objects.filter(circle=circle).count()

    if member_count >= 4:
        return Response({"error": "Circle is full"}, status=400)

    Membership.objects.create(
        user=request.user,
        circle=circle,
        position=member_count + 1
    )

    return Response({"message": "Joined successfully"})