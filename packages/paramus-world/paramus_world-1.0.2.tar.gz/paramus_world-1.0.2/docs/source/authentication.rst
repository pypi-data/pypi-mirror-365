Authentication
==============

The Paramus World Client uses JWT (JSON Web Token) authentication to secure API access. This guide explains how to obtain and use authentication tokens.

Overview
--------

The Paramus World API uses Bearer token authentication with JWT tokens. Each request must include a valid token in the Authorization header.

Authentication Flow
-------------------

1. **Obtain Token**: Get a JWT token from the authentication endpoint
2. **Initialize Client**: Create a client instance with the token
3. **Make Requests**: Use the client to make authenticated API calls
4. **Token Refresh**: Renew tokens when they expire

Getting a Token
---------------

Method 1: Using the Client
~~~~~~~~~~~~~~~~~~~~~~~~~~

The client can authenticate and obtain a token automatically:

.. code-block:: python

   from paramus_world import ParamusWorldClient

   # Create client without token
   client = ParamusWorldClient(base_url="http://127.0.0.1:8051")

   # Authenticate and get token
   token = client.authenticate("username", "password")
   print(f"Token: {token}")

   # The client now has the token and can make authenticated requests
   health = client.check_system_health()

Method 2: Direct API Call
~~~~~~~~~~~~~~~~~~~~~~~~~

You can also get a token directly using HTTP requests:

.. code-block:: python

   import requests

   auth_url = "http://127.0.0.1:8051/api/auth/token"
   auth_data = {
       "username": "your_username",
       "password": "your_password"
   }

   response = requests.post(auth_url, json=auth_data)
   token = response.json()["token"]

   # Use the token with the client
   from paramus_world import ParamusWorldClient
   client = ParamusWorldClient(token=token)

Method 3: Environment Variables
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For production use, store tokens in environment variables:

.. code-block:: python

   import os
   from paramus_world import ParamusWorldClient

   # Get token from environment
   token = os.getenv("PARAMUS_TOKEN")
   
   if not token:
       raise ValueError("PARAMUS_TOKEN environment variable not set")

   client = ParamusWorldClient(token=token)

Token Management
----------------

Token Validation
~~~~~~~~~~~~~~~~~

Check if a token is valid:

.. code-block:: python

   from paramus_world import ParamusWorldClient

   def is_token_valid(token):
       try:
           client = ParamusWorldClient(token=token)
           client.check_system_health()
           return True
       except Exception:
           return False

   # Usage
   if is_token_valid("your-token"):
       print("Token is valid")
   else:
       print("Token is invalid or expired")

Token Expiration
~~~~~~~~~~~~~~~~

JWT tokens have an expiration time. Handle expired tokens gracefully:

.. code-block:: python

   from paramus_world import ParamusWorldClient
   import requests

   class AuthenticatedClient:
       def __init__(self, base_url, username, password):
           self.base_url = base_url
           self.username = username
           self.password = password
           self.client = None
           self._authenticate()

       def _authenticate(self):
           """Get a new token and create client"""
           temp_client = ParamusWorldClient(base_url=self.base_url)
           token = temp_client.authenticate(self.username, self.password)
           self.client = ParamusWorldClient(base_url=self.base_url, token=token)

       def _make_request(self, method, *args, **kwargs):
           """Make request with automatic token refresh"""
           try:
               return getattr(self.client, method)(*args, **kwargs)
           except requests.exceptions.HTTPError as e:
               if e.response.status_code == 401:  # Unauthorized
                   print("Token expired, refreshing...")
                   self._authenticate()
                   return getattr(self.client, method)(*args, **kwargs)
               raise

       def check_system_health(self):
           return self._make_request('check_system_health')

       def submit_chat(self, message, context=None):
           return self._make_request('submit_chat', message, context)

       def sparql_query(self, query, format="json"):
           return self._make_request('sparql_query', query, format)

       def sparql_update(self, update):
           return self._make_request('sparql_update', update)

   # Usage
   auth_client = AuthenticatedClient(
       base_url="http://127.0.0.1:8051",
       username="your_username",
       password="your_password"
   )

   # Automatically handles token refresh
   health = auth_client.check_system_health()

Token Storage
~~~~~~~~~~~~~

Secure token storage for different environments:

.. code-block:: python

   import os
   import keyring
   from paramus_world import ParamusWorldClient

   class SecureTokenManager:
       def __init__(self, service_name="paramus-world"):
           self.service_name = service_name

       def save_token(self, username, token):
           """Save token securely using keyring"""
           keyring.set_password(self.service_name, username, token)

       def get_token(self, username):
           """Retrieve token from secure storage"""
           return keyring.get_password(self.service_name, username)

       def get_client(self, username):
           """Get authenticated client"""
           token = self.get_token(username)
           if not token:
               raise ValueError(f"No token found for user {username}")
           return ParamusWorldClient(token=token)

   # Usage
   manager = SecureTokenManager()
   
   # Save token (do this once)
   manager.save_token("your_username", "your-jwt-token")
   
   # Get client (use this in your applications)
   client = manager.get_client("your_username")

Security Best Practices
------------------------

Token Security
~~~~~~~~~~~~~~

1. **Never commit tokens to version control**
2. **Use environment variables or secure storage**
3. **Rotate tokens regularly**
4. **Use HTTPS in production**

.. code-block:: python

   # ❌ DON'T DO THIS
   client = ParamusWorldClient(token="hardcoded-token-123")

   # ✅ DO THIS
   import os
   token = os.getenv("PARAMUS_TOKEN")
   client = ParamusWorldClient(token=token)

Environment Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~

Set up different configurations for different environments:

.. code-block:: bash

   # Development (.env.dev)
   PARAMUS_BASE_URL=http://localhost:8051
   PARAMUS_TOKEN=dev-token-here

   # Production (.env.prod)
   PARAMUS_BASE_URL=https://api.paramus.ai:8051
   PARAMUS_TOKEN=prod-token-here

.. code-block:: python

   import os
   from dotenv import load_dotenv
   from paramus_world import ParamusWorldClient

   # Load environment-specific configuration
   env = os.getenv("ENVIRONMENT", "dev")
   load_dotenv(f".env.{env}")

   client = ParamusWorldClient(
       base_url=os.getenv("PARAMUS_BASE_URL"),
       token=os.getenv("PARAMUS_TOKEN")
   )

Token Monitoring
~~~~~~~~~~~~~~~~

Monitor token usage and expiration:

.. code-block:: python

   import jwt
   import datetime
   from paramus_world import ParamusWorldClient

   def decode_token(token):
       """Decode JWT token to check expiration"""
       try:
           # Note: This doesn't verify signature
           decoded = jwt.decode(token, options={"verify_signature": False})
           return decoded
       except jwt.InvalidTokenError:
           return None

   def check_token_expiration(token):
       """Check if token will expire soon"""
       decoded = decode_token(token)
       if not decoded or 'exp' not in decoded:
           return False
       
       exp_time = datetime.datetime.fromtimestamp(decoded['exp'])
       now = datetime.datetime.now()
       time_left = exp_time - now
       
       return time_left.total_seconds() < 3600  # Expires within 1 hour

   # Usage
   token = "your-jwt-token"
   if check_token_expiration(token):
       print("⚠️  Token expires soon, consider refreshing")

   client = ParamusWorldClient(token=token)

Production Configuration
------------------------

Docker Environment
~~~~~~~~~~~~~~~~~~

Configure authentication in Docker containers:

.. code-block:: dockerfile

   # Dockerfile
   FROM python:3.9
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   COPY . .
   CMD ["python", "app.py"]

.. code-block:: yaml

   # docker-compose.yml
   version: '3.8'
   services:
     paramus-client:
       build: .
       environment:
         - PARAMUS_BASE_URL=http://paramus-server:8051
         - PARAMUS_TOKEN=${PARAMUS_TOKEN}
       depends_on:
         - paramus-server

Kubernetes Secrets
~~~~~~~~~~~~~~~~~~~

Store tokens as Kubernetes secrets:

.. code-block:: yaml

   # secret.yaml
   apiVersion: v1
   kind: Secret
   metadata:
     name: paramus-token
   type: Opaque
   data:
     token: <base64-encoded-token>

.. code-block:: yaml

   # deployment.yaml
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: paramus-client
   spec:
     template:
       spec:
         containers:
         - name: client
           image: paramus-client:latest
           env:
           - name: PARAMUS_TOKEN
             valueFrom:
               secretKeyRef:
                 name: paramus-token
                 key: token

Troubleshooting
---------------

Common Authentication Issues
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**401 Unauthorized Error**

.. code-block:: python

   try:
       health = client.check_system_health()
   except requests.HTTPError as e:
       if e.response.status_code == 401:
           print("Authentication failed:")
           print("- Check if token is valid")
           print("- Check if token has expired")
           print("- Verify token format")

**Token Format Issues**

.. code-block:: python

   def validate_token_format(token):
       """Basic token format validation"""
       if not token:
           return False, "Token is empty"
       
       if not token.startswith(('eyJ', 'Bearer eyJ')):
           return False, "Token doesn't appear to be JWT format"
       
       parts = token.replace('Bearer ', '').split('.')
       if len(parts) != 3:
           return False, "JWT should have 3 parts separated by dots"
       
       return True, "Token format appears valid"

   # Usage
   is_valid, message = validate_token_format("your-token")
   print(f"Token validation: {message}")

**Network Issues**

.. code-block:: python

   import requests
   from paramus_world import ParamusWorldClient

   def diagnose_connection():
       """Diagnose connection issues"""
       base_url = "http://127.0.0.1:8051"
       
       try:
           # Test basic connectivity
           response = requests.get(f"{base_url}/health", timeout=5)
           print(f"✅ Server reachable: {response.status_code}")
       except requests.ConnectionError:
           print("❌ Cannot connect to server")
           return
       except requests.Timeout:
           print("❌ Server timeout")
           return
       
       try:
           # Test authentication endpoint
           auth_response = requests.post(f"{base_url}/api/auth/token", json={})
           print(f"✅ Auth endpoint reachable: {auth_response.status_code}")
       except Exception as e:
           print(f"❌ Auth endpoint issue: {e}")
       
       try:
           # Test JSON-RPC endpoint
           rpc_response = requests.post(f"{base_url}/api/jsonrpc", json={
               "jsonrpc": "2.0",
               "method": "system.health",
               "id": 1
           })
           print(f"✅ JSON-RPC endpoint reachable: {rpc_response.status_code}")
       except Exception as e:
           print(f"❌ JSON-RPC endpoint issue: {e}")

   # Run diagnostics
   diagnose_connection()
