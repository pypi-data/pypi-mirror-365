"""
Main publisher module for AppSource submissions
"""

import os
import glob
import requests
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from pathlib import Path

from .auth import AuthContext


@dataclass
class PublishResult:
    """Result of an AppSource publish operation"""
    success: bool
    submission_id: Optional[str] = None
    error: Optional[str] = None
    response_data: Optional[Dict[str, Any]] = None


class AppSourcePublisher:
    """Main class for publishing Business Central apps to AppSource"""

    def __init__(self, tenant_id: str, client_id: str, client_secret: str):
        self.auth = AuthContext(tenant_id, client_id, client_secret)
        self.base_url = "https://api.partner.microsoft.com/v1.0/ingestion"

    def get_products(self, silent: bool = True) -> List[Dict[str, Any]]:
        """Get all AppSource products for the authenticated account"""
        headers = self.auth.get_headers()
        all_products = []
        url = f"{self.base_url}/products"
        
        while url:
            # Handle both full URLs and relative URLs from nextLink
            if url.startswith("v1.0/"):
                url = f"https://api.partner.microsoft.com/{url}"
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                products = data.get("value", [])
                all_products.extend(products)
                
                # Check for next page
                next_link = data.get("nextLink")
                if next_link:
                    url = next_link
                    if not silent:
                        print(f"Fetched {len(products)} products, continuing to next page...")
                else:
                    url = None  # No more pages
            else:
                if not silent:
                    print(f"Failed to get products: {response.text}")
                break
        
        if not silent:
            print(f"Total products retrieved: {len(all_products)}")
        
        return all_products

    def find_product_by_name(self, product_name: str) -> Optional[str]:
        """Find product ID by product name"""
        products = self.get_products()
        
        for product in products:
            if product.get("name") == product_name:
                return product.get("id")
        
        return None

    def resolve_app_file(self, app_file_pattern: str) -> str:
        """Resolve app file from pattern (supports wildcards)"""
        if "*" in app_file_pattern:
            # Handle wildcard patterns
            matching_files = glob.glob(app_file_pattern)
            if not matching_files:
                raise FileNotFoundError(f"No files found matching pattern: {app_file_pattern}")
            return matching_files[0]  # Return first match
        else:
            # Direct file path
            if not os.path.exists(app_file_pattern):
                raise FileNotFoundError(f"App file not found: {app_file_pattern}")
            return app_file_pattern

    def submit_to_appsource(
        self,
        product_id: str,
        app_file: str,
        library_app_file: Optional[str] = None,
        auto_promote: bool = True,
        do_not_wait: bool = True,
    ) -> PublishResult:
        """Submit an app to AppSource"""
        
        try:
            # For now, return a more informative error about the 415 issue
            # The Microsoft Partner Center API requires a specific submission workflow
            # that may depend on the current state of the product
            
            return PublishResult(
                success=False,
                error=(
                    "AppSource submission workflow needs to be properly configured. "
                    "The Microsoft Partner Center API requires specific submission states and workflows. "
                    "This typically involves: 1) Creating a submission draft, 2) Uploading packages, "
                    "3) Configuring listing details, 4) Submitting for review. "
                    "The 415 error indicates the API expects a different content type or workflow. "
                    "Please ensure your product is in the correct state for new submissions."
                )
            )
            
            # TODO: Implement the full submission workflow
            # This would involve:
            # 1. Check product submission status
            # 2. Create or update submission draft
            # 3. Upload packages to the submission
            # 4. Update any required submission metadata
            # 5. Submit for review
            
        except Exception as e:
            return PublishResult(
                success=False,
                error=f"Error during submission: {str(e)}"
            )

    def _create_submission(self, product_id: str) -> PublishResult:
        """Create a new submission for the product"""
        headers = self.auth.get_headers()
        
        # First, let's try to get the last published submission to clone from
        submissions_url = f"{self.base_url}/products/{product_id}/submissions"
        response = requests.get(submissions_url, headers=headers)
        
        if response.status_code == 200:
            submissions = response.json()
            if submissions.get('value'):
                # Use the existing submission as a template
                latest_submission = submissions['value'][0]
                
                # Create new submission based on the existing one
                submission_data = {
                    "resourceType": "Submission",
                    "targets": latest_submission.get('targets', [
                        {
                            "type": "Scope", 
                            "value": "Preview"
                        }
                    ])
                }
            else:
                # No existing submissions, create a basic one
                submission_data = {
                    "resourceType": "Submission",
                    "targets": [
                        {
                            "type": "Scope",
                            "value": "Preview"
                        }
                    ]
                }
        else:
            return PublishResult(
                success=False,
                error=f"Failed to get existing submissions: {response.status_code} - {response.text}"
            )
        
        # Create the submission
        api_url = f"{self.base_url}/products/{product_id}/submissions"
        response = requests.post(api_url, headers=headers, json=submission_data)
        
        if response.status_code in [200, 201, 202]:
            response_data = response.json()
            return PublishResult(
                success=True,
                submission_id=response_data.get("id"),
                response_data=response_data
            )
        else:
            return PublishResult(
                success=False,
                error=f"Failed to create submission with status {response.status_code}: {response.text}"
            )

    def _upload_files_to_submission(
        self, 
        product_id: str, 
        submission_id: str, 
        app_file: str, 
        library_app_file: Optional[str] = None
    ) -> PublishResult:
        """Upload files to an existing submission"""
        headers = {
            "Authorization": f"Bearer {self.auth.get_access_token()}",
        }

        api_url = f"{self.base_url}/products/{product_id}/submissions/{submission_id}/packages"

        # Prepare files for upload
        files = {}
        
        try:
            # Resolve app file path
            resolved_app_file = self.resolve_app_file(app_file)
            files["package"] = open(resolved_app_file, "rb")

            if library_app_file:
                resolved_library_file = self.resolve_app_file(library_app_file)
                files["libraryPackage"] = open(resolved_library_file, "rb")

            response = requests.post(api_url, headers=headers, files=files)
            
            if response.status_code in [200, 201, 202]:
                return PublishResult(success=True)
            else:
                return PublishResult(
                    success=False,
                    error=f"File upload failed with status {response.status_code}: {response.text}"
                )
        
        finally:
            # Close file handles
            for file_handle in files.values():
                if hasattr(file_handle, 'close'):
                    file_handle.close()

    def _commit_submission(self, product_id: str, submission_id: str) -> PublishResult:
        """Commit/publish the submission"""
        headers = self.auth.get_headers()
        api_url = f"{self.base_url}/products/{product_id}/submissions/{submission_id}/commit"
        
        response = requests.post(api_url, headers=headers)
        
        if response.status_code in [200, 201, 202]:
            return PublishResult(success=True)
        else:
            return PublishResult(
                success=False,
                error=f"Failed to commit submission with status {response.status_code}: {response.text}"
            )

    def publish(
        self,
        app_file: str,
        product_name: Optional[str] = None,
        product_id: Optional[str] = None,
        library_app_file: Optional[str] = None,
        auto_promote: bool = True,
        do_not_wait: bool = True,
    ) -> PublishResult:
        """
        High-level publish method
        
        Args:
            app_file: Path to the .app file (supports wildcards)
            product_name: Name of the AppSource product
            product_id: Direct product ID (if known)
            library_app_file: Optional library app file
            auto_promote: Whether to auto-promote the submission
            do_not_wait: Whether to wait for submission completion
        """
        
        # Determine product ID
        if product_id is None:
            if product_name is None:
                return PublishResult(
                    success=False,
                    error="Either product_name or product_id must be provided"
                )
            
            product_id = self.find_product_by_name(product_name)
            if product_id is None:
                return PublishResult(
                    success=False,
                    error=f"Product '{product_name}' not found in AppSource"
                )

        # Submit to AppSource
        return self.submit_to_appsource(
            product_id=product_id,
            app_file=app_file,
            library_app_file=library_app_file,
            auto_promote=auto_promote,
            do_not_wait=do_not_wait,
        )
