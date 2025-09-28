from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from .serializers import RegistrationSerializer, LoginSerializer
from rest_framework.permissions import AllowAny


class RegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        print("REGISTRATION REQUEST RECEIVED")
        print(f"Data: {request.data}")

        serializer = RegistrationSerializer(data=request.data)

        if serializer.is_valid():
            try:
                user = serializer.save()

                token, created = Token.objects.get_or_create(user=user)

                print(f"USER REGISTERED SUCCESSFULLY: {user.email}")

                return Response({
                    "message": "User registered successfully",
                    "token": token.key,
                    "user_id": user.id,
                    "email": user.email
                }, status=status.HTTP_201_CREATED)

            except Exception as e:
                print(f"ERROR CREATING USER: {str(e)}")
                return Response({"error": f"Registration error: {str(e)}"},
                                status=status.HTTP_400_BAD_REQUEST)

        print(f"VALIDATION ERROR: {serializer.errors}")

        error_messages = []
        for field, errors in serializer.errors.items():
            for error in errors:
                error_messages.append(f"{field}: {error}")

        error_string = "; ".join(error_messages)
        return Response({"error": error_string}, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        print("LOGIN REQUEST RECEIVED")
        print(f"Email: {request.data.get('email')}")

        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response({"error": "Email and password are required"},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "User with this email not found"},
                            status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(username=user.username, password=password)

        if user is not None:
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                "message": "Login successful",
                "token": token.key,
                "user_id": user.id,
                "email": user.email
            })
        else:
            return Response({"error": "Invalid password"},
                            status=status.HTTP_400_BAD_REQUEST)