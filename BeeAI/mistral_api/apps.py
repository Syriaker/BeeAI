from django.apps import AppConfig


class MistralApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mistral_api'

    def ready(self):
        """
        Этот метод вызывается Django, когда приложение полностью готово.
        Идеальное место для инициализации.
        """
        print("Сигнал 'ready' для приложения 'core' получен.")

        # Импортируем наш сервис. Важно делать импорт внутри метода,
        # чтобы избежать проблем с преждевременной загрузкой моделей.
        from .services import MistralService

        # Запускаем загрузку модели
        MistralService.load_model()