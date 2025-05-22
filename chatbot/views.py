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
        except json.JSONDecodeError:
            return JsonResponse(
                {"reply": "Lỗi: Dữ liệu gửi lên không hợp lệ."}, status=400
            )

        if not user_message_original:
            return JsonResponse({"reply": "Bạn muốn hỏi về món ăn nào nhỉ?"})

        bot_reply = ""

        # In ra log để debug
        print(f"[CHAT] Câu hỏi người dùng: '{user_message_original}'")

        dish_to_search = extract_dish_name_from_query(user_message_original)

        if not dish_to_search:
            print(f"Không trích xuất được tên món ăn từ '{user_message_original}'.")
            bot_reply = "Xin lỗi, tôi chưa hiểu rõ bạn muốn hỏi về món ăn nào. Bạn có thể vui lòng cho biết tên món ăn cụ thể được không?"
        else:
            print(f"[CHAT] Tìm kiếm món: '{dish_to_search}'")
            dish_details = get_dish_details(dish_to_search)
            print(f"[CHAT] Kết quả tìm kiếm: {dish_details.keys()}")

            if "error" in dish_details:
                bot_reply = dish_details["error"]
                print(f"[CHAT] Lỗi: {bot_reply}")
            elif "not_found" in dish_details:
                if dish_to_search.lower() == user_message_original.lower():
                    bot_reply = f"Xin lỗi, tôi không tìm thấy thông tin cho món '{dish_to_search}' trong cơ sở dữ liệu của mình."
                else:
                    bot_reply = f"Xin lỗi, tôi không tìm thấy thông tin cho món '{dish_to_search}' (được hiểu từ câu '{user_message_original}') trong cơ sở dữ liệu của mình."
                print(f"[CHAT] Không tìm thấy món: {bot_reply}")
            elif "title" in dish_details:
                print(f"[CHAT] Tìm thấy món ăn: {dish_details['title']}")
                # Format ingredients with line breaks
                ingredients_text = ""
                if "ingredients" in dish_details and dish_details["ingredients"]:
                    # Check if ingredients is a string or a list
                    if isinstance(dish_details["ingredients"], list):
                        ingredients_text = "\n".join(
                            [
                                f"• {ingredient}"
                                for ingredient in dish_details["ingredients"]
                            ]
                        )
                    else:
                        # Split by commas or semicolons if it's a string
                        ingredients_list = [
                            i.strip()
                            for i in dish_details["ingredients"]
                            .replace(";", ",")
                            .split(",")
                        ]
                        ingredients_text = "\n".join(
                            [
                                f"• {ingredient}"
                                for ingredient in ingredients_list
                                if ingredient
                            ]
                        )

                # Format instructions with line breaks
                instructions_text = ""
                if "instructions" in dish_details and dish_details["instructions"]:
                    if isinstance(dish_details["instructions"], list):
                        instructions_text = "\n".join(
                            [
                                f"{i + 1}. {step}"
                                for i, step in enumerate(dish_details["instructions"])
                            ]
                        )
                    else:
                        # Try to identify steps by numbers or periods
                        instructions = dish_details["instructions"]
                        # Replace common Vietnamese step indicators
                        for indicator in ["Bước ", "bước "]:
                            instructions = instructions.replace(
                                indicator, "\n" + indicator
                            )
                        instructions_text = instructions

                # Construct the final formatted reply
                bot_reply = (
                    f"OK bạn! Để nấu món **{dish_details['title']}**, bạn cần:\n\n"
                    f"**Nguyên liệu:**\n{ingredients_text}\n\n"
                    f"**Hướng dẫn thực hiện:**\n{instructions_text}"
                )
            else:
                bot_reply = f"Đã có lỗi xảy ra khi tìm thông tin món '{dish_to_search}'. Vui lòng thử lại."

        return JsonResponse({"reply": bot_reply})

    return JsonResponse({"reply": "Yêu cầu không hợp lệ."}, status=400)
