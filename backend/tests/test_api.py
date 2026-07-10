import pytest
from fastapi.testclient import TestClient
import urllib.parse

from app.main import app
from app.storage import storage

client = TestClient(app)

@pytest.fixture(autouse=True)
def clean_storage():
    storage.clear()
    yield
    storage.clear()

def test_shorten_new_url_with_qr_code():
    """
    Test creating a new shortened URL with a QR code.
    The QR code URL must contain the original URL.
    """
    url = "https://example.com/some/path?param=1"
    response = client.post(
        "/shorten",
        json={"url": url, "generate_qr": True}
    )
    assert response.status_code == 201
    data = response.json()
    short_url = data["short_url"]
    qr_code = data["qr_code"]
    
    # Assert that the QR code points to the original URL, not the shortened URL
    expected_data_param = urllib.parse.quote(url)
    assert f"data={expected_data_param}" in qr_code
    assert f"data={urllib.parse.quote(short_url)}" not in qr_code

def test_shorten_existing_url_with_qr_code():
    """
    Test requesting a QR code for an already shortened URL.
    The QR code URL must contain the original URL.
    """
    url = "https://example.com/duplicate"
    # First request: shorten without QR
    response1 = client.post(
        "/shorten",
        json={"url": url, "generate_qr": False}
    )
    assert response1.status_code == 201
    short_url = response1.json()["short_url"]
    
    # Second request: shorten with QR (should return existing link with new QR)
    response2 = client.post(
        "/shorten",
        json={"url": url, "generate_qr": True}
    )
    assert response2.status_code == 201
    data = response2.json()
    qr_code = data["qr_code"]
    
    expected_data_param = urllib.parse.quote(url)
    assert f"data={expected_data_param}" in qr_code
