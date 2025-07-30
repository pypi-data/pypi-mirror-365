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
        """Submit an app to AppSource using the correct Microsoft Partner Center workflow"""
        
        try:
            # Step 1: Check if there's already a submission in progress
            existing_submission = self._check_existing_submission(product_id)
            if existing_submission and not existing_submission.success:
                return existing_submission
            
            # Step 2: Get package branch information
            package_branch = self._get_package_branch(product_id)
            if not package_branch.success:
                return package_branch
            
            package_instance_id = package_branch.response_data.get('currentDraftInstanceID')
            
            # Step 3: Upload app files to package storage
            upload_result = self._upload_app_packages(product_id, package_instance_id, app_file, library_app_file)
            if not upload_result.success:
                return upload_result
            
            # Step 4: Update package configuration
            config_result = self._update_package_configuration(product_id, package_instance_id, upload_result.response_data)
            if not config_result.success:
                return config_result
            
            # Step 5: Create the submission
            submission_body = {
                "resourceType": "SubmissionCreationRequest",
                "targets": [
                    {
                        "type": "Scope",
                        "value": "preview"
                    }
                ],
                "resources": [
                    {
                        "type": "Package",
                        "value": package_instance_id
                    }
                ]
            }
            
            headers = self.auth.get_headers()
            api_url = f"{self.base_url}/products/{product_id}/submissions"
            
            response = requests.post(api_url, headers=headers, json=submission_body)
            
            if response.status_code in [200, 201, 202]:
                response_data = response.json()
                submission_id = response_data.get("id")
                
                if not do_not_wait:
                    # Wait for submission to complete
                    self._wait_for_submission(product_id, submission_id, auto_promote)
                
                return PublishResult(
                    success=True,
                    submission_id=submission_id,
                    response_data=response_data
                )
            else:
                return PublishResult(
                    success=False,
                    error=f"Submission creation failed with status {response.status_code}: {response.text}"
                )
        
        except Exception as e:
            return PublishResult(
                success=False,
                error=f"Error during submission: {str(e)}"
            )

    def _check_existing_submission(self, product_id: str) -> PublishResult:
        """Check if there's already a submission in progress"""
        headers = self.auth.get_headers()
        api_url = f"{self.base_url}/products/{product_id}/submissions"
        
        response = requests.get(api_url, headers=headers)
        if response.status_code != 200:
            return PublishResult(
                success=False,
                error=f"Failed to check existing submissions: {response.status_code} - {response.text}"
            )
        
        submissions = response.json()
        if submissions.get('value'):
            latest_submission = submissions['value'][0]
            state = latest_submission.get('state')
            substate = latest_submission.get('substate')
            
            if state == "InProgress" and substate != "Failed":
                return PublishResult(
                    success=False,
                    error=f"An AppSource submission is in progress (state: {state}, substate: {substate}). Please wait for it to complete or cancel it first."
                )
            elif not (state == "Published" and substate in ["ReadyToPublish", "InStore"]):
                return PublishResult(
                    success=False,
                    error=f"Cannot create new submission. Current submission state: {state}, substate: {substate}"
                )
        
        return PublishResult(success=True)

    def _get_package_branch(self, product_id: str) -> PublishResult:
        """Get the package branch information"""
        headers = self.auth.get_headers()
        api_url = f"{self.base_url}/products/{product_id}/branches/getByModule(module=Package)"
        
        response = requests.get(api_url, headers=headers)
        if response.status_code != 200:
            return PublishResult(
                success=False,
                error=f"Failed to get package branch: {response.status_code} - {response.text}"
            )
        
        branches = response.json()
        if not branches.get('value') or len(branches['value']) == 0:
            return PublishResult(
                success=False,
                error="No package branch found for this product"
            )
        
        # Use the first branch (typically there's only one for BC apps)
        package_branch = branches['value'][0]
        
        return PublishResult(
            success=True,
            response_data=package_branch
        )

    def _upload_app_packages(self, product_id: str, package_instance_id: str, app_file: str, library_app_file: Optional[str] = None) -> PublishResult:
        """Upload app packages to Azure storage"""
        headers = self.auth.get_headers()
        uploaded_packages = {}
        
        try:
            # Upload main app file
            if app_file:
                resolved_app_file = self.resolve_app_file(app_file)
                
                # Create package upload request
                body = {
                    "resourceType": "Dynamics365BusinessCentralAddOnExtensionPackage",
                    "fileName": os.path.basename(resolved_app_file)
                }
                
                response = requests.post(f"{self.base_url}/products/{product_id}/packages", 
                                       headers=headers, json=body)
                
                if response.status_code not in [200, 201, 202]:
                    return PublishResult(
                        success=False,
                        error=f"Failed to create package upload: {response.status_code} - {response.text}"
                    )
                
                package_upload = response.json()
                
                # Upload file to Azure storage using SAS URI
                upload_result = self._upload_file_to_storage(resolved_app_file, package_upload.get('fileSasUri'))
                if not upload_result:
                    return PublishResult(
                        success=False,
                        error="Failed to upload app file to storage"
                    )
                
                # Mark package as uploaded
                package_upload['state'] = 'Uploaded'
                response = requests.put(f"{self.base_url}/products/{product_id}/packages/{package_upload['id']}", 
                                      headers=headers, json=package_upload)
                
                if response.status_code not in [200, 201, 202]:
                    return PublishResult(
                        success=False,
                        error=f"Failed to mark package as uploaded: {response.status_code} - {response.text}"
                    )
                
                uploaded_packages['main'] = response.json()
            
            # Upload library app file if provided
            if library_app_file:
                resolved_library_file = self.resolve_app_file(library_app_file)
                
                body = {
                    "resourceType": "Dynamics365BusinessCentralAddOnLibraryExtensionPackage",
                    "fileName": os.path.basename(resolved_library_file)
                }
                
                response = requests.post(f"{self.base_url}/products/{product_id}/packages", 
                                       headers=headers, json=body)
                
                if response.status_code not in [200, 201, 202]:
                    return PublishResult(
                        success=False,
                        error=f"Failed to create library package upload: {response.status_code} - {response.text}"
                    )
                
                package_upload = response.json()
                
                upload_result = self._upload_file_to_storage(resolved_library_file, package_upload.get('fileSasUri'))
                if not upload_result:
                    return PublishResult(
                        success=False,
                        error="Failed to upload library file to storage"
                    )
                
                package_upload['state'] = 'Uploaded'
                response = requests.put(f"{self.base_url}/products/{product_id}/packages/{package_upload['id']}", 
                                      headers=headers, json=package_upload)
                
                if response.status_code not in [200, 201, 202]:
                    return PublishResult(
                        success=False,
                        error=f"Failed to mark library package as uploaded: {response.status_code} - {response.text}"
                    )
                
                uploaded_packages['library'] = response.json()
            
            return PublishResult(
                success=True,
                response_data=uploaded_packages
            )
            
        except Exception as e:
            return PublishResult(
                success=False,
                error=f"Error uploading packages: {str(e)}"
            )

    def _upload_file_to_storage(self, file_path: str, sas_uri: str) -> bool:
        """Upload file to Azure storage using SAS URI"""
        try:
            with open(file_path, 'rb') as file_data:
                # Use PUT request to upload to Azure Blob Storage
                response = requests.put(sas_uri, 
                                      data=file_data,
                                      headers={'x-ms-blob-type': 'BlockBlob'})
                return response.status_code in [200, 201]
        except Exception:
            return False

    def _update_package_configuration(self, product_id: str, package_instance_id: str, uploaded_packages: Dict[str, Any]) -> PublishResult:
        """Update package configuration with uploaded packages"""
        headers = self.auth.get_headers()
        
        # Get current package configuration
        api_url = f"{self.base_url}/products/{product_id}/packageConfigurations/getByInstanceID(instanceID={package_instance_id})"
        response = requests.get(api_url, headers=headers)
        
        if response.status_code != 200:
            return PublishResult(
                success=False,
                error=f"Failed to get package configuration: {response.status_code} - {response.text}"
            )
        
        configs = response.json()
        if not configs.get('value') or len(configs['value']) == 0:
            return PublishResult(
                success=False,
                error="No package configuration found"
            )
        
        package_config = configs['value'][0]
        
        # Update package references
        if 'main' in uploaded_packages:
            # Remove existing main package references
            package_config['packageReferences'] = [
                ref for ref in package_config.get('packageReferences', [])
                if ref.get('type') != 'Dynamics365BusinessCentralAddOnExtensionPackage'
            ]
            # Add new main package reference
            package_config['packageReferences'].append({
                'type': 'Dynamics365BusinessCentralAddOnExtensionPackage',
                'value': uploaded_packages['main']['id']
            })
        
        if 'library' in uploaded_packages:
            # Remove existing library package references
            package_config['packageReferences'] = [
                ref for ref in package_config.get('packageReferences', [])
                if ref.get('type') != 'Dynamics365BusinessCentralAddOnLibraryExtensionPackage'
            ]
            # Add new library package reference
            package_config['packageReferences'].append({
                'type': 'Dynamics365BusinessCentralAddOnLibraryExtensionPackage',
                'value': uploaded_packages['library']['id']
            })
        
        # Update the package configuration with proper ETag header
        update_headers = headers.copy()
        # The Microsoft API often requires an If-Match header with the ETag value
        if '@odata.etag' in package_config:
            update_headers['If-Match'] = package_config['@odata.etag']
        else:
            # Some APIs use a different format
            update_headers['If-Match'] = '*'
        
        response = requests.put(f"{self.base_url}/products/{product_id}/packageConfigurations/{package_config['id']}", 
                              headers=update_headers, json=package_config)
        
        if response.status_code not in [200, 201, 202]:
            return PublishResult(
                success=False,
                error=f"Failed to update package configuration: {response.status_code} - {response.text}"
            )
        
        return PublishResult(success=True)

    def _wait_for_submission(self, product_id: str, submission_id: str, auto_promote: bool = False) -> None:
        """Wait for submission to complete and optionally auto-promote"""
        # This would implement the workflow monitoring from the PowerShell code
        # For now, we'll just return as this is complex polling logic
        pass

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
