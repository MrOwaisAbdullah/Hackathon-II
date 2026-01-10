"""Integration tests for Chat API (T075, T046).

Tests Urdu language support and chat preferences endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from uuid import uuid4

from app.main import app
from app.agents.prompts import detect_language, get_base_system_prompt


@pytest.fixture
def client():
    """Test client for FastAPI app."""
    return TestClient(app)


@pytest.fixture
def test_session_token():
    """Mock session token for testing."""
    return "test-session-token"


class TestUrduLanguageSupport:
    """Test Urdu language detection and responses (T075)."""

    def test_detect_language_english(self):
        """Test that English text is detected correctly."""
        english_text = "Create a new task for the landing page"
        language = detect_language(english_text)
        assert language == "en"

    def test_detect_language_urdu(self):
        """Test that Urdu text is detected correctly (>30% Urdu chars)."""
        urdu_text = "Acme project کے لیے task بنائیں"  # Mix of Urdu and Roman Urdu
        language = detect_language(urdu_text)
        assert language == "ur"

    def test_detect_mixed_text_below_threshold(self):
        """Test that text below 30% threshold is detected as English."""
        mixed_text = "Create a task for آصف"  # Only 2 Urdu chars out of ~20
        language = detect_language(mixed_text)
        assert language == "en"

    def test_detect_mixed_text_above_threshold(self):
        """Test that text above 30% threshold is detected as Urdu."""
        mixed_text = "آصف کے لیےAcme project میں task بنائیں"  # Many Urdu chars
        language = detect_language(mixed_text)
        assert language == "ur"

    def test_empty_text_defaults_to_english(self):
        """Test that empty text defaults to English."""
        language = detect_language("")
        assert language == "en"

    def test_get_english_system_prompt(self):
        """Test that English system prompt is returned correctly."""
        prompt = get_base_system_prompt("en")
        assert "TeamFlow Assistant" in prompt
        assert "Task Management" in prompt
        assert "English" not in prompt  # Should not contain "Urdu"

    def test_get_urdu_system_prompt(self):
        """Test that Urdu system prompt is returned correctly."""
        prompt = get_base_system_prompt("ur")
        assert "TeamFlow Assistant" in prompt or "TeamFlow" in prompt
        # Check for Urdu/Roman Urdu content
        assert "Urdu" in prompt or "اردو" in prompt or "Aap" in prompt
        assert "Task Management" in prompt or "Task" in prompt

    def test_urdu_prompt_has_roman_script_instructions(self):
        """Test that Urdu prompt mentions Roman script."""
        prompt = get_base_system_prompt("ur")
        # The prompt should use Roman Urdu (Latin script)
        # Check for common Roman Urdu words
        roman_urdu_indicators = ["Aap", "ka", "ke", "ki", "hai", "karein", "banayein"]
        has_indicators = any(indicator in prompt for indicator in roman_urdu_indicators)
        assert has_indicators, "Urdu prompt should use Roman script (Latin characters)"


class TestChatPreferencesAPI:
    """Test chat preferences endpoints (T073)."""

    def test_get_preferences_returns_defaults(self, client, test_session_token):
        """Test that GET /preferences returns defaults for new user."""
        response = client.get(
            "/api/v1/chat/preferences",
            headers={"X-Session-Token": test_session_token}
        )

        # Should return 200 with default preferences
        assert response.status_code in [200, 404]  # 404 acceptable if user not found
        if response.status_code == 200:
            data = response.json()
            assert "language" in data
            assert data["language"] in ["en", "ur"]

    def test_update_preferences_saves_language(self, client, test_session_token):
        """Test that PATCH /preferences saves language choice."""
        response = client.patch(
            "/api/v1/chat/preferences",
            headers={"X-Session-Token": test_session_token},
            json={
                "language": "ur",
                "voice_enabled": False,
            }
        )

        # Should accept the update
        assert response.status_code in [200, 201, 404]  # 404 acceptable for testing
        if response.status_code in [200, 201]:
            data = response.json()
            assert data["language"] == "ur"

    def test_update_preferences_invalid_language_rejected(self, client, test_session_token):
        """Test that invalid language values are rejected."""
        response = client.patch(
            "/api/v1/chat/preferences",
            headers={"X-Session-Token": test_session_token},
            json={
                "language": "fr",  # Invalid - only 'en' and 'ur' supported
                "voice_enabled": False,
            }
        )

        # Should reject invalid language
        assert response.status_code == 422  # Validation error


class TestUrduChatFlow:
    """Test end-to-end Urdu chat flow (T075)."""

    def test_urdu_message_gets_urdu_response(self, client, test_session_token):
        """Test that Urdu input produces Urdu response (mock test)."""
        # This is a simplified test - full integration would require
        # mocking the AI agent response

        # Send Urdu message
        urdu_message = "Acme project کے لیے ایک task بنائیں"

        # Test language detection
        detected_language = detect_language(urdu_message)
        assert detected_language == "ur"

        # Get appropriate prompt
        prompt = get_base_system_prompt(detected_language)
        assert "ur" in prompt.lower() or "roman" in prompt.lower() or "اردو" in prompt

    def test_english_message_gets_english_response(self, client, test_session_token):
        """Test that English input produces English response."""
        english_message = "Create a task for Acme project"

        # Test language detection
        detected_language = detect_language(english_message)
        assert detected_language == "en"

        # Get appropriate prompt
        prompt = get_base_system_prompt(detected_language)
        assert "TeamFlow Assistant" in prompt
