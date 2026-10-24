import urllib.request
import io
import json
from PIL import Image

def test_locate():
    img = Image.new('RGB', (200, 200), color=(30, 40, 50))
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    img_bytes = buf.getvalue()

    boundary = '----WebKitFormBoundaryLookDoTest'
    body = (
        f'--{boundary}\r\n'
        f'Content-Disposition: form-data; name="instruction"\r\n\r\n'
        f'where do I download this?\r\n'
        f'--{boundary}\r\n'
        f'Content-Disposition: form-data; name="image"; filename="screenshot.png"\r\n'
        f'Content-Type: image/png\r\n\r\n'
    ).encode('utf-8') + img_bytes + f'\r\n--{boundary}--\r\n'.encode('utf-8')

    req = urllib.request.Request(
        'http://127.0.0.1:8000/api/locate',
        data=body,
        headers={'Content-Type': f'multipart/form-data; boundary={boundary}'}
    )
    with urllib.request.urlopen(req) as res:
        print('Status:', res.getcode())
        data = json.loads(res.read().decode())
        print('Returned JSON:', json.dumps(data, indent=2))

if __name__ == '__main__':
    test_locate()
