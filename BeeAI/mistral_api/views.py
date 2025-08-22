from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .services import MistralService
from .models import MistralAPI
import requests
from django.shortcuts import render

API_URL = 'https://api-metrika.yandex.ru/stat/v1/data.csv'


def my_view(request):
    return render(request, 'mistral_api/index.html')


class MetrikaAPIView(APIView):
    def post(self, request):
        counter_id = request.data.get('counter_id')
        api_token = request.data.get('api_token')

        if not counter_id or not api_token:
            return Response({"error": "Не указаны ID счетчика или API токен"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            counter_id = int(counter_id)

            params = {
                'date1': '60daysAgo',
                'date2': 'today',
                'id': counter_id,
                'metrics': 'ym:s:visits,ym:s:users',
                'dimensions': 'ym:s:TrafficSource',
                'limit': 100
            }

            r = requests.get(API_URL, params=params, headers={'Authorization': api_token})
            r.raise_for_status()

            metrika_data = r.text

            mistral_response = MistralService.generate_response(metrika_data)  # Передача данных из Метрики
            MistralAPI.objects.create(prompt=metrika_data, response=mistral_response)  # Сохраняем в БД (Мирону настроить для начала)

            return Response({"response": mistral_response}, status=status.HTTP_200_OK)

        except ValueError:
            return Response({"error": "Некорректный ID счетчика. Должно быть целым числом."},
                            status=status.HTTP_400_BAD_REQUEST)
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при запросе к Яндекс.Метрике: {e}")
            return Response({"error": f"Ошибка при запросе к Яндекс.Метрике: {e}"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            print(f"Непредвиденная ошибка: {e}")
            return Response({"error": "Произошла ошибка при обработке запроса."},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MistralAPIView(APIView):
    def post(self, request):

        prompt = request.data.get('prompt')

        if not prompt:
            return Response({"error": "No prompt"}, status=status.HTTP_400_BAD_REQUEST)

        try:

            response = MistralService.generate_response(prompt)

            MistralAPI.objects.create(prompt=prompt, response=response)

            return Response({"response": response}, status=status.HTTP_200_OK)
        except Exception as e:
            # Обработайте любые ошибки
            print(f"Error generating response: {e}")
            return Response({"error": "Failed to generate response"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)