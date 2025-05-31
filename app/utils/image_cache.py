# utils/image_cache.py
import os
import hashlib
import requests

CACHE_DIR = "cache_images"
FALLBACK_IMAGE = "assets/no-image-available.jpg"


def get_cached_image_path(url):
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)

    filename = hashlib.md5(url.encode()).hexdigest() + ".jpg"
    path = os.path.join(CACHE_DIR, filename)

    if not os.path.exists(path):
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                with open(path, "wb") as f:
                    f.write(response.content)
                print(f"📥 Cached: {url}")
            else:
                print(f"⚠️ Không thể tải ảnh {url} → dùng fallback")
                return FALLBACK_IMAGE
        except Exception as e:
            print(f"⚠️ Lỗi tải ảnh {url}: {e} → dùng fallback")
            return FALLBACK_IMAGE

    return path