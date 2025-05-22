# utils/data_loader.py
import os
import pandas as pd
import re
from django.conf import settings
from .gemini_client import load_dish_names
from fuzzywuzzy import process

DATASET_PATH = os.path.join(settings.BASE_DIR, "data", "recipes.csv")
df_recipes = None


def load_recipes_data():
    """Tải dữ liệu từ file CSV"""
    global df_recipes
    try:
        # Try different encodings if needed
        try:
            df_recipes = pd.read_csv(DATASET_PATH)
        except UnicodeDecodeError:
            df_recipes = pd.read_csv(DATASET_PATH, encoding="latin1")
            print("Sử dụng encoding latin1 cho CSV")

        print(f"Đã tải dữ liệu từ {DATASET_PATH}: {len(df_recipes)} món ăn")
        print(f"Columns in CSV: {', '.join(df_recipes.columns)}")

        # Map column names to standardized names (case insensitive)
        column_mapping = {
            "title": [
                "title",
                "Title",
                "TÊN MÓN",
                "name",
                "dish_name",
                "ten",
            ],
            "ingredients": [
                "ingredients",
                "Ingredients",
                "NGUYÊN LIỆU",
                "Cleaned_Ingredients",
            ],
            "instructions": [
                "instructions",
                "Instructions",
                "CÁCH LÀM",
                "steps",
            ],
        }

        # Find the appropriate columns in the dataset
        actual_columns = {}
        for std_col, possible_names in column_mapping.items():
            for col_name in possible_names:
                if col_name in df_recipes.columns:
                    actual_columns[std_col] = col_name
                    print(f"Đã tìm thấy cột {std_col}: {col_name}")
                    break

            if std_col not in actual_columns:
                print(f"Cảnh báo: Không tìm thấy cột {std_col} trong CSV")

        # Check if we found the title column
        if "title" not in actual_columns:
            print("Lỗi: Không tìm được cột tên món ăn. Không thể tiếp tục.")
            return None

        # Rename columns for easier access
        df_recipes = df_recipes.rename(
            columns={
                actual_columns.get("title"): "title",
                actual_columns.get("ingredients", "ingredients"): "ingredients",
                actual_columns.get("instructions", "instructions"): "instructions",
            }
        )

        # Drop any empty rows in the title column
        df_recipes = df_recipes.dropna(subset=["title"])
        df_recipes = df_recipes[df_recipes["title"].astype(str).str.strip() != ""]

        # Ensure all columns are strings
        for col in ["title", "ingredients", "instructions"]:
            if col in df_recipes.columns:
                df_recipes[col] = df_recipes[col].astype(str)

        # Create a list of dish names
        all_dish_names = df_recipes["title"].tolist()

        # Show some sample data
        print(f"Sample dish names: {all_dish_names[:5]}")
        print(f"Total dishes after cleaning: {len(all_dish_names)}")

        # Load dish names into memory
        load_dish_names(all_dish_names)
        return df_recipes

    except FileNotFoundError:
        print(f"Không tìm thấy file dữ liệu tại {DATASET_PATH}")
        return None
    except Exception as e:
        print(f"Lỗi khi tải dữ liệu: {str(e)}")
        import traceback

        print(traceback.format_exc())
        return None


def get_dish_details(dish_name):
    """Lấy thông tin chi tiết về món ăn từ tên món"""
    global df_recipes

    if df_recipes is None:
        df_recipes = load_recipes_data()
        if df_recipes is None:
            return {"error": "Không thể tải dữ liệu món ăn"}

    try:
        # Clean input dish name
        dish_name_lower = dish_name.lower().strip()

        # Direct matching (không phân biệt hoa thường)
        matching_dishes = df_recipes[df_recipes["title"].str.lower() == dish_name_lower]

        # If direct match failed, try fuzzy matching
        if matching_dishes.empty:
            print(
                f"Không tìm thấy món '{dish_name_lower}' bằng so khớp chính xác, thử fuzzy matching"
            )
            return find_dish_fuzzy(dish_name)

        # Lấy thông tin của món đầu tiên tìm thấy
        dish = matching_dishes.iloc[0]

        result = {"title": dish["title"]}

        if "ingredients" in df_recipes.columns:
            result["ingredients"] = dish["ingredients"]

        if "instructions" in df_recipes.columns:
            result["instructions"] = dish["instructions"]

        return result

    except Exception as e:
        import traceback

        print(f"Lỗi khi tìm thông tin món ăn: {str(e)}")
        print(traceback.format_exc())
        return {"error": f"Lỗi khi tìm thông tin món ăn: {str(e)}"}


def find_dish_fuzzy(dish_name, threshold=70):
    """
    Tìm món ăn bằng fuzzy matching
    """
    global df_recipes

    try:
        # Clean input dish name
        dish_name_clean = dish_name.lower().strip()

        # Get all dish names
        all_dishes = df_recipes["title"].tolist()

        # Find the best match
        match_result = process.extractOne(
            dish_name_clean, [d.lower() for d in all_dishes]
        )
        if not match_result:
            return {"not_found": True}

        match, score = match_result

        print(f"Fuzzy match: '{dish_name}' -> '{match}' (score: {score})")

        if score >= threshold:
            # Find the index of the match in our list
            match_index = [d.lower() for d in all_dishes].index(match)
            # Get the original dish name with proper casing
            original_match = all_dishes[match_index]

            # Find this dish in the dataframe
            dish = df_recipes.iloc[match_index]

            result = {"title": original_match}

            if "ingredients" in df_recipes.columns:
                result["ingredients"] = dish["ingredients"]

            if "instructions" in df_recipes.columns:
                result["instructions"] = dish["instructions"]

            return result
        else:
            return {"not_found": True}
    except Exception as e:
        import traceback

        print(f"Lỗi trong fuzzy matching: {str(e)}")
        print(traceback.format_exc())
        return {"error": f"Lỗi trong fuzzy matching: {str(e)}"}


# Add a function to preview actual data
def preview_data():
    global df_recipes

    if df_recipes is None:
        df_recipes = load_recipes_data()
        if df_recipes is None:
            print("Không thể tải dữ liệu để xem trước")
            return

    print("\n=== PREVIEW OF RECIPE DATA ===")
    # Display first few rows with specific columns
    cols_to_show = ["title"]
    cols_to_show.extend(
        [c for c in ["ingredients", "instructions"] if c in df_recipes.columns]
    )

    sample_data = df_recipes[cols_to_show].head()
    for idx, row in sample_data.iterrows():
        print(f"\nMón #{idx + 1}: {row['title']}")
        if "ingredients" in cols_to_show:
            print(
                f"Nguyên liệu: {row['ingredients'][:100]}..."
                if len(row["ingredients"]) > 100
                else row["ingredients"]
            )
        if "instructions" in cols_to_show:
            print(
                f"Hướng dẫn: {row['instructions'][:100]}..."
                if len(row["instructions"]) > 100
                else row["instructions"]
            )


# Tải dữ liệu khi module được import
print("Đang tải dữ liệu món ăn...")
load_recipes_data()
print("\nXem trước dữ liệu món ăn:")
preview_data()
