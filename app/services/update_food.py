import requests
from app.utils.image_cache import get_cached_image_path

def fetch_food_data(api_url="https://kltn-green.vercel.app/food"):
    try:
        response = requests.get(api_url)
        if response.status_code == 200:
            res_json = response.json()
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
    except Exception as e:
        print("⚠️ Lỗi khi gọi API:", e)
        return []