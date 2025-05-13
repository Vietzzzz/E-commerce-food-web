# utils/gemini_client.py (ví dụ)
import google.generativeai as genai
from django.conf import settings
import re

genai.configure(api_key=settings.GOOGLE_API_KEY)

# Khởi tạo model
# Chọn model phù hợp, ví dụ: 'gemini-pro' cho các tác vụ ngôn ngữ chung
model = genai.GenerativeModel("gemini-1.5-flash-latest")  # Hoặc 'gemini-pro'


def get_gemini_suggestion(prompt_text):
    if not settings.GOOGLE_API_KEY:
        return "Lỗi: API Key của Google chưa được cấu hình."
    try:
        response = model.generate_content(prompt_text)
        return response.text
    except Exception as e:
        print(f"Lỗi khi gọi Gemini API: {e}")
        return f"Xin lỗi, đã có lỗi xảy ra khi kết nối với AI: {e}"


def get_enhanced_dish_suggestion(
    user_input, dish_name_from_dataset, ingredients_list_str
):
    """
    Sử dụng Gemini để tạo câu trả lời tự nhiên hơn hoặc xử lý các trường hợp phức tạp.
    """
    if not ingredients_list_str or "không tìm thấy" in ingredients_list_str.lower():
        # Nếu dataset không có, hỏi Gemini xem nó có biết không (nhưng nên cẩn thận vì có thể không chính xác bằng dataset của bạn)
        prompt = f"""Người dùng muốn biết nguyên liệu cho món ăn: '{user_input}'.
        Trong bộ dữ liệu của tôi không có món này.
        Dựa trên kiến thức của bạn, bạn có thể gợi ý một vài nguyên liệu phổ biến cho món '{user_input}' được không?
        Nếu không biết, hãy nói rằng bạn không có thông tin."""
    else:
        # Dataset có thông tin, dùng Gemini để làm câu trả lời tự nhiên hơn
        prompt = f"""Người dùng muốn biết nguyên liệu cho món ăn: '{user_input}'.
        Dựa trên dữ liệu được cung cấp, nguyên liệu cho món '{dish_name_from_dataset}' là: {ingredients_list_str}.
        Hãy tạo một câu trả lời thân thiện và tự nhiên để gợi ý các nguyên liệu này cho người dùng.
        Ví dụ: 'Để nấu món {dish_name_from_dataset} thơm ngon, bạn sẽ cần chuẩn bị: [danh sách nguyên liệu]. Chúc bạn vào bếp thành công!'
        """
    return get_gemini_suggestion(prompt)


def extract_dish_name_from_query(user_query, dish_titles_from_dataset=None):
    """
    Trích xuất tên món ăn từ câu truy vấn của người dùng.
    dish_titles_from_dataset là một list các tên món ăn có trong dataset của bạn (tùy chọn).
    """
    if not model:
        return user_query  # Trả về query gốc nếu model lỗi

    # Cung cấp thêm ngữ cảnh cho Gemini nếu có danh sách món ăn
    context_prompt = ""
    if dish_titles_from_dataset:
        # Chỉ lấy một phần nhỏ để không làm prompt quá dài, hoặc không cần nếu quá nhiều
        # sample_dishes = ", ".join(dish_titles_from_dataset[:20]) # Ví dụ lấy 20 món đầu
        # context_prompt = f"Một số món ăn có thể có trong cơ sở dữ liệu: {sample_dishes}."
        pass  # Hiện tại có thể bỏ qua việc truyền toàn bộ danh sách nếu quá lớn

    prompt = f"""
    Người dùng đã nhập câu sau: "{user_query}".
    {context_prompt}
    Hãy trích xuất tên món ăn chính mà người dùng có khả năng đang đề cập đến từ câu trên.
    Chỉ trả về tên món ăn đó, không thêm bất kỳ giải thích nào.
    Ví dụ:
    - Nếu người dùng nhập "tôi muốn ăn phở bò", chỉ trả về "phở bò".
    - Nếu người dùng nhập "cách làm món cá kho tộ", chỉ trả về "cá kho tộ".
    - Nếu người dùng nhập "bún chả", chỉ trả về "bún chả".
    - Nếu người dùng nhập "cho xin công thức món cơm sườn nướng", chỉ trả về "cơm sườn nướng".
    - Nếu không chắc chắn hoặc không thể trích xuất được tên món ăn rõ ràng, hãy trả về lại CHUỖI RỖNG.
    Tên món ăn cần trích xuất là:
    """
    try:
        response = model.generate_content(prompt)
        extracted_name = response.text.strip()

        # Xóa các dấu câu không cần thiết có thể Gemini trả về
        extracted_name = re.sub(
            r"[^\w\s]", "", extracted_name
        )  # Giữ lại chữ, số, khoảng trắng

        if (
            not extracted_name or len(extracted_name) < 2
        ):  # Nếu trả về rỗng hoặc quá ngắn, coi như không trích xuất được
            print(
                f"Gemini không trích xuất được tên món ăn rõ ràng từ '{user_query}', trả về rỗng."
            )
            return ""  # Trả về chuỗi rỗng nếu không trích xuất được
        print(f"Gemini trích xuất từ '{user_query}' -> '{extracted_name}'")
        return extracted_name
    except Exception as e:
        print(f"Lỗi khi trích xuất tên món ăn bằng Gemini: {e}")
        return user_query  # Trả về query gốc nếu có lỗi API
