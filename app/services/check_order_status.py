import requests

API_URL = "https://kltn-green.vercel.app/order/status"

def check_order_status(order_code):
    '''
    Kiểm tra đơn đã thanh toán chưa
    status = 2: thành công
    '''
    try:
        url = f"{API_URL}/{order_code}"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json().get("data", {})
            return data.get("status")
        else:
            print(f"❌ Lỗi khi kiểm tra trạng thái đơn: {response.status_code}")
            return None
    except Exception as e:
        print("⚠️ Exception:", e)
        return None
        