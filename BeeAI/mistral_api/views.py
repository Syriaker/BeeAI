from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import MistralAPI
from datetime import datetime
import requests
from rest_framework.permissions import IsAuthenticated

API_URL = 'https://api-metrika.yandex.ru/stat/v1/data.csv'

class MetrikaAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        print("=" * 50)
        print(f"!!! ПОЛУЧЕН НОВЫЙ ЗАПРОС ОТ ФРОНТЕНДА !!!")
        print(f"Пользователь: {request.user}")
        print(f"Время получения: {datetime.now().strftime('%H:%M:%S')}")
        print(f"Содержимое запроса (request.data): {request.data}")
        print("=" * 50)
        counter_id = request.data.get('counter_id')
        api_token = request.data.get('api_token')
        charts = request.data.get('charts', [])  # Добавляем получение charts

        print(f"Полученные графики: {charts}")

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
            #print(metrika_data)

            mistral_response = 'test' #MistralService.generate_response(metrika_data)  # генерим ответ
            MistralAPI.objects.create(prompt=metrika_data, response=mistral_response)

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
    permission_classes = [IsAuthenticated]
    def post(self, request):

        prompt = request.data.get('prompt')

        if not prompt:
            return Response({"error": "No prompt"}, status=status.HTTP_400_BAD_REQUEST)

        try:

            response = 'test' #MistralService.generate_response(prompt)

            MistralAPI.objects.create(prompt=prompt, response=response)

            return Response({"response": response}, status=status.HTTP_200_OK)
        except Exception as e:
            # Обработайте любые ошибки
            print(f"Error generating response: {e}")
            return Response({"error": "Failed to generate response"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)