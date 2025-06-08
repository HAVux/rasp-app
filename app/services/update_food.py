#app/services/update_food.py
import requests
import time
from app.utils.image_cache import get_cached_image_path

def fetch_food_data(api_url="https://kltn-green.vercel.app/food"):
    try:
        start_time = time.time()

        headers = {"User-Agent": "Mozilla/5.0 (Kivy App)"}
        response = requests.get(api_url, headers=headers, timeout=5)

        duration = time.time() - start_time
        print(f"⏱ Lấy menu mất {duration:.2f}s")

        if response.status_code == 200:
            res_json = response.json()
            print("lấy menu thành công")
            return [
                {
                    "food_id": item["_id"],
                    "name": item["Name"],
                    "price": item["Price"],
                    "image": get_cached_image_path(item["Image_url"]),
                    "available": item["Quantity"],
                    "type": "do_an" if item.get("Type") == 0 else "thuc_uong"
                }
                for item in res_json.get("data", []) if not item.get("deleted", False)
            ]
        else:
            print(f"❌ Không thể lấy dữ liệu: {response.status_code}")
            return []
    except requests.exceptions.Timeout:
        print("⚠️ Timeout khi gọi API lấy food")
        return []
    except requests.exceptions.RequestException as e:
        print("⚠️ Lỗi kết nối khi gọi API:", e)
        return []