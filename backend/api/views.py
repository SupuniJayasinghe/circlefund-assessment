from rest_framework import generics, status
from rest_framework.response import Response
from django.contrib.auth.models import User
from .serializers import RegisterSerializer
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import Circle, Membership, Round, Contribution
from .serializers import CircleSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from datetime import timedelta
from django.utils import timezone
from django.db import transaction
import math

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

        # Add admin as first member
        Membership.objects.create(
            user=request.user,
            circle=circle,
            position=1
        )

        # Create first saving round automatically
        Round.objects.create(
            circle=circle,
            recipient=request.user,
            deadline=timezone.now() + timedelta(days=7)
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

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def contribute(request):

    round_id = request.data.get("round_id")

    try:
        current_round = Round.objects.get(
            id=round_id,
            status="OPEN"
        )

    except Round.DoesNotExist:
        return Response(
            {"error": "Round not found"},
            status=404
        )


    # Recipient does not pay
    if current_round.recipient == request.user:
        return Response(
            {"error": "Recipient does not contribute"},
            status=400
        )


    # Prevent duplicate contribution
    if Contribution.objects.filter(
        round=current_round,
        member=request.user
    ).exists():

        return Response(
            {"error": "Already contributed"},
            status=400
        )


    amount = current_round.contribution_amount

    penalty = 0


    # Check late payment
    if timezone.now() > current_round.deadline:

        penalty = int(
            (
                Decimal(amount * current_round.penalty_rate)
                /
                Decimal(100)

            ).quantize(
                Decimal("1"),
                rounding=ROUND_HALF_UP
            )
        )


    # Save contribution
    Contribution.objects.create(
        round=current_round,
        member=request.user,
        amount=amount,
        penalty=penalty
    )


    # Check whether all members paid
    expected = (
        Membership.objects
        .filter(circle=current_round.circle)
        .count()
        - 1
    )


    if current_round.contributions.count() >= expected:

        current_round.status = "PENDING"
        current_round.save()


    return Response(
        {
            "message": "Contribution recorded",
            "penalty": penalty
        },
        status=201
    )

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def approve_payout(request):

    round_id = request.data.get("round_id")


    with transaction.atomic():

        try:
            current_round = (
                Round.objects
                .select_for_update()
                .get(
                    id=round_id,
                    status="PENDING"
                )
            )

        except Round.DoesNotExist:
            return Response(
                {"error":"Pending round not found"},
                status=404
            )


        # only circle admin
        if current_round.circle.admin != request.user:
            return Response(
                {"error":"Only admin can approve"},
                status=403
            )


        total = 0

        contributions = current_round.contributions.all()


        for contribution in contributions:
            total += (
                contribution.amount +
                contribution.penalty
            )


        payout = math.floor(total * 0.99)


        current_round.payout_amount = payout
        current_round.status = "CLOSED"
        current_round.save()



        # find next recipient
        members = (
            Membership.objects
            .filter(circle=current_round.circle)
            .order_by("position")
        )


        next_member = None


        for member in members:

            if member.user != current_round.recipient:
                next_member = member.user
                break


        if next_member:

            Round.objects.create(
                circle=current_round.circle,
                recipient=next_member,
                deadline=timezone.now()+timedelta(days=7)
            )


        return Response({
            "message":"Payout approved",
            "payout_amount":payout
        })