import pandas as pd
import spacy
import re
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from django.conf import settings
import os

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# Đường dẫn đến dataset và file đã train
DATASET_PATH = os.path.join(settings.BASE_DIR, 'data', 'Food Ingredients and Recipe Dataset with Image Name Mapping.csv')
VECTORIZER_PATH = os.path.join(settings.BASE_DIR, 'data', 'title_vectorizer.pkl')
VECTORS_PATH = os.path.join(settings.BASE_DIR, 'data', 'title_vectors.pkl')

# Danh sách các từ cần loại bỏ
stopwords = set([
    "cup", "cups", "tbsp", "tsp", "oz", "pound", "lb", "medium", "large", "small",
    "fresh", "kosher", "extra-virgin", "toasted", "mild", "seasoned", "virgin",
    "x", "half", "coarsely", "chopped", "diced", "peeled", "sliced", "grated",
    "preferably", "crosswise", "drained", "thinly", "freshly", "gallon", "ounce",
    "and", "from", "pieces", "ground", "bone", "water", "carcass", "handful",
    "1", "2", "3", "4", "5", "6", "7", "8", "9", "½", "⅓", "¼", "⅔", "¾"
])

# Đọc dataset và load vectorizer/vectors đã train
def load_dataset_and_vectorizer():
    # Đọc dataset
    df = pd.read_csv(DATASET_PATH)
    ingredient_col = 'Cleaned_Ingredients' if 'Cleaned_Ingredients' in df.columns else 'Ingredients'
    df[ingredient_col] = df[ingredient_col].fillna("")
    df['Title'] = df['Title'].fillna("")

    # Load vectorizer và vectors đã train
    try:
        with open(VECTORIZER_PATH, "rb") as f:
            vectorizer = pickle.load(f)
        with open(VECTORS_PATH, "rb") as f:
            vectors = pickle.load(f)
    except (FileNotFoundError, EOFError):
        # Nếu không tìm thấy file, khởi tạo lại (dự phòng)
        vectorizer = TfidfVectorizer(stop_words='english')
        vectors = vectorizer.fit_transform(df['Title'])
        with open(VECTORIZER_PATH, "wb") as f:
            pickle.dump(vectorizer, f)
        with open(VECTORS_PATH, "wb") as f:
            pickle.dump(vectors, f)

    return df, vectorizer, vectors, ingredient_col

# Hàm tiền xử lý để loại bỏ số và ký tự đặc biệt
def preprocess_ingredient_text(ingredient_text):
    ingredient_text = re.sub(r'\[.*?\]', '', ingredient_text)
    ingredient_text = re.sub(r'\(.*?\)', '', ingredient_text)
    ingredient_text = re.sub(r'^\d+\s*', '', ingredient_text)
    ingredient_text = re.sub(r'[^a-zA-Z\s]', '', ingredient_text)
    return ingredient_text.strip()

# Hàm lọc danh từ chính từ cụm nguyên liệu
def extract_ingredient_nouns(ingredient_text):
    ingredient_text = preprocess_ingredient_text(ingredient_text)
    if not ingredient_text:
        return ""
    
    doc = nlp(ingredient_text)
    nouns = []
    current_noun = []
    
    for token in doc:
        if token.text.lower() in stopwords:
            continue
        if token.pos_ in ["NOUN", "PROPN"]:
            current_noun.append(token.text.lower())
        elif token.pos_ in ["NUM", "ADJ", "ADV", "DET"] or token.text in [",", "."]:
            continue
        else:
            if current_noun:
                noun_phrase = " ".join(current_noun)
                if "salt" in noun_phrase:
                    noun_phrase = "salt"
                elif "oil" in noun_phrase:
                    noun_phrase = "oil"
                nouns.append(noun_phrase)
                current_noun = []
    
    if current_noun:
        noun_phrase = " ".join(current_noun)
        if "salt" in noun_phrase:
            noun_phrase = "salt"
        elif "oil" in noun_phrase:
            noun_phrase = "oil"
        nouns.append(noun_phrase)
    
    return nouns[0] if nouns else ""

# Hàm làm sạch danh sách nguyên liệu
def clean_ingredients(ingredient_text):
    ingredients = ingredient_text.split(", ")
    cleaned_ingredients = []
    
    for ing in ingredients:
        if ing:
            cleaned_name = extract_ingredient_nouns(ing)
            if cleaned_name and cleaned_name not in stopwords:
                cleaned_ingredients.append(cleaned_name)
    
    specific_vegetables = {"cabbage", "carrots", "zucchini", "cucumbers", "scallions", "lettuce", "broccolini"}
    cleaned_ingredients = sorted(set(cleaned_ingredients))
    if "vegetables" in cleaned_ingredients and any(veg in cleaned_ingredients for veg in specific_vegetables):
        cleaned_ingredients.remove("vegetables")
    
    return cleaned_ingredients

# Hàm tìm kiếm món ăn và trả về nguyên liệu
def search_dish(dish_name):
    df, vectorizer, vectors, ingredient_col = load_dataset_and_vectorizer()
    
    # Chuyển tên món nhập vào thành vector TF-IDF
    input_vector = vectorizer.transform([dish_name.lower()])
    similarities = cosine_similarity(input_vector, vectors).flatten()
    top_indices = similarities.argsort()[-1:][::-1]  # Lấy món khớp nhất
    
    matched_dish = df.iloc[top_indices[0]]
    similarity = similarities[top_indices[0]]
    
    if similarity > 0.1:
        cleaned_ingredients = clean_ingredients(matched_dish[ingredient_col])
        return {
            'dish_name': matched_dish['Title'],
            'ingredients': cleaned_ingredients,
            'similarity': similarity
        }
    else:
        return None