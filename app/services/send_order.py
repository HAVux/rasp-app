import requests

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
        response = requests.post(ORDER_API_URL, json=payload)
        if response.status_code in (200, 201):
            data = response.json().get("data", {})
            print("✅ Đặt hàng thành công:", data)
            return data.get("UID"), data.get("QR_URL")
        else:
            print(f"❌ Gửi đơn thất bại: {response.status_code}", response.text)
            return None, None
    except Exception as e:
        print("⚠️ Lỗi khi gửi đơn hàng:", e)
        return None, None