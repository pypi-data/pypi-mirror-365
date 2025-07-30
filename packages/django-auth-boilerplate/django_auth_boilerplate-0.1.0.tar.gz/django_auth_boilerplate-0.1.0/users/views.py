from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes,throttle_classes
from rest_framework.permissions import AllowAny,IsAuthenticated
from .throttles import LoginThrottle, RegisterThrottle, LogoutThrottle
from .serializers import RegistrationSerializer,LoginSerializer,LogoutSerializer
from rest_framework_simplejwt.tokens import RefreshToken,TokenError

from rest_framework_simplejwt.serializers import TokenRefreshSerializer

import logging

logger = logging.getLogger(__name__)




from rest_framework.exceptions import ValidationError

@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([RegisterThrottle])
def register(request):
    request.throttle_scope = 'register'
    serializer = RegistrationSerializer(data=request.data)
    try:
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        logger.info(f"New user registered: {user.email}")
        return Response({
            "user": serializer.data,
            "message": "User created successfully."
        }, status=status.HTTP_201_CREATED)

    except ValidationError as ve:
        logger.warning(f"Validation error during registration: {ve}")
        return Response({
            'status': 'error',
            'message': 'Validation failed',
            'errors': ve.detail  
        }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        logger.exception("Error during user registration")
        return Response({
            'status': 'error',
            'message': "Something went wrong on our end."
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)





@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([LoginThrottle])
def login_view(request):
    request.throttle_scope = 'login'
    try:
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            logger.info(f"[LOGIN] User logged in: {user.email}")
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user':{
                    'id':str(user.id),
                    'email': user.email,
                    'full_name': user.full_name
                }
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.exception("[LOGIN ERROR] Exception during user login")
        return Response({
            'message': 'something went wrong on our end'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    








@api_view(['POST'])
@permission_classes([AllowAny])
def custom_token_refresh_view(request):
    try:
        serializer = TokenRefreshSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            access = serializer.validated_data['access']

            return Response({
                "access": access
            }, status=status.HTTP_200_OK)

    except TokenError as e:
        logger.warning(f"[REFRESH ERROR] Token error: {str(e)}")
        return Response({
            "message": "Invalid refresh token."
        }, status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        logger.exception("[REFRESH ERROR] Unexpected error during token refresh")
        return Response({
            "message": "Something went wrong on our end."
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)






@api_view(['POST'])
@permission_classes([IsAuthenticated])
@throttle_classes([LogoutThrottle])
def logout_view(request):
    request.throttle_scope = 'logout'
    try:
        serializer = LogoutSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            logger.info(f"[LOGOUT] User logged out: {request.user.email}")
            return Response({
                'message': f'Successfully logged out {request.user.email}'
            }, status=status.HTTP_200_OK)
    except Exception as e:
        logger.exception("[LOGOUT ERROR] Exception during user logout")
        return Response({
            'message': 'Something went wrong on our end.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
