#app/services/send_order.py
import requests
import time

ORDER_API_URL = "https://kltn-green.vercel.app/order"

#save_path="assets/latest_qr.png"

def send_order(items):
    """
    items: list of dicts, each with keys:
        - FoodId: str
        - Quantity: int
    response:
        - status
        - qr_code
        - order_code
    """
    try:
        payload = {"items": items}
        headers = {
            "User-Agent": "Mozilla/5.0 (Kivy App)",
            "Content-Type": "application/json"
        }

        start_time = time.time()
        response = requests.post(ORDER_API_URL, json=payload, headers=headers, timeout=10)
        duration = time.time() - start_time
        print(f"⏱ Gửi đơn mất {duration:.2f}s")
        
        if response.status_code in (200, 201):
            data = response.json().get("data", {})
            print("✅ Đặt hàng thành công:", data)
            return data.get("UID"), data.get("QR_URL")
        else:
            print(f"❌ Gửi đơn thất bại: {response.status_code}", response.text)
            return None, None
    except requests.exceptions.Timeout:
        print("⚠️ Timeout khi gửi đơn hàng")
        return None, None
    except requests.exceptions.RequestException as e:
        print("⚠️ Lỗi kết nối khi gửi đơn hàng:", e)
        return None, None