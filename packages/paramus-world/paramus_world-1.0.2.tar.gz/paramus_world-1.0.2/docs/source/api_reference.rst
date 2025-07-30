API Reference
=============

This section provides detailed documentation for all classes and methods in the Paramus World Client.

ParamusWorldClient
------------------

.. autoclass:: example.ParamusWorldClient
   :members:
   :undoc-members:
   :show-inheritance:

Class Methods
~~~~~~~~~~~~~

.. automethod:: example.ParamusWorldClient.__init__

.. automethod:: example.ParamusWorldClient.authenticate

.. automethod:: example.ParamusWorldClient.submit_chat

.. automethod:: example.ParamusWorldClient.sparql_query

.. automethod:: example.ParamusWorldClient.sparql_update

.. automethod:: example.ParamusWorldClient.check_system_health

Private Methods
~~~~~~~~~~~~~~

.. automethod:: example.ParamusWorldClient._make_jsonrpc_request

Method Details
--------------

Authentication
~~~~~~~~~~~~~

The client supports JWT token-based authentication. You can either:

1. Provide a token during initialization
2. Use the ``authenticate()`` method to get a token

**Token Authentication**::

    client = ParamusWorldClient(token="your-jwt-token")

**Username/Password Authentication**::

    client = ParamusWorldClient()
    token = client.authenticate("username", "password")

Chat Interface
~~~~~~~~~~~~~

The chat interface allows natural language interaction with the AI system.

**Parameters:**

* ``message`` (str): The message to send to the AI
* ``context`` (dict, optional): Additional context for the conversation

**Returns:**

* ``dict``: Response containing the AI's reply

**Example**::

    response = client.submit_chat(
        message="What is the current status?",
        context={"user": "analyst", "department": "research"}
    )

SPARQL Operations
~~~~~~~~~~~~~~~~

Execute SPARQL queries and updates against the knowledge graph.

**Query Parameters:**

* ``query`` (str): The SPARQL query string
* ``format`` (str): Response format (default: "json")

**Update Parameters:**

* ``update`` (str): The SPARQL update string

**Examples**::

    # Query
    results = client.sparql_query("""
        SELECT ?lab ?device WHERE {
            ?lab world:hasDevice ?device .
        }
    """)

    # Update
    result = client.sparql_update("""
        PREFIX world: <https://paramus.ai/world/>
        INSERT DATA {
            world:NewLab world:hasCapacity 20 .
        }
    """)

System Monitoring
~~~~~~~~~~~~~~~~

Monitor system health and status.

**Returns:**

* ``dict``: System health information including:
  
  * ``status``: Overall system status
  * ``active_sessions``: Number of active user sessions
  * ``timestamp``: Current server timestamp
  * ``world_stats``: Knowledge graph statistics

**Example**::

    health = client.check_system_health()
    print(f"System status: {health['status']}")
    print(f"Total triples: {health['world_stats']['triples_count']}")

Error Handling
--------------

The client raises specific exceptions for different error conditions:

**requests.RequestException**
    Network-related errors (connection failures, timeouts)

**ValueError**
    API errors returned by the server

**Example Error Handling**::

    try:
        response = client.submit_chat("Hello")
    except requests.RequestException as e:
        print(f"Network error: {e}")
    except ValueError as e:
        print(f"API error: {e}")

Configuration
-------------

**Base URL Configuration**

Default: ``http://127.0.0.1:8051``

**Endpoints**

* JSON-RPC: ``/api/jsonrpc``
* Authentication: ``/api/auth/token``

**Headers**

* ``Content-Type``: ``application/json``
* ``Accept``: ``application/json``
* ``Authorization``: ``Bearer <token>`` (when authenticated)

**Session Management**

The client uses a ``requests.Session`` object for connection pooling and persistent headers.
