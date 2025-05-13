# chatbot/views.py
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

# --- Đảm bảo import đầy đủ các hàm cần thiết ---
from .utils.data_loader import (
    get_dish_details,
    # find_vegetarian_dishes, # BỎ dòng này
)
from .utils.gemini_client import (
    get_gemini_suggestion,
    get_enhanced_dish_suggestion,
    extract_dish_name_from_query,
)


def chatbot_view(request):
    return render(request, "chatbot/chat_interface.html")


@csrf_exempt
def get_chatbot_response(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_message_original = data.get("message", "").strip()
            # user_message_lower = user_message_original.lower() # Không cần thiết nữa nếu không có nhận diện keyword chay
        except json.JSONDecodeError:
            return JsonResponse(
                {"reply": "Lỗi: Dữ liệu gửi lên không hợp lệ."}, status=400
            )

        if not user_message_original:
            return JsonResponse({"reply": "Bạn muốn hỏi về món ăn nào nhỉ?"})

        bot_reply = ""

        dish_to_search = extract_dish_name_from_query(user_message_original)

        if not dish_to_search:
            print(
                f"Gemini không trích xuất được tên món ăn từ '{user_message_original}'."
            )
            bot_reply = "Xin lỗi, tôi chưa hiểu rõ bạn muốn hỏi về món ăn nào. Bạn có thể vui lòng cho biết tên món ăn cụ thể được không?"

        if dish_to_search:
            dish_details = get_dish_details(dish_to_search)

            if "error" in dish_details:
                bot_reply = dish_details["error"]
            elif "not_found" in dish_details:
                if dish_to_search.lower() == user_message_original.lower():
                    bot_reply = f"Xin lỗi, tôi không tìm thấy thông tin cho món '{dish_to_search}' trong cơ sở dữ liệu của mình."
                else:
                    bot_reply = f"Xin lỗi, tôi không tìm thấy thông tin cho món '{dish_to_search}' (được hiểu từ câu '{user_message_original}') trong cơ sở dữ liệu của mình."
                # Optional: Ask Gemini general knowledge
                # general_info_prompt = f"Cung cấp thông tin chung (nguyên liệu, cách làm nếu có) về món ăn '{dish_to_search}'. Nếu không biết, hãy nói không biết."
                # gemini_general_info = get_gemini_suggestion(general_info_prompt)
                # if gemini_general_info and "không biết" not in gemini_general_info.lower() and len(gemini_general_info) > 20:
                #     bot_reply += f"\n\nTuy nhiên, theo kiến thức chung của AI:\n{gemini_general_info}"

            elif "title" in dish_details:
                # Optional: Use Gemini to format better
                # bot_reply = format_dish_details_with_gemini(
                #     dish_details['title'],
                #     dish_details['ingredients'],
                #     dish_details['instructions']
                # )
                # Manual formatting:
                bot_reply = (
                    f"OK bạn! Để nấu món **{dish_details['title']}**, bạn cần:\n\n"
                    f"**Nguyên liệu:**\n{dish_details.get('ingredients', 'Chưa có thông tin')}\n\n"
                    f"**Hướng dẫn thực hiện:**\n{dish_details.get('instructions', 'Chưa có thông tin')}"
                )
            else:
                bot_reply = f"Đã có lỗi xảy ra khi tìm thông tin món '{dish_to_search}'. Vui lòng thử lại."
            # elif not bot_reply: # This was the fallback if dish_to_search was empty and bot_reply not set by vegetarian logic
            # Now, if dish_to_search is empty, bot_reply is set directly above, so this specific elif is not needed.
            # If dish_to_search is empty and bot_reply has already been set, we just return it.
            pass  # bot_reply has been set if dish_to_search was initially empty

        return JsonResponse({"reply": bot_reply})

    return JsonResponse({"reply": "Yêu cầu không hợp lệ."}, status=400)
