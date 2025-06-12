#app/services/check_order_status.py
import requests
from app.services.api_config import STATUS_API_URL

def check_order_status(order_code):
    '''
    Kiểm tra đơn đã thanh toán chưa
    status = 2: thành công
    '''
    headers = {
            "User-Agent": "Mozilla/5.0 (Kivy App)",
            "Content-Type": "application/json"
        }
    
    try:
        url = f"{STATUS_API_URL}/{order_code}"
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json().get("data", {})
            return data.get("status")
        else:
            print(f"❌ Lỗi khi kiểm tra trạng thái đơn: {response.status_code}")
            return None
    except Exception as e:
        print("⚠️ Exception:", e)
        return None
        