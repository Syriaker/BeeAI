from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from .models import MistralAPI
from .services import MistralService
from datetime import datetime
import requests
from rest_framework.permissions import IsAuthenticated, AllowAny
from .serializers import AnalysisHistorySerializer, AnalysisDetailSerializer
import pandas as pd
import numpy as np
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
            charts_data_response = []
            mistral_response = []
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

                mistral_response.append(MistralService.generate_response(metrika_data))

            if 2 in charts:
                API_URL = 'https://api-metrika.yandex.ru/stat/v1/data/bytime.csv'
                params = {
                    'date1': '6daysAgo',
                    'date2': 'today',
                    'id': counter_id,
                    'metrics': 'ym:s:pageviews',
                    'group': 'day',
                }

                r = requests.get(API_URL, params=params, headers={'Authorization': api_token})
                r.raise_for_status()

                metrika_data = r.text

                csv_file = io.StringIO(metrika_data)

                df = pd.read_csv(csv_file, header=0)
                df = df.dropna(how='all')
                df = df.reset_index(drop=True)
                df['(Просмотры)'] = pd.to_numeric(df['(Просмотры)'])


                charts_data_response.append({
                    "chart_id": 2,
                    "chart_type": "Столбчатая диаграмма",
                    "data": df.rename(columns={'Период': 'time', '(Просмотры)': 'value'}).to_dict('records')
                })

                mistral_response.append(MistralService.generate_response(metrika_data))

            if 4 in charts:
                API_URL = 'https://api-metrika.yandex.ru/stat/v1/data/bytime.csv'
                params = {
                    'date1': '6daysAgo',
                    'date2': 'today',
                    'id': counter_id,
                    'metrics': 'ym:s:avgVisitDurationSeconds',
                    'group': 'day',
                }

                r = requests.get(API_URL, params=params, headers={'Authorization': api_token})
                r.raise_for_status()

                metrika_data = r.text

                csv_file = io.StringIO(metrika_data)

                df = pd.read_csv(csv_file, header=0)
                df = df.dropna(how='all')
                df = df.reset_index(drop=True)
                df['value'] = pd.to_timedelta(df['(Время на сайте)']).dt.total_seconds().astype(int)

                charts_data_response.append({
                    "chart_id": 4,
                    "chart_type": "Гладкий график",
                    "data": df[['Период', 'value']]
                    .rename(columns={'Период': 'date'})
                    .to_dict('records')
                })

                mistral_response.append(MistralService.generate_response(metrika_data))

            if 6 in charts:
                API_URL = 'https://api-metrika.yandex.ru/stat/v1/data/bytime.csv'
                params = {
                    'date1': '6daysAgo',
                    'date2': 'today',
                    'id': counter_id,
                    'metrics': 'ym:s:visits',
                    'dimensions': 'ym:s:bounce',
                    'group': 'day',
                }

                r = requests.get(API_URL, params=params, headers={'Authorization': api_token})
                r.raise_for_status()

                metrika_data = r.text

                csv_file = io.StringIO(metrika_data)

                df = pd.read_csv(csv_file, header=0)
                df = df.dropna(how='all')
                df = df.reset_index(drop=True)
                df['Отказ (Визиты)'] = pd.to_numeric(df['Отказ (Визиты)'])
                df['Не отказ (Визиты)'] = pd.to_numeric(df['Не отказ (Визиты)'])
                df['total_visits'] = df['Отказ (Визиты)'] + df['Не отказ (Визиты)']
                df['value'] = (df['Отказ (Визиты)'] / df['total_visits']).fillna(0)


                charts_data_response.append({
                    "chart_id": 6,
                    "chart_type": "Линейный график",
                    "data": df[['Период', 'value']]
                    .rename(columns={'Период': 'date'})
                    .to_dict('records')
                })

                mistral_response.append(MistralService.generate_response(metrika_data))

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

                mistral_response.append('test')    #mistral_response.append(MistralService.generate_response(metrika_data))

            if 8 in charts:
                API_URL = 'https://api-metrika.yandex.ru/stat/v1/data.csv'
                params = {
                    'date1': '6daysAgo',
                    'date2': 'today',
                    'id': counter_id,
                    'metrics': 'ym:s:users',
                    'dimensions': 'ym:s:ageInterval',
                    'limit': 100
                }

                r = requests.get(API_URL, params=params, headers={'Authorization': api_token})
                r.raise_for_status()

                metrika_data = r.text

                csv_file = io.StringIO(metrika_data)

                df = pd.read_csv(csv_file, header=0)
                df = df.dropna(how='all')
                df = df.reset_index(drop=True)

                DESIRED_RANGES = ["18-24", "25-34", "35-44", "45-54", "55+"]
                template_df = pd.DataFrame({
                    'age_range': DESIRED_RANGES,
                    'value': 0
                }).set_index('age_range')
                df = df[df['Возраст'] != 'Итого и средние'].copy()
                df['age_range'] = df['Возраст'].str.replace(' года', '').str.replace(' лет', '') \
                    .str.replace('‑', '-').str.replace('старше ', '') \
                    .str.replace('младше ', '0-')
                df = df.rename(columns={'Посетители': 'value'})
                df['value'] = pd.to_numeric(df['value'])
                df_processed = df.set_index('age_range')
                template_df.update(df_processed)


                charts_data_response.append({
                    "chart_id": 8,
                    "chart_type": "Гистограмма",
                    "data": template_df.reset_index().to_dict('records')
                })

                mistral_response.append(MistralService.generate_response(metrika_data))

            if 9 in charts:
                API_URL = 'https://api-metrika.yandex.ru/stat/v1/data.csv'
                params = {
                    'date1': '6daysAgo',
                    'date2': 'today',
                    'id': counter_id,
                    'metrics': 'ym:s:visits',
                    'dimensions': 'ym:s:operatingSystem',
                    'limit': 100
                }

                r = requests.get(API_URL, params=params, headers={'Authorization': api_token})
                r.raise_for_status()

                metrika_data = r.text

                csv_file = io.StringIO(metrika_data)

                df = pd.read_csv(csv_file, header=0)
                df = df.dropna(how='all')
                df = df.reset_index(drop=True)

                df = df[df['Операционная система (детально)'] != 'Итого и средние'].copy()
                df['Визиты'] = pd.to_numeric(df['Визиты'])

                conditions = [
                    df['Операционная система (детально)'].str.contains('Windows', case=False),
                    df['Операционная система (детально)'].str.contains('Android', case=False),
                    df['Операционная система (детально)'].str.contains('iOS', case=False),
                    df['Операционная система (детально)'].str.contains('mac', case=False),
                    df['Операционная система (детально)'].str.contains('Linux', case=False)
                ]

                choices = ['Windows', 'Android', 'iOS', 'macOS', 'Linux']

                df['os_group'] = np.select(conditions, choices, default='Другое')

                grouped_df = df.groupby('os_group')['Визиты'].sum().reset_index()

                charts_data_response.append({
                    "chart_id": 9,
                    "chart_type": "Кольцевая диаграмма",
                    "data": grouped_df.rename(columns={'os_group': 'os', 'Визиты': 'value'})  # Переименовываем столбцы
                    .to_dict('records')
                })

                mistral_response.append(MistralService.generate_response(metrika_data))

            for i in charts_data_response:
                print(i)
            final_response = ''
            for i in mistral_response:
                final_response = final_response + i + '\n'

            MistralAPI.objects.create(
                user=request.user,
                counter_id=counter_id,
                prompt=metrika_data,
                response=final_response,
                charts_data = charts_data_response
            )

            return Response({"response": final_response,"charts_data": charts_data_response}, status=status.HTTP_200_OK)

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

            response = MistralService.generate_response(prompt)

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