from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .services import MistralService
from .models import MistralAPI

class MistralAPIView(APIView):
    def post(self, request):

        prompt = request.data.get('prompt')

        if not prompt:
            return Response({"error": "No prompt"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            response = MistralService.generate_response(prompt)
            MistralAPI.objects.create(prompt=prompt, response=response)  # Сохраняем в БД
            return Response({"response": response}, status=status.HTTP_200_OK)
        except Exception as e:
            # Логирование ошибки (важно!)
            print(f"Ошибка при обработке запроса к Mistral: {e}")
            return Response({"error": "Произошла ошибка при обработке запроса."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)