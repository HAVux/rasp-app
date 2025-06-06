import requests

API_URL = "https://kltn-green.vercel.app/order/status/"

def cancel_order(order_code):
    """
    Hủy đơn hàng theo mã order_code bằng cách gửi PUT.
    Trạng thái 4 = Đã hủy.
    """
    try:
        url = f"{API_URL}/{order_code}"
        payload = {"status": 4}
        headers = {"Content-Type": "application/json"}

        response = requests.post(url, json=payload, headers=headers)

        if response.status_code == 200:
            print(f"✅ Hủy đơn hàng {order_code} thành công.")
            return True
        else:
            print(f"❌ Hủy đơn thất bại: {response.status_code} - {response.text}")
            return False

    except Exception as e:
        print(f"⚠️ Lỗi khi hủy đơn: {e}")
        return False
