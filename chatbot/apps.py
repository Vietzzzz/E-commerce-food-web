# chatbot/apps.py
from django.apps import AppConfig
from .utils import data_loader  # Đảm bảo đường dẫn đúng


class ChatbotConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "chatbot"

    def ready(self):
        print("Đang tải dữ liệu món ăn...")
        data_loader.df_recipes = data_loader.load_recipes_data()
        if data_loader.df_recipes is not None:
            print(f"Đã tải thành công {len(data_loader.df_recipes)} món ăn.")
        else:
            print("Không tải được dữ liệu món ăn.")
