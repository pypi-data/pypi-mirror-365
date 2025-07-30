"""
Tests for the authentication module
"""

import pytest
from unittest.mock import patch, Mock
from bc2appsource.auth import AuthContext


class TestAuthContext:
    def test_init(self):
        """Test AuthContext initialization"""
        auth = AuthContext("tenant", "client", "secret")
        assert auth.tenant_id == "tenant"
        assert auth.client_id == "client"
        assert auth.client_secret == "secret"
        assert auth._access_token is None

    @patch('bc2appsource.auth.requests.post')
    def test_authenticate_success(self, mock_post):
        """Test successful authentication"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"access_token": "test_token"}
        mock_post.return_value = mock_response

        auth = AuthContext("tenant", "client", "secret")
        token = auth._authenticate()

        assert token == "test_token"
        mock_post.assert_called_once()

    @patch('bc2appsource.auth.requests.post')
    def test_authenticate_failure(self, mock_post):
        """Test authentication failure"""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Invalid request"
        mock_post.return_value = mock_response

        auth = AuthContext("tenant", "client", "secret")
        
        with pytest.raises(Exception) as exc_info:
            auth._authenticate()
        
        assert "Authentication failed" in str(exc_info.value)

    def test_get_headers(self):
        """Test get_headers method"""
        auth = AuthContext("tenant", "client", "secret")
        auth._access_token = "test_token"
        
        headers = auth.get_headers()
        
        assert headers["Authorization"] == "Bearer test_token"
        assert headers["Content-Type"] == "application/json"
