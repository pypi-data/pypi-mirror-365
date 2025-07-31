"""
Key Vault Client - Main client for interacting with the Key Vault API
"""

import requests
from typing import Dict, List, Optional, Union, Any
from urllib.parse import urljoin


class KeyVaultError(Exception):
    """Base exception for Key Vault SDK errors"""
    pass


class KeyVaultAuthError(KeyVaultError):
    """Authentication error"""
    pass


class KeyVaultNotFoundError(KeyVaultError):
    """Resource not found error"""
    pass


class KeyVault:
    """
    Key Vault SDK Client
    
    Provides a simple interface for accessing Key Vault API keys and values.
    This SDK is read-only: key creation, update, and deletion must be performed
    via the Key Vault web platform.
    """
    
    def __init__(self, api_url: str, token: str, timeout: int = 30):
        """
        Initialize the Key Vault client
        
        Args:
            api_url: Base URL of the Key Vault API (e.g., https://yourdomain.com/api)
            token: Your API token for authentication
            timeout: Request timeout in seconds (default: 30)
        """
        self.api_url = api_url.rstrip('/')
        self.token = token
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
            'User-Agent': f'KeyVault-Python-SDK/1.0.0'
        })
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """
        Make an HTTP request to the Key Vault API
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            **kwargs: Additional arguments for requests
            
        Returns:
            API response as dictionary
            
        Raises:
            KeyVaultError: For API errors
            KeyVaultAuthError: For authentication errors
            KeyVaultNotFoundError: For not found errors
        """
        # Fix URL construction to preserve the /api path
        if endpoint.startswith('/'):
            url = self.api_url + endpoint
        else:
            url = self.api_url + '/' + endpoint
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                timeout=self.timeout,
                **kwargs
            )
            
            # Handle different response status codes
            if response.status_code == 401:
                raise KeyVaultAuthError("Invalid API token or token expired")
            elif response.status_code == 404:
                raise KeyVaultNotFoundError("Resource not found")
            elif response.status_code >= 400:
                try:
                    error_data = response.json()
                    error_msg = error_data.get('error', f'HTTP {response.status_code}')
                except:
                    error_msg = f'HTTP {response.status_code}: {response.text}'
                raise KeyVaultError(error_msg)
            
            # Parse JSON response
            try:
                return response.json()
            except ValueError:
                raise KeyVaultError(f"Invalid JSON response: {response.text}")
                
        except requests.exceptions.Timeout:
            raise KeyVaultError("Request timeout")
        except requests.exceptions.ConnectionError:
            raise KeyVaultError("Connection error")
        except requests.exceptions.RequestException as e:
            raise KeyVaultError(f"Request failed: {str(e)}")
    
    def list_keys(self, folder_id: str, limit: int = 20, offset: int = 0) -> Dict[str, Any]:
        """
        List keys in a folder
        
        Args:
            folder_id: Folder ID to list keys from
            limit: Number of keys to return (default: 20, max: 100)
            offset: Number of keys to skip (default: 0)
            
        Returns:
            Dictionary containing keys list and pagination info
            
        Example:
            >>> kv = KeyVault(api_url="https://yourdomain.com/api", token="your-token")
            >>> result = kv.list_keys(folder_id="folder-123", limit=50)
            >>> print(f"Found {len(result['keys'])} keys")
        """
        params = {
            'folderId': folder_id,
            'limit': min(limit, 100),  # Cap at 100
            'offset': offset
        }
        
        response = self._make_request('GET', '/keys', params=params)
        
        if not response.get('success', True):
            raise KeyVaultError(response.get('error', 'Failed to list keys'))
        
        return {
            'keys': response.get('keys', []),
            'total': response.get('total', 0),
            'limit': response.get('limit', limit),
            'offset': response.get('offset', offset)
        }
    
    def get_key(self, key_id: str, include_value: bool = False) -> Dict[str, Any]:
        """
        Get a key by ID
        
        Args:
            key_id: The key's ID
            include_value: If True, include the decrypted key value
            
        Returns:
            Key object with metadata and optionally the value
            
        Example:
            >>> kv = KeyVault(api_url="https://yourdomain.com/api", token="your-token")
            >>> key = kv.get_key(key_id="key-123", include_value=True)
            >>> print(f"Key: {key['name']}, Value: {key['value']}")
        """
        params = {'includeValue': str(include_value).lower()}
        
        response = self._make_request('GET', f'/keys/{key_id}', params=params)
        
        if not response.get('success', True):
            raise KeyVaultError(response.get('error', 'Failed to fetch key'))
        
        return response.get('key', {})
    
    def get_key_by_name(self, folder_id: str, key_name: str) -> str:
        """
        Get a key's value by name (convenience method)
        
        Args:
            folder_id: Folder containing the key
            key_name: Name of the key to retrieve
            
        Returns:
            The decrypted key value as string
            
        Example:
            >>> kv = KeyVault(api_url="https://yourdomain.com/api", token="your-token")
            >>> api_key = kv.get_key_by_name(folder_id="folder-123", key_name="stripe-secret-key")
            >>> print(f"API Key: {api_key}")
        """
        # First, list keys to find the one we want
        result = self.list_keys(folder_id=folder_id, limit=100)
        
        # Find the key by name
        key = next((k for k in result['keys'] if k['name'] == key_name), None)
        
        if not key:
            raise KeyVaultNotFoundError(f"Key '{key_name}' not found in folder")
        
        # Get the key with value
        key_with_value = self.get_key(key_id=key['id'], include_value=True)
        
        return key_with_value.get('value', '')
    
    def get_multiple_keys(self, folder_id: str, key_names: List[str]) -> Dict[str, str]:
        """
        Get multiple keys by name
        
        Args:
            folder_id: Folder containing the keys
            key_names: List of key names to retrieve
            
        Returns:
            Dictionary mapping key names to their values
            
        Example:
            >>> kv = KeyVault(api_url="https://yourdomain.com/api", token="your-token")
            >>> keys = kv.get_multiple_keys(
            ...     folder_id="folder-123", 
            ...     key_names=["stripe-key", "database-password", "api-secret"]
            ... )
            >>> print(f"Retrieved {len(keys)} keys")
        """
        # Get all keys from the folder
        result = self.list_keys(folder_id=folder_id, limit=100)
        folder_keys = {k['name']: k for k in result['keys']}
        
        # Get values for requested keys
        keys_dict = {}
        for key_name in key_names:
            if key_name in folder_keys:
                key_with_value = self.get_key(
                    key_id=folder_keys[key_name]['id'], 
                    include_value=True
                )
                keys_dict[key_name] = key_with_value.get('value', '')
            else:
                keys_dict[key_name] = None  # Key not found
        
        return keys_dict
    
    def list_folders(self) -> List[Dict[str, Any]]:
        """
        List all folders
        
        Returns:
            List of folder objects
            
        Example:
            >>> kv = KeyVault(api_url="https://yourdomain.com/api", token="your-token")
            >>> folders = kv.list_folders()
            >>> for folder in folders:
            ...     print(f"Folder: {folder['name']} (ID: {folder['id']})")
        """
        response = self._make_request('GET', '/folders')
        
        # The /folders endpoint returns { "folders": [...] } without a success field
        return response.get('folders', [])
    
    def test_connection(self) -> bool:
        """
        Test the connection to the Key Vault API
        
        Returns:
            True if connection is successful
            
        Example:
            >>> kv = KeyVault(api_url="https://yourdomain.com/api", token="your-token")
            >>> if kv.test_connection():
            ...     print("Connection successful!")
            ... else:
            ...     print("Connection failed!")
        """
        try:
            # Try to list folders as a connection test
            self.list_folders()
            return True
        except Exception:
            return False 