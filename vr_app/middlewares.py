# import logging

# logger = logging.getLogger('django.request')

# class RequestLoggingMiddleware:
#     def __init__(self, get_response):
#         self.get_response = get_response

#     def __call__(self, request):
#         logger.debug(f"📢 요청 감지: {request.method} {request.path} FROM {request.META.get('REMOTE_ADDR')}")
#         response = self.get_response(request)
#         return response
