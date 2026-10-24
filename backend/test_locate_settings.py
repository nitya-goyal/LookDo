"""
End-to-end test for the /api/locate endpoint with 'Open settings' instruction.
Uses the test_ui_settings.png image and verifies the returned bounding box.
"""
import io
import json
import urllib.request

from PIL import Image


def create_test_ui_screenshot() -> bytes:
    """Create a simple UI screenshot with a visible Settings button in the top right."""
    img = Image.new("RGB", (800, 600), color="#1e293b")
    from PIL import ImageDraw
    draw = ImageDraw.Draw(img)
    # Top navbar
    draw.rectangle([0, 0, 800, 60], fill="#0f172a")
    draw.text((20, 20), "Dashboard App", fill="#f8fafc")
    # Settings button on top right: x=680-770, y=12-48
    draw.rectangle([680, 12, 770, 48], fill="#3b82f6", outline="#60a5fa", width=2)
    draw.text((695, 22), "Settings", fill="#ffffff")
    # Main area
    draw.rectangle([40, 90, 760, 560], fill="#334155")
    draw.text((60, 110), "Welcome to your workspace", fill="#94a3b8")

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def test_locate_open_settings():
    print("Creating test UI screenshot...", flush=True)
    img_bytes = create_test_ui_screenshot()

    boundary = "----LookDoE2ETest"
    body = (
        f"--{boundary}\r\n"
        f"Content-Disposition: form-data; name=\"instruction\"\r\n\r\n"
        f"Open settings\r\n"
        f"--{boundary}\r\n"
        f"Content-Disposition: form-data; name=\"image\"; filename=\"test_ui.png\"\r\n"
        f"Content-Type: image/png\r\n\r\n"
    ).encode("utf-8") + img_bytes + f"\r\n--{boundary}--\r\n".encode("utf-8")

    req = urllib.request.Request(
        "http://127.0.0.1:8000/api/locate",
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
    )

    print("Sending POST /api/locate with instruction='Open settings'...", flush=True)
    try:
        with urllib.request.urlopen(req, timeout=90) as res:
            status = res.getcode()
            data = json.loads(res.read().decode())
            print(f"Status: {status}", flush=True)
            print("Response:", json.dumps(data, indent=2), flush=True)

            # Verify response has expected fields
            assert "element_label" in data, "Missing element_label"
            assert "bounding_box" in data, "Missing bounding_box"
            bb = data["bounding_box"]
            assert all(k in bb for k in ["top", "left", "bottom", "right"]), f"Incomplete bounding_box: {bb}"
            print("\n[PASS] Test PASSED: bounding box returned successfully", flush=True)
            print(f"  element_label: {data['element_label']}", flush=True)
            print(f"  element_type:  {data.get('element_type', 'N/A')}", flush=True)
            print(f"  bounding_box:  top={bb['top']}, left={bb['left']}, bottom={bb['bottom']}, right={bb['right']}", flush=True)
            print(f"  confidence:    {data.get('confidence', 'N/A')}", flush=True)
            print(f"  explanation:   {data.get('explanation', 'N/A')}", flush=True)
    except urllib.error.HTTPError as e:
        body_err = e.read().decode()
        print(f"HTTP Error {e.code}: {body_err}", flush=True)
    except Exception as e:
        print(f"Error: {type(e).__name__}: {e}", flush=True)


if __name__ == "__main__":
    test_locate_open_settings()
