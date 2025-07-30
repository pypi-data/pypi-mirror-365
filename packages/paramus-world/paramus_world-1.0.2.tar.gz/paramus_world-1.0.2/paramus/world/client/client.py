"""
Paramus World Client API

This module provides the main client for interacting with the Paramus World API.
It supports all available API methods:
- chat.submit - Submit chat messages
- sparql.query - Execute SPARQL queries  
- sparql.update - Execute SPARQL updates
- system.health - Check system health
"""

import json
import requests
from typing import Dict, Any, Optional


class ParamusWorldClient:
    """Client for interacting with the Paramus World API."""
    
    def __init__(self, base_url: str = "http://127.0.0.1:8051", token: str = None):
        """
        Initialize the Paramus World Client.
        
        Args:
            base_url: Base URL for the API (default: http://127.0.0.1:8051)
            token: Authentication token
        """
        self.base_url = base_url.rstrip('/')
        self.jsonrpc_url = f"{self.base_url}/api/jsonrpc"
        self.auth_url = f"{self.base_url}/api/auth/token"
        self.token = token
        self.session = requests.Session()
        
        # Set default headers
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        
        # If token is provided, set authorization header
        if self.token:
            self.session.headers.update({
                'Authorization': f'Bearer {self.token}'
            })
    
    def _make_jsonrpc_request(self, method: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Make a JSON-RPC request to the API.
        
        Args:
            method: The RPC method name
            params: Parameters for the method
            
        Returns:
            The response from the API
            
        Raises:
            requests.RequestException: If the request fails
            ValueError: If the response contains an error
        """
        # Prepare JSON-RPC payload
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or {},
            "id": 1
        }
        
        try:
            response = self.session.post(self.jsonrpc_url, json=payload)
            response.raise_for_status()
            
            result = response.json()
            
            # Check for JSON-RPC errors
            if "error" in result:
                raise ValueError(f"API Error: {result['error']}")
            
            return result.get("result", {})
            
        except requests.RequestException as e:
            raise requests.RequestException(f"Request failed: {e}")
    
    def authenticate(self, username: str = None, password: str = None) -> str:
        """
        Authenticate with the API and get a token.
        
        Args:
            username: Username for authentication
            password: Password for authentication
            
        Returns:
            Authentication token
        """
        auth_data = {}
        if username and password:
            auth_data = {"username": username, "password": password}
        
        try:
            response = self.session.post(self.auth_url, json=auth_data)
            response.raise_for_status()
            
            result = response.json()
            token = result.get("token")
            
            if token:
                self.token = token
                self.session.headers.update({
                    'Authorization': f'Bearer {token}'
                })
            
            return token
            
        except requests.RequestException as e:
            raise requests.RequestException(f"Authentication failed: {e}")
    
    def submit_chat(self, message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Submit a chat message to the system.
        
        Args:
            message: The chat message to submit
            context: Additional context for the chat message
            
        Returns:
            Chat response from the system
        """
        params = {
            "message": message
        }
        if context:
            params["context"] = context
        
        return self._make_jsonrpc_request("chat.submit", params)
    
    def sparql_query(self, query: str, format: str = "json") -> Dict[str, Any]:
        """
        Execute a SPARQL query.
        
        Args:
            query: The SPARQL query string
            format: Response format (default: json)
            
        Returns:
            Query results
        """
        params = {
            "query": query,
            "format": format
        }
        
        return self._make_jsonrpc_request("sparql.query", params)
    
    def sparql_update(self, update: str) -> Dict[str, Any]:
        """
        Execute a SPARQL update operation.
        
        Args:
            update: The SPARQL update string
            
        Returns:
            Update operation result
        """
        params = {
            "update_query": update
        }
        
        return self._make_jsonrpc_request("sparql.update", params)
    
    def check_system_health(self) -> Dict[str, Any]:
        """
        Check the system health status.
        
        Returns:
            System health information
        """
        return self._make_jsonrpc_request("system.health")
