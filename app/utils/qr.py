import requests
import os
import uuid
import ssl
import urllib.request

def download_qr_image(qr_url, save_dir="cache_images"):
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    filename = f"qr_{uuid.uuid4().hex}.png"
    filepath = os.path.join(save_dir, filename)

    try:
        # Cách 1: requests + verify SSL
        r = requests.get(qr_url, timeout=5)
        r.raise_for_status()
        with open(filepath, 'wb') as f:
            f.write(r.content)
        print(f"✅ QR đã tải và lưu vào: {filepath}")
        return filepath
    except requests.exceptions.SSLError as ssl_err:
        print("⚠️ SSL ERROR khi tải QR:", ssl_err)
        try:
            # Cách 2: urllib + bỏ verify
            ssl_context = ssl._create_unverified_context()
            urllib.request.urlretrieve(qr_url, filepath, context=ssl_context)
            print(f"⚠️ Đã tải QR bằng urllib (bỏ verify): {filepath}")
            return filepath
        except Exception as e:
            print("❌ Tải QR thất bại hoàn toàn:", e)
            return None
    except Exception as e:
        print("❌ Lỗi khi tải QR:", e)
        return None
