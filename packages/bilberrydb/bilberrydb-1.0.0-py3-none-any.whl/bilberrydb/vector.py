# bilberrydb/vector.py
"""
Vector Collection - Handles image search operations for existing images
"""

import os
import json
import mimetypes
from typing import List, Dict, Any, Union, Tuple
from urllib.request import Request, urlopen
from urllib.parse import urlencode, quote

from .exceptions import ValidationError, APIError, NetworkError


class VectorCollection:
    """
    Vector collection for image similarity search operations.

    This class handles similarity search functionality for existing images
    in your BilberryDB collection. Images must be uploaded through the
    web interface or other means before using this SDK.
    """

    def __init__(self, client, user_email: str):
        """
        Initialize vector collection.

        Args:
            client: BilberryClient instance
            user_email: User email for the collection
        """
        self.client = client
        # Ensure user_email is properly set as a string
        if not isinstance(user_email, str):
            raise ValidationError("User email must be a string")
        self.user_email = user_email
        self._existing_items = None

    def _get_existing_items(self, force_refresh: bool = False) -> List[Dict[str, Any]]:
        """
        Get existing items from BilberryDB, with caching.

        Args:
            force_refresh (bool): Force refresh of cached items

        Returns:
            List[Dict]: List of existing items
        """
        if self._existing_items is None or force_refresh:
            try:
                self._existing_items = self.client.get_existing_items(user_email=self.user_email)
            except Exception as e:
                print(f"Warning: Could not fetch existing items: {str(e)}")
                self._existing_items = []

        return self._existing_items

    def search_by_text(self, text_query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for similar images using text query.

        Args:
            text_query (str): Text search query
            top_k (int): Number of top results to return (default: 5)

        Returns:
            List[Dict]: List of similar images with similarity scores

        Example:
            >>> results = vec.search_by_text("damaged car", top_k=10)
            >>> for result in results:
            ...     print(f"Image: {result['filename']}, Score: {result['similarity_score']}")
        """
        if not text_query or not isinstance(text_query, str):
            raise ValidationError("Text query must be a non-empty string")

        if not isinstance(top_k, int) or top_k < 1:
            raise ValidationError("top_k must be a positive integer")

        try:
            # Prepare the request data
            request_data = {
                'text': text_query,
                'top_k': top_k
            }

            body = json.dumps(request_data).encode('utf-8')
            headers = {
                'Content-Type': 'application/json',
            }

            # URL encode the user email to prevent URL errors
            encoded_email = quote(self.user_email)
            endpoint = f"search/text?user_email={encoded_email}"
            response = self.client._make_request(endpoint, method="POST", data=body, headers=headers)

            # Process and format results
            return self._format_search_results(response)

        except Exception as e:
            raise APIError(f"Text search failed: {str(e)}")

    def search_by_image(self, query_input: Union[str, bytes], top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for similar images using image file or image bytes.

        Args:
            query_input: Path to query image file or image bytes
            top_k: Number of top results to return (default: 5)

        Returns:
            List[Dict]: List of similar images with similarity scores

        Example:
            >>> results = vec.search_by_image("./query_image.jpg", top_k=10)
            >>> for result in results:
            ...     print(f"Image: {result['filename']}, Score: {result['similarity_score']}")
        """
        if not query_input:
            raise ValidationError("Query input cannot be empty")

        if not isinstance(top_k, int) or top_k < 1:
            raise ValidationError("top_k must be a positive integer")

        # Handle different input types
        if isinstance(query_input, str):
            # File path
            if not os.path.exists(query_input):
                raise ValidationError(f"Query image file not found: {query_input}")
            return self._search_by_image_file(query_input, top_k)
        elif isinstance(query_input, bytes):
            # Image bytes
            return self._search_by_image_bytes(query_input, top_k)
        else:
            raise ValidationError("Query input must be file path (string) or image bytes")

    def search(self, query_input: Union[str, bytes], top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Universal search method that automatically detects query type.

        Args:
            query_input: Text query, path to query image file, or image bytes
            top_k: Number of top results to return (default: 5)

        Returns:
            List[Dict]: List of similar images with similarity scores

        Example:
            >>> # Text search
            >>> results = vec.search("damaged car", top_k=10)
            >>> # Image search
            >>> results = vec.search("./query_image.jpg", top_k=10)
        """
        if not query_input:
            raise ValidationError("Query input cannot be empty")

        if isinstance(query_input, str):
            # Check if it's a file path or text query
            if os.path.exists(query_input):
                # File path - perform image search
                return self.search_by_image(query_input, top_k)
            else:
                # Text query
                return self.search_by_text(query_input, top_k)
        elif isinstance(query_input, bytes):
            # Image bytes
            return self.search_by_image(query_input, top_k)
        else:
            raise ValidationError("Query input must be text string, file path, or image bytes")

    def _search_by_image_file(self, image_path: str, top_k: int) -> List[Dict[str, Any]]:
        """
        Search using image file path.

        Args:
            image_path (str): Path to query image
            top_k (int): Number of results

        Returns:
            List[Dict]: Search results
        """
        filename = os.path.basename(image_path)

        # Validate image file type
        mime_type, _ = mimetypes.guess_type(image_path)
        if not mime_type or not mime_type.startswith('image/'):
            raise ValidationError(f"File is not a valid image: {image_path}")

        # Read image file
        with open(image_path, 'rb') as f:
            image_data = f.read()

        return self._perform_image_search(image_data, filename, top_k)

    def _search_by_image_bytes(self, image_bytes: bytes, top_k: int) -> List[Dict[str, Any]]:
        """
        Search using image bytes.

        Args:
            image_bytes (bytes): Image data
            top_k (int): Number of results

        Returns:
            List[Dict]: Search results
        """
        return self._perform_image_search(image_bytes, "query_image.jpg", top_k)

    def _perform_image_search(self, image_data: bytes, filename: str, top_k: int) -> List[Dict[str, Any]]:
        """Perform the actual image search API call using FormData approach."""
        # Create multipart form data similar to JavaScript FormData
        import uuid
        boundary = f'----formdata-{uuid.uuid4().hex}'

        # Build multipart data exactly like JavaScript FormData.append('file', file)
        multipart_parts = []
        multipart_parts.append(f'--{boundary}')
        multipart_parts.append(f'Content-Disposition: form-data; name="file"; filename="{filename}"')
        multipart_parts.append(f'Content-Type: {self._get_content_type_from_filename(filename)}')
        multipart_parts.append('')  # Empty line before file data

        # Convert header to bytes
        header_data = '\r\n'.join(multipart_parts).encode('utf-8')

        # Create the final body: header + file data + boundary end
        footer_data = f'\r\n--{boundary}--\r\n'.encode('utf-8')
        body = header_data + b'\r\n' + image_data + footer_data

        headers = {
            'Content-Type': f'multipart/form-data; boundary={boundary}',
        }

        try:
            # URL encode the user email and include api_key
            encoded_email = quote(self.user_email)
            # FIX: Change from 'search/imagez' to 'search/imagez' (your backend expects this)
            # Based on your backend code, it expects '/search/imagez'
            endpoint = f"search/imagez?user_email={encoded_email}&top_k={top_k}"
            response = self.client._make_request(endpoint, method="POST", data=body, headers=headers)

            # Process and format results
            return self._format_search_results(response)

        except Exception as e:
            raise APIError(f"Image search failed: {str(e)}")

    def _get_content_type_from_filename(self, filename: str) -> str:
        """Get content type from filename."""
        content_type, _ = mimetypes.guess_type(filename)
        return content_type or 'image/jpeg'

    def _format_search_results(self, api_response: Any) -> List[Dict[str, Any]]:
        """
        Format API response into standardized result format.

        Args:
            api_response: Raw API response

        Returns:
            List[Dict]: Formatted results
        """
        results = []

        try:
            # Handle different response formats
            if isinstance(api_response, list):
                data = api_response
            elif isinstance(api_response, dict) and 'results' in api_response:
                data = api_response['results']
            elif isinstance(api_response, dict) and 'data' in api_response:
                data = api_response['data']
            else:
                data = [api_response] if api_response else []

            for item in data:
                if not isinstance(item, dict):
                    continue

                # Extract relevant information matching the JavaScript structure
                result = {
                    'id': item.get('id', ''),
                    'filename': item.get('file_name', item.get('filename', 'unknown')),
                    'similarity_score': self._extract_similarity_score(item),
                    'file_type': item.get('file_type', item.get('content_type', 'image')),
                    'file_size': item.get('file_size', 0),
                    'content_type': item.get('content_type', 'image'),
                    'download_url': self._get_download_url(item.get('id', '')),
                    'metadata': {
                        'content_type': item.get('content_type', 'image'),
                        'upload_date': item.get('created_at', item.get('uploaded_at', '')),
                        'file_size': item.get('file_size', 0),
                    }
                }

                results.append(result)

            # Sort by similarity score (highest first) - matching JavaScript behavior
            results.sort(key=lambda x: x['similarity_score'], reverse=True)

            return results

        except Exception as e:
            raise APIError(f"Failed to format search results: {str(e)}")

    def _extract_similarity_score(self, item: Dict[str, Any]) -> float:
        """
        Extract similarity score from various possible fields.

        Args:
            item (dict): Item from API response

        Returns:
            float: Similarity score
        """
        # Try different possible field names for similarity score
        score_fields = ['similarity_score', 'similarity', 'score', 'confidence']

        for field in score_fields:
            if field in item:
                try:
                    return float(item[field])
                except (ValueError, TypeError):
                    continue

        return 0.0

    def _get_download_url(self, item_id: str) -> str:
        """Generate download URL for an item."""
        if not item_id:
            return ""
        # URL encode the user email and include api_key in download URLs
        encoded_email = quote(self.user_email)
        # FIX: Your backend expects '/itemz/{item_id}/download' which matches the SDK
        return f"{self.client.base_url}/itemz/{item_id}/download?user_email={encoded_email}&api_key={self.client.api_key}"

    def get_collection_info(self) -> Dict[str, Any]:
        """
        Get information about the vector collection.

        Returns:
            Dict: Collection information
        """
        existing_items = self._get_existing_items()
        image_items = [item for item in existing_items if item.get('content_type', '').startswith('image')]

        return {
            'user_email': self.user_email,
            'total_items': len(existing_items),
            'image_items': len(image_items),
            'collection_id': f"collection_{abs(hash(self.user_email)) % 100000}",
            'available_for_search': len(image_items) > 0,
            'sample_filenames': [item.get('file_name', 'unknown') for item in image_items[:5]]
        }

    def list_available_images(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        List available images in the collection.

        Args:
            limit (int): Maximum number of images to return

        Returns:
            List[Dict]: List of available images
        """
        existing_items = self._get_existing_items()
        image_items = [item for item in existing_items if item.get('content_type', '').startswith('image')]

        return image_items[:limit]