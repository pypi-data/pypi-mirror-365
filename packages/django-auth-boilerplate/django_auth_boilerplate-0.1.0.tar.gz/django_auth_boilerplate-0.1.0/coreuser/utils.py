# core/utils.py or core/exception_handlers.py

from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import Throttled
import logging

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Custom global exception handler for DRF.
    Logs errors and returns a consistent response format.
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)

    view = context.get('view', None)
    request = context.get('request', None)
    view_name = view.__class__.__name__ if view else 'UnknownView'

    if isinstance(exc, Throttled):
        # Determine user info (if available)
        user_info = 'Anonymous'
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            user_info = request.user.email

        logger.warning(
            f"[THROTTLE] {user_info} exceeded rate limit on {view_name}. "
            f"Retry after {exc.wait} seconds."
        )

        return Response({
            'status': 'error',
            'message': 'Rate limit exceeded. Please try again later.',
            'retry_after_seconds': exc.wait
        }, status=status.HTTP_429_TOO_MANY_REQUESTS)

    # Log all other handled exceptions
    if response is not None:
        logger.error(f"Exception in {view_name}: {str(exc)}")

        custom_response = {
            'status': 'error',
            'message': 'Request failed',
            'errors': response.data
        }
        return Response(custom_response, status=response.status_code)

    # For unhandled exceptions (500)
    logger.exception(f"[UNHANDLED EXCEPTION] {str(exc)}")
    return Response({
        'status': 'error',
        'message': 'Internal server error',
        'errors': str(exc)
    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
