from django.apps import AppConfig
import os
import pickle  # Hoặc joblib
import spacy
from django.conf import settings


############################
# Biến toàn cục để giữ model đã load (hoặc có thể gắn vào AppConfig instance)
NLP_MODEL = None
VECTORIZER = None
INGREDIENT_VECTORS = None


class CoreConfig(AppConfig):  # Tên class thường là <AppName>Config
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"  # Tên app của bạn

    def ready(self):
        # Hàm này chạy một lần khi server khởi động
        global NLP_MODEL, VECTORIZER, INGREDIENT_VECTORS
        if settings.DEBUG:  # Chỉ load khi chạy development server hoặc khi cần
            try:
                print("Loading spaCy NLP model...")
                NLP_MODEL = spacy.load("en_core_web_sm")

                vectorizer_path = os.path.join(
                    settings.BASE_DIR, "core", "ml_models", "vectorizer.pkl"
                )
                ingredients_path = os.path.join(
                    settings.BASE_DIR, "core", "ml_models", "ingredient_vectors.pkl"
                )

                print(f"Loading Vectorizer from {vectorizer_path}...")
                with open(vectorizer_path, "rb") as f_vec:
                    VECTORIZER = pickle.load(f_vec)  # Hoặc joblib.load

                print(f"Loading Ingredient Vectors from {ingredients_path}...")
                with open(ingredients_path, "rb") as f_ingred:
                    INGREDIENT_VECTORS = pickle.load(f_ingred)  # Hoặc joblib.load

                print("ML models loaded successfully for Recipes app!")

            except FileNotFoundError:
                print(
                    "ERROR: Model files not found. Make sure 'vectorizer.pkl' and 'ingredient_vectors.pkl' are in core/ml_models/"
                )
                # Xử lý lỗi, có thể raise exception hoặc để các biến là None
                NLP_MODEL = None
                VECTORIZER = None
                INGREDIENT_VECTORS = None
            except Exception as e:
                print(f"ERROR loading ML models: {e}")
                NLP_MODEL = None
                VECTORIZER = None
                INGREDIENT_VECTORS = None
        else:
            # Có thể bạn muốn cơ chế load khác cho production
            print(
                "ML models loading skipped (DEBUG is False). Adjust apps.py if needed for production."
            )


# Hàm trợ giúp để lấy model đã load từ nơi khác (ví dụ: views.py)
def get_nlp_model():
    return NLP_MODEL


def get_vectorizer():
    return VECTORIZER


def get_ingredient_vectors():
    return INGREDIENT_VECTORS
