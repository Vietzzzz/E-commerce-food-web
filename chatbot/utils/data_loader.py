# utils/data_loader.py (ví dụ)
import pandas as pd
import os
from django.conf import settings
import ast

DATASET_PATH = os.path.join(
    settings.BASE_DIR, "data", "recipes.csv"
)  # Điều chỉnh tên file nếu cần

df_recipes = None


def load_recipes_data():
    try:
        DATASET_PATH = os.path.join(
            settings.BASE_DIR, "data", "recipes.csv"
        )  # Điều chỉnh tên file nếu cần
        df = pd.read_csv(DATASET_PATH)
        # Tiền xử lý nếu cần, ví dụ:
        # df.rename(columns={'Tên Cột Món Ăn CSV': 'Title',
        #                    'Tên Cột Nguyên Liệu CSV': 'Cleaned_Ingredients',
        #                    'Tên Cột Hướng Dẫn CSV': 'Instructions'}, # THAY TÊN CỘT HƯỚNG DẪN Ở ĐÂY
        #           inplace=True)

        # Đảm bảo cột Instructions là chuỗi (nếu có thể là số hoặc NaN)
        if "Instructions" in df.columns:  # THAY 'Instructions' BẰNG TÊN CỘT THỰC TẾ
            df["Instructions"] = (
                df["Instructions"].astype(str).fillna("Không có hướng dẫn chi tiết.")
            )
        else:
            print("CẢNH BÁO: Không tìm thấy cột 'Instructions' trong dataset.")
            df["Instructions"] = (
                "Không có hướng dẫn chi tiết."  # Cung cấp giá trị mặc định
            )

        # Tương tự cho cột Cleaned_Ingredients
        if "Cleaned_Ingredients" in df.columns:
            df["Cleaned_Ingredients"] = (
                df["Cleaned_Ingredients"]
                .astype(str)
                .fillna("Không có thông tin nguyên liệu.")
            )
        else:
            print("CẢNH BÁO: Không tìm thấy cột 'Cleaned_Ingredients' trong dataset.")
            df["Cleaned_Ingredients"] = "Không có thông tin nguyên liệu."

        # Nếu bạn có cột Is_Vegetarian (TRUE/FALSE hoặc 1/0)
        # if 'Is_Vegetarian' in df.columns: # THAY 'Is_Vegetarian' BẰNG TÊN CỘT THỰC TẾ
        #     # Chuyển đổi sang kiểu boolean nếu cần (ví dụ nếu nó là 0/1 hoặc chuỗi 'True'/'False')
        #     # df['Is_Vegetarian'] = df['Is_Vegetarian'].replace({1: True, 0: False, '1': True, '0': False, 'TRUE': True, 'FALSE': False})
        #     # df['Is_Vegetarian'] = df['Is_Vegetarian'].astype(bool)
        #     pass # Để đó xử lý ở hàm tìm món chay
        # else:
        #     print("CẢNH BÁO: Không tìm thấy cột 'Is_Vegetarian' hoặc cột tương tự để xác định món chay.")

        return df
    except FileNotFoundError:
        print(f"Lỗi: Không tìm thấy file dataset.")
        return None
    except Exception as e:
        print(f"Lỗi khi tải dataset: {e}")
        return None


def get_dish_details(dish_name):  # Đổi tên hàm để rõ ràng hơn
    if df_recipes is None:
        return {"error": "Xin lỗi, tôi không thể truy cập dữ liệu món ăn vào lúc này."}

    dish_name_lower = dish_name.lower().strip()
    # THAY 'Title' BẰNG TÊN CỘT MÓN ĂN THỰC TẾ CỦA BẠN
    result = df_recipes[df_recipes["Title"].str.strip().str.lower() == dish_name_lower]

    if not result.empty:
        dish_data = result.iloc[0]
        dish_title = dish_data["Title"]  # Lấy tên món ăn chính xác từ dataset

        # THAY 'Cleaned_Ingredients' BẰNG TÊN CỘT NGUYÊN LIỆU THỰC TẾ
        ingredients_str = dish_data.get(
            "Cleaned_Ingredients", "Không có thông tin nguyên liệu."
        )
        # THAY 'Instructions' BẰNG TÊN CỘT HƯỚNG DẪN THỰC TẾ
        instructions_str = dish_data.get("Instructions", "Không có hướng dẫn chi tiết.")

        # Xử lý chuỗi nguyên liệu (tùy thuộc vào định dạng trong CSV)
        try:
            # Nếu nó là một chuỗi dạng list: "['item1', 'item2']"
            cleaned_ingredients_list = ast.literal_eval(ingredients_str)
            if isinstance(cleaned_ingredients_list, list):
                ingredients_text = ", ".join(cleaned_ingredients_list)
            else:  # Nếu không phải list thì dùng chuỗi gốc
                ingredients_text = (
                    ingredients_str.replace("[", "")
                    .replace("]", "")
                    .replace('"', "")
                    .replace("'", "")
                )
        except (ValueError, SyntaxError):
            # Nếu là chuỗi phân cách bằng dấu phẩy hoặc dạng khác không phải list chuẩn
            ingredients_text = (
                ingredients_str.replace("[", "")
                .replace("]", "")
                .replace('"', "")
                .replace("'", "")
            )

        return {
            "title": dish_title,
            "ingredients": ingredients_text,
            "instructions": instructions_str,
        }
    else:
        return {
            "not_found": f"Xin lỗi, tôi không tìm thấy thông tin cho món '{dish_name}'."
        }

    # # def find_vegetarian_dishes(limit=10): # Giới hạn số lượng món trả về
    # if df_recipes is None:
    #     return {"error": "Xin lỗi, tôi không thể truy cập dữ liệu món ăn vào lúc này."}

    # else:
    #     # --- CÁCH 3: Phỏng đoán dựa trên nguyên liệu (KÉM CHÍNH XÁC HƠN) ---
    #     # Đây là một ví dụ rất cơ bản và cần cải thiện nhiều
    #     # print("Thông báo: Không có cột đánh dấu món chay. Thử phỏng đoán dựa trên nguyên liệu (kết quả có thể không chính xác).")
    #     # non_veg_keywords = ['thịt', 'cá', 'gà', 'bò', 'heo', 'tôm', 'cua', 'mực', 'trứng'] # Có thể mở rộng
    #     # vegetarian_dishes = []
    #     # # THAY 'Title' VÀ 'Cleaned_Ingredients' BẰNG TÊN CỘT THỰC TẾ
    #     # for index, row in df_recipes.iterrows():
    #     #     is_vegetarian = True
    #     #     ingredients_lower = str(row['Cleaned_Ingredients']).lower()
    #     #     for keyword in non_veg_keywords:
    #     #         if keyword in ingredients_lower:
    #     #             is_vegetarian = False
    #     #             break
    #     #     if is_vegetarian:
    #     #         vegetarian_dishes.append(row['Title'])
    #     #     if len(vegetarian_dishes) >= limit * 5: # Quét một phần để không quá chậm
    #     #         break
    #     return {
    #         "error": "Không tìm thấy cột thông tin món chay trong dataset. Tính năng này chưa được hỗ trợ đầy đủ."
    #     }

    # if vegetarian_dishes:
    #     return {
    #         "dishes": list(set(vegetarian_dishes))[:limit]
    #     }  # Trả về danh sách không trùng lặp và giới hạn số lượng
    # else:
    #     return {
    #         "not_found": "Xin lỗi, tôi không tìm thấy món chay nào trong dữ liệu hiện tại."
    #     }
