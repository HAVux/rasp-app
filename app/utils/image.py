import requests

def download_image(url, save_path="assets/temp_qr.png"):
    r = requests.get(url, stream=True)
    if r.status_code == 200:
        with open(save_path, 'wb') as f:
            for chunk in r:
                f.write(chunk)
        return save_path
    return "assets/qrcode/default.jpg"