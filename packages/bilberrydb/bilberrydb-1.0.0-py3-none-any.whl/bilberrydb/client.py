# bilberrydb/client.py
"""
BilberryDB Client - Main client class for API interactions
"""

import os
import json
import mimetypes
from typing import List, Union, Dict, Any, Optional
from urllib.request import urlopen, Request
from urllib.parse import urlencode, quote
from urllib.error import HTTPError, URLError

from .exceptions import (
    BilberryError,
    AuthenticationError,
    APIError,
    ValidationError,
    NetworkError
)
from .vector import VectorCollection


class BilberryClient:
    """
    Main client class for BilberryDB operations.

    This client handles authentication and provides methods to create
    vector collections for image search operations.
    """

    def __init__(self, api_key: str, api_id: str = None, base_url: str = "https://appbilberry.com"):
        """
        Initialize BilberryDB client.

        Args:
            api_key (str): Your BilberryDB API key
            api_id (str, optional): Your API ID (should be user email)
            base_url (str): Base URL for BilberryDB API
        """
        if not api_key or not isinstance(api_key, str):
            raise ValidationError("API key must be a non-empty string")

        self.api_key = api_key.strip()
        self.api_id = api_id.strip() if api_id else None
        self.base_url = base_url.rstrip('/')
        self.user_email = self._extract_email_from_key()

    def _extract_email_from_key(self) -> str:
        """
        Extract user email from API key or use api_id.
        In a real implementation, this would decode the API key.
        """
        # Use api_id as user_email if provided (api_id should be the email)
        if self.api_id and '@' in self.api_id:
            return self.api_id

        # Simple extraction - in real implementation, decode JWT or use proper method
        # This is a placeholder implementation
        return f"user_{self.api_key[:8]}@bilberrydb.com"

    def _make_request(self, endpoint: str, method: str = "GET", data: bytes = None,
                      headers: Dict[str, str] = None, include_api_key_param: bool = True) -> Dict[str, Any]:
        """
        Make HTTP request to BilberryDB API.

        Args:
            endpoint (str): API endpoint
            method (str): HTTP method
            data (bytes): Request body data
            headers (dict): Additional headers
            include_api_key_param (bool): Whether to include api_key as URL parameter

        Returns:
            dict: JSON response

        Raises:
            AuthenticationError: Invalid credentials
            APIError: API error response
            NetworkError: Network connection issues
        """
        # Add api_key parameter to URL if needed
        if include_api_key_param:
            separator = "&" if "?" in endpoint else "?"
            endpoint = f"{endpoint}{separator}api_key={self.api_key}"

        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        # Default headers (remove Authorization header since we're using URL params)
        request_headers = {
            'User-Agent': f'BilberryDB-Python-SDK/{__import__("bilberrydb").__version__}',
        }

        if headers:
            request_headers.update(headers)

        try:
            request = Request(url, data=data, headers=request_headers, method=method)

            with urlopen(request, timeout=30) as response:
                response_data = response.read().decode('utf-8')

                if response.status == 200:
                    try:
                        return json.loads(response_data) if response_data else {}
                    except json.JSONDecodeError:
                        return {"success": True, "data": response_data}
                else:
                    raise APIError(f"API request failed with status {response.status}")


        except HTTPError as e:
            # Read the error response body to get the actual error message
            error_message = "Unknown error"
            try:
                error_body = e.read().decode('utf-8')
                error_json = json.loads(error_body)
                error_message = error_json.get('detail', error_message)

            except:
                error_message = e.reason
            # Handle specific error cases based on status code and message

            if e.code == 401:
                if "Invalid API key" in error_message or "Invalid API key or user email" in error_message:
                    raise AuthenticationError("Invalid API key - please check your API key and user email")

                else:
                    raise AuthenticationError(f"Authentication failed: {error_message}")

            elif e.code == 403:

                if "API key expired" in error_message:
                    raise AuthenticationError("API key has expired")

                elif "usage limit exceeded" in error_message:
                    raise AuthenticationError("API key usage limit exceeded")

                else:
                    raise AuthenticationError(f"Access forbidden: {error_message}")

            elif e.code == 404:
                raise APIError(f"Endpoint not found: {error_message}")

            elif e.code == 500:
                # Parse 500 errors to provide more specific messages
                if "Invalid API key" in error_message or "API key validation error" in error_message:
                    raise AuthenticationError("Invalid API key - please verify your credentials")

                elif "usage limit exceeded" in error_message:
                    raise AuthenticationError("API key usage limit exceeded")

                else:
                    raise APIError(f"Server error: {error_message}")

            else:
                raise APIError(f"HTTP error {e.code}: {error_message}")

        except URLError as e:
            raise NetworkError(f"Network error: {e.reason}")

        except Exception as e:
            raise BilberryError(f"Unexpected error: {str(e)}")

    def get_vec(self, user_email: str = None) -> VectorCollection:
        """
        Create a vector collection for search operations.

        Note: This SDK only supports searching existing images in your BilberryDB.
        Images must be uploaded through the web interface or other means.

        Args:
            user_email (str, optional): User email for the collection.
                                      If not provided, uses the client's user_email.

        Returns:
            VectorCollection: Collection object for search operations

        Example:
            >>> vec = client.get_vec()
            >>> results = vec.search_by_image("./query.jpg")
            >>> text_results = vec.search_by_text("damaged car")
        """
        collection_user_email = user_email or self.user_email

        if not collection_user_email:
            raise ValidationError("User email is required for vector collection")

        # Ensure user_email is a string and properly formatted
        if not isinstance(collection_user_email, str):
            raise ValidationError("User email must be a string")

        # Basic email validation
        if '@' not in collection_user_email or ' ' in collection_user_email:
            raise ValidationError("User email must be a valid email address")

        return VectorCollection(client=self, user_email=collection_user_email)

    def search_by_image(self, image_path: str, top_k: int = 5, user_email: str = None) -> List[Dict[str, Any]]:
        """
        Direct image search without creating a vector collection.

        Args:
            image_path (str): Path to query image file
            top_k (int): Number of top results to return
            user_email (str, optional): User email for search

        Returns:
            List[Dict]: List of similar images with similarity scores

        Example:
            >>> results = client.search_by_image("./query.jpg", top_k=10)
        """
        vec = self.get_vec(user_email)
        return vec.search_by_image(image_path, top_k)

    def search_by_text(self, text_query: str, top_k: int = 5, user_email: str = None) -> List[Dict[str, Any]]:
        """
        Direct text search without creating a vector collection.

        Args:
            text_query (str): Text search query
            top_k (int): Number of top results to return
            user_email (str, optional): User email for search

        Returns:
            List[Dict]: List of similar images with similarity scores

        Example:
            >>> results = client.search_by_text("damaged car", top_k=10)
        """
        vec = self.get_vec(user_email)
        return vec.search_by_text(text_query, top_k)

    def get_existing_items(self, limit: int = 100, user_email: str = None) -> List[Dict[str, Any]]:
        """Fetch existing items from BilberryDB."""
        search_user_email = user_email or self.user_email

        # Validate and URL encode the user email
        if not isinstance(search_user_email, str) or '@' not in search_user_email:
            raise ValidationError("Valid user email is required")

        encoded_email = quote(search_user_email)

        try:
            # FIX: Your backend expects '/itemz' which matches the SDK
            response = self._make_request(f"itemz?user_email={encoded_email}&limit={limit}")

            if isinstance(response, list):
                return response
            elif isinstance(response, dict) and 'data' in response:
                return response['data'] if isinstance(response['data'], list) else []
            else:
                return []

        except Exception as e:
            raise APIError(f"Failed to fetch existing items: {str(e)}")

    def test_connection(self) -> bool:
        """
        Test connection to BilberryDB API.

        Returns:
            bool: True if connection successful

        Raises:
            AuthenticationError: Invalid credentials
            NetworkError: Connection issues
        """
        try:
            # Test with a simple endpoint
            encoded_email = quote(self.user_email)
            self._make_request(f"itemz?user_email={encoded_email}&limit=1")
            return True
        except Exception:
            return False