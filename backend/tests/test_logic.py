import os
import pytest
from app.logic import is_valid_url, is_valid_alias, generate_short_code
from app.storage import storage

@pytest.fixture(autouse=True)
def clean_storage_fixture():
    """
    Automatically clears the in-memory database before and after each test
    to guarantee test isolation.
    """
    storage.clear()
    yield
    storage.clear()

def test_generate_short_code():
    """
    Test that generated short codes are correctly formatted (6 characters, alphanumeric)
    and produce no collisions across repeated calls.
    """
    # Verify properties of a single generated code
    code = generate_short_code()
    assert isinstance(code, str)
    assert len(code) == 6
    assert code.isalnum()

    # Verify no collisions across 1000 generated codes
    generated_codes = {generate_short_code() for _ in range(1000)}
    assert len(generated_codes) == 1000

def test_url_validation():
    """
    Test that URL validation correctly accepts well-formed URLs (including localhost)
    and rejects invalid or garbage input.
    """
    # Valid URLs
    assert is_valid_url("https://www.google.com") is True
    assert is_valid_url("http://github.com/profile") is True
    assert is_valid_url("http://localhost:8000/api/links") is True
    assert is_valid_url("https://sub-domain.example.co.uk?query=param&other=1") is True

    # Invalid URLs
    assert is_valid_url("garbage") is False
    assert is_valid_url("www.google.com") is False  # missing scheme
    assert is_valid_url("http://") is False  # missing host
    assert is_valid_url("https://.com") is False  # invalid host
    assert is_valid_url("ftp://files.example.com") is False  # unsupported scheme
    assert is_valid_url("") is False

def test_custom_alias_validation():
    """
    Test that custom alias validation accepts valid characters (alphanumeric, hyphens)
    and rejects invalid ones or bounds.
    """
    # Valid aliases
    assert is_valid_alias("my-custom-alias") is True
    assert is_valid_alias("Short123") is True
    assert is_valid_alias("a") is True  # Min boundary
    assert is_valid_alias("a" * 30) is True  # Max boundary

    # Invalid aliases
    assert is_valid_alias("my_custom_alias") is False  # contains underscore
    assert is_valid_alias("alias@123") is False  # contains special char
    assert is_valid_alias("") is False  # empty
    assert is_valid_alias("a" * 31) is False  # too long

def test_duplicate_long_url_submission():
    """
    Test that query by long URL returns the same code if already shortened.
    """
    url = "https://example.com"
    code = "ex1234"
    
    # Save the link first
    storage.save_link(code, url)
    
    # Query the existing URL
    existing = storage.get_link_by_url(url)
    assert existing is not None
    assert existing["short_code"] == code

    # Non-existing URL should return None
    assert storage.get_link_by_url("https://different.com") is None

def test_click_counter_increments():
    """
    Test that click count increments correctly on incremental hits.
    """
    code = "clk123"
    url = "https://example.com"
    
    storage.save_link(code, url)
    link = storage.get_link_by_code(code)
    assert link["clicks"] == 0
    
    # Increment click count
    success = storage.increment_clicks(code)
    assert success is True
    assert link["clicks"] == 1
    
    storage.increment_clicks(code)
    assert link["clicks"] == 2
    
    # Increment for non-existing code should return False
    assert storage.increment_clicks("missing") is False

def test_toggleable_failure():
    """
    This test is designed to fail intentionally if the environment variable
    TOGGLE_TEST_FAILURE is set to 'true'. Used for demoing CI failures.
    """
    is_triggered = os.environ.get("TOGGLE_TEST_FAILURE", "false").lower() == "true"
    if is_triggered:
        pytest.fail("Intentionally triggered test failure via TOGGLE_TEST_FAILURE=true")
    else:
        assert True
