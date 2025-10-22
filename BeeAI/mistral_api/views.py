from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from .models import MistralAPI
from datetime import datetime
import requests
from rest_framework.permissions import IsAuthenticated, AllowAny
from .serializers import AnalysisHistorySerializer, AnalysisDetailSerializer
import pandas as pd
import io

class MetrikaAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        print("=" * 50)
        print(f"!!! ПОЛУЧЕН НОВЫЙ ЗАПРОС ОТ ФРОНТЕНДА !!!")
        print(f"Время получения: {datetime.now().strftime('%H:%M:%S')}")
        print(f"Содержимое запроса (request.data): {request.data}")
        print("=" * 50)
        counter_id = int(request.data.get('counter_id'))
        api_token = request.data.get('api_token')
        charts = request.data.get('charts', [])

        if not counter_id or not api_token:
            return Response({"error": "Не указаны ID счетчика или API токен"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            if 7 in charts:
                API_URL = 'https://api-metrika.yandex.ru/stat/v1/data.csv'
                params = {
                    'date1': '60daysAgo',
                    'date2': 'today',
                    'id': counter_id,
                    'metrics': 'ym:s:visits,ym:s:users',
                    'dimensions': 'ym:s:deviceCategory',
                    'limit': 100
                }

                r = requests.get(API_URL, params=params, headers={'Authorization': api_token})
                r.raise_for_status()

                metrika_data = r.text
                charts_data_response = []

                csv_file = io.StringIO(metrika_data)

                df = pd.read_csv(csv_file, header=0)
                df = df.dropna(how='all')
                df = df.reset_index(drop=True)

                mobile = df.iloc[1, 1]
                pc = df.iloc[2, 1]

                charts_data_response.append({
                    "chart_id": 7,
                    "chart_type": "Круговая диаграмма",
                    "data": [
                        {"category": "ПК", "value": str(pc)},
                        {"category": "Мобильные", "value": str(mobile)},
                    ]
                })

            if 1 in charts:
                API_URL = 'https://api-metrika.yandex.ru/stat/v1/data/bytime.csv'
                params = {
                    'date1': '6daysAgo',
                    'date2': 'today',
                    'id': counter_id,
                    'metrics': 'ym:s:visits',
                    'group': 'day',
                }

                r = requests.get(API_URL, params=params, headers={'Authorization': api_token})
                r.raise_for_status()

                metrika_data = r.text
                print(metrika_data)
                charts_data_response = []

                csv_file = io.StringIO(metrika_data)

                df = pd.read_csv(csv_file, header=0)
                df = df.dropna(how='all')
                df = df.reset_index(drop=True)
                df['(Визиты)'] = pd.to_numeric(df['(Визиты)'])


                charts_data_response.append({
                    "chart_id": 1,
                    "chart_type": "Столбчатая диаграмма",
                    "data": df.rename(columns={'Период': 'time', '(Визиты)': 'value'}).to_dict('records')
                })


            mistral_response = 'test' #MistralService.generate_response(metrika_data)  # генерим ответ

            MistralAPI.objects.create(
                user=request.user,
                counter_id=counter_id,
                prompt=metrika_data,
                response=mistral_response,
                charts_data = charts_data_response
            )

            return Response({"response": mistral_response,"charts_data": charts_data_response}, status=status.HTTP_200_OK)

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
            print(f"Error generating response: {e}")
            return Response({"error": "Failed to generate response"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AnalysisHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_analyses = MistralAPI.objects.filter(user=request.user).order_by('-created_at')
        serializer = AnalysisHistorySerializer(user_analyses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class AnalysisDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AnalysisDetailSerializer
    queryset = MistralAPI.objects.all()

    def get_queryset(self):

        return self.queryset.filter(user=self.request.user)