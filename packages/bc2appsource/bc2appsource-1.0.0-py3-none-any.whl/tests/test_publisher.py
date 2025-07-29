"""
Tests for the publisher module
"""

import pytest
import tempfile
import os
from unittest.mock import patch, Mock, mock_open
from bc2appsource.publisher import AppSourcePublisher, PublishResult


class TestAppSourcePublisher:
    def test_init(self):
        """Test AppSourcePublisher initialization"""
        publisher = AppSourcePublisher("tenant", "client", "secret")
        assert publisher.auth.tenant_id == "tenant"
        assert publisher.base_url == "https://api.partner.microsoft.com/v1.0"

    @patch('bc2appsource.publisher.requests.get')
    def test_get_products_success(self, mock_get):
        """Test successful product retrieval"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"value": [{"name": "Test Product", "id": "123"}]}
        mock_get.return_value = mock_response

        publisher = AppSourcePublisher("tenant", "client", "secret")
        with patch.object(publisher.auth, 'get_headers', return_value={}):
            products = publisher.get_products()

        assert len(products) == 1
        assert products[0]["name"] == "Test Product"

    def test_find_product_by_name(self):
        """Test finding product by name"""
        publisher = AppSourcePublisher("tenant", "client", "secret")
        
        with patch.object(publisher, 'get_products', return_value=[
            {"name": "Product A", "id": "123"},
            {"name": "Product B", "id": "456"}
        ]):
            product_id = publisher.find_product_by_name("Product B")
            assert product_id == "456"
            
            # Test not found
            product_id = publisher.find_product_by_name("Product C")
            assert product_id is None

    def test_resolve_app_file_direct_path(self):
        """Test resolving direct file path"""
        publisher = AppSourcePublisher("tenant", "client", "secret")
        
        with tempfile.NamedTemporaryFile(suffix=".app", delete=False) as tmp:
            try:
                result = publisher.resolve_app_file(tmp.name)
                assert result == tmp.name
            finally:
                os.unlink(tmp.name)

    def test_resolve_app_file_not_found(self):
        """Test resolving non-existent file"""
        publisher = AppSourcePublisher("tenant", "client", "secret")
        
        with pytest.raises(FileNotFoundError):
            publisher.resolve_app_file("/non/existent/file.app")

    def test_publish_missing_params(self):
        """Test publish with missing parameters"""
        publisher = AppSourcePublisher("tenant", "client", "secret")
        
        result = publisher.publish("test.app")
        
        assert not result.success
        assert "Either product_name or product_id must be provided" in result.error

    @patch('bc2appsource.publisher.requests.post')
    def test_submit_to_appsource_success(self, mock_post):
        """Test successful AppSource submission"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "submission_123"}
        mock_post.return_value = mock_response

        publisher = AppSourcePublisher("tenant", "client", "secret")
        
        with tempfile.NamedTemporaryFile(suffix=".app", delete=False) as tmp:
            try:
                with patch.object(publisher.auth, 'get_access_token', return_value="token"):
                    result = publisher.submit_to_appsource("product_123", tmp.name)
                
                assert result.success
                assert result.submission_id == "submission_123"
            finally:
                os.unlink(tmp.name)
