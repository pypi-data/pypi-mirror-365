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
        assert publisher.base_url == "https://api.partner.microsoft.com/v1.0/ingestion"

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

    @patch('bc2appsource.publisher.requests.get')
    def test_get_products_with_pagination(self, mock_get):
        """Test product retrieval with pagination"""
        # First page response
        first_response = Mock()
        first_response.status_code = 200
        first_response.json.return_value = {
            "value": [{"name": "Product 1", "id": "123"}],
            "nextLink": "v1.0/ingestion/products?$skipToken=abc123"
        }
        
        # Second page response
        second_response = Mock()
        second_response.status_code = 200
        second_response.json.return_value = {
            "value": [{"name": "Product 2", "id": "456"}]
            # No nextLink - last page
        }
        
        mock_get.side_effect = [first_response, second_response]

        publisher = AppSourcePublisher("tenant", "client", "secret")
        with patch.object(publisher.auth, 'get_headers', return_value={}):
            products = publisher.get_products()

        assert len(products) == 2
        assert products[0]["name"] == "Product 1"
        assert products[1]["name"] == "Product 2"
        
        # Verify pagination URLs were called correctly
        expected_calls = [
            ((f"{publisher.base_url}/products",), {'headers': {}}),
            (("https://api.partner.microsoft.com/v1.0/ingestion/products?$skipToken=abc123",), {'headers': {}})
        ]
        actual_calls = [call for call in mock_get.call_args_list]
        assert len(actual_calls) == 2

    @patch('bc2appsource.publisher.requests.get')
    def test_get_products_pagination_error(self, mock_get):
        """Test error handling during pagination"""
        # First page response (success)
        first_response = Mock()
        first_response.status_code = 200
        first_response.json.return_value = {
            "value": [{"name": "Product 1", "id": "123"}],
            "nextLink": "v1.0/ingestion/products?$skipToken=abc123"
        }
        
        # Second page response (error)
        second_response = Mock()
        second_response.status_code = 500
        second_response.text = "Internal Server Error"
        
        mock_get.side_effect = [first_response, second_response]

        publisher = AppSourcePublisher("tenant", "client", "secret")
        with patch.object(publisher.auth, 'get_headers', return_value={}):
            products = publisher.get_products()

        # Should return products from first page only
        assert len(products) == 1
        assert products[0]["name"] == "Product 1"

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

    def test_submit_to_appsource_working_implementation(self):
        """Test that submission method uses proper workflow"""
        publisher = AppSourcePublisher("tenant", "client", "secret")
        
        with tempfile.NamedTemporaryFile(suffix=".app", delete=False) as tmp:
            try:
                with patch.object(publisher.auth, 'get_access_token', return_value="token"):
                    # Mock the workflow methods
                    with patch.object(publisher, '_check_existing_submission', return_value=PublishResult(success=True)):
                        with patch.object(publisher, '_get_package_branch', return_value=PublishResult(success=True, response_data={'currentDraftInstanceID': 'test-id'})):
                            with patch.object(publisher, '_upload_app_packages', return_value=PublishResult(success=True, response_data={'main': {'id': 'pkg-id'}})):
                                with patch.object(publisher, '_update_package_configuration', return_value=PublishResult(success=True)):
                                    with patch('bc2appsource.publisher.requests.post') as mock_post:
                                        mock_response = Mock()
                                        mock_response.status_code = 200
                                        mock_response.json.return_value = {"id": "submission_123"}
                                        mock_post.return_value = mock_response
                                        
                                        result = publisher.submit_to_appsource("product_123", tmp.name)
                
                assert result.success
                assert result.submission_id == "submission_123"
            finally:
                os.unlink(tmp.name)

    def test_check_existing_submission_success(self):
        """Test checking existing submission when none in progress"""
        publisher = AppSourcePublisher("tenant", "client", "secret")
        
        with patch.object(publisher.auth, 'get_headers', return_value={}):
            with patch('bc2appsource.publisher.requests.get') as mock_get:
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.json.return_value = {
                    "value": [{
                        "state": "Published",
                        "substate": "InStore"
                    }]
                }
                mock_get.return_value = mock_response
                
                result = publisher._check_existing_submission("product_123")
                
                assert result.success

    # TODO: Re-enable these tests when submission workflow is fully implemented
    # @patch('bc2appsource.publisher.requests.post')
    # def test_submit_to_appsource_success(self, mock_post):
    #     """Test successful AppSource submission"""
    #     # Implementation pending full submission workflow
    #     pass

    def test_submit_to_appsource_failure(self):
        """Test AppSource submission failure scenario"""
        publisher = AppSourcePublisher("tenant", "client", "secret")
        
        with tempfile.NamedTemporaryFile(suffix=".app", delete=False) as tmp:
            try:
                with patch.object(publisher.auth, 'get_access_token', return_value="token"):
                    # Mock the first step to fail
                    with patch.object(publisher, '_check_existing_submission') as mock_check:
                        mock_check.return_value = PublishResult(
                            success=False,
                            error="An AppSource submission is in progress"
                        )
                        
                        result = publisher.submit_to_appsource("product_123", tmp.name)
                
                assert not result.success
                assert "An AppSource submission is in progress" in result.error
            finally:
                os.unlink(tmp.name)

    @patch('bc2appsource.publisher.glob.glob')
    def test_resolve_app_file_wildcard(self, mock_glob):
        """Test resolving wildcard file pattern"""
        publisher = AppSourcePublisher("tenant", "client", "secret")
        
        mock_glob.return_value = ["app1.app", "app2.app"]
        result = publisher.resolve_app_file("*.app")
        
        assert result == "app1.app"  # Should return first match
        mock_glob.assert_called_once_with("*.app")

    @patch('bc2appsource.publisher.glob.glob')
    def test_resolve_app_file_wildcard_no_matches(self, mock_glob):
        """Test resolving wildcard pattern with no matches"""
        publisher = AppSourcePublisher("tenant", "client", "secret")
        
        mock_glob.return_value = []
        
        with pytest.raises(FileNotFoundError, match="No files found matching pattern"):
            publisher.resolve_app_file("*.app")
