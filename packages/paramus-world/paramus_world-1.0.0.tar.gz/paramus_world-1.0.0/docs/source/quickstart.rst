Quick Start Guide
=================

This guide will help you get started with the Paramus World Client quickly.

Prerequisites
-------------

Before you begin, make sure you have:

1. Python 3.8+ installed
2. The Paramus World Client installed (``pip install paramus-world``)
3. A valid JWT authentication token
4. Access to a running Paramus World server

Basic Usage
-----------

Here's a simple example to get you started:

.. code-block:: python

   from paramus_world import ParamusWorldClient

   # Initialize the client with your token
   client = ParamusWorldClient(token="your-jwt-token-here")

   # Check if the system is healthy
   health = client.check_system_health()
   print(f"System status: {health['status']}")

Step-by-Step Tutorial
---------------------

1. Import and Initialize
~~~~~~~~~~~~~~~~~~~~~~~~

First, import the client and create an instance:

.. code-block:: python

   from paramus_world import ParamusWorldClient
   
   # Initialize with default settings (localhost:8051)
   client = ParamusWorldClient(token="your-token")
   
   # Or specify a custom base URL
   client = ParamusWorldClient(
       base_url="https://your-server.com:8051",
       token="your-token"
   )

The simplest way to interact with Paramus World is through the chat interface::

    response = client.submit_chat(
        message="Hello, what can you tell me about the system?",
        context={"source": "quickstart_guide"}
    )
    
    print(f"AI Response: {response['response']}")

Query the Knowledge Graph
~~~~~~~~~~~~~~~~~~~~~~~~~

Execute SPARQL queries to explore the knowledge graph::

    query = """
    SELECT ?subject ?predicate ?object
    WHERE {
        ?subject ?predicate ?object .
    }
    LIMIT 5
    """
    
    results = client.sparql_query(query)
    print(f"Query results: {results['result']}")

Update the Knowledge Graph
~~~~~~~~~~~~~~~~~~~~~~~~~

Add new data to the knowledge graph::

    update = """
    PREFIX world: <https://paramus.ai/world/>
    INSERT DATA {
        world:MyEntity world:hasProperty "my_value" .
    }
    """
    
    result = client.sparql_update(update)
    print(f"Update result: {result}")

Common Patterns
--------------

Error Handling
~~~~~~~~~~~~~

Always wrap API calls in try-catch blocks::

    try:
        response = client.submit_chat("Hello!")
        print(response['response'])
    except requests.RequestException as e:
        print(f"Network error: {e}")
    except ValueError as e:
        print(f"API error: {e}")

Working with Context
~~~~~~~~~~~~~~~~~~

Provide context to improve AI responses::

    context = {
        "user_id": "john_doe",
        "session_id": "session_123",
        "timestamp": "2025-07-28T10:00:00Z",
        "application": "data_analysis"
    }
    
    response = client.submit_chat(
        message="Analyze the latest data trends",
        context=context
    )

Batch Operations
~~~~~~~~~~~~~~~

Process multiple queries efficiently::

    queries = [
        "SELECT ?s WHERE { ?s a world:Laboratory }",
        "SELECT ?s WHERE { ?s a world:LabDevice }",
        "SELECT ?s WHERE { ?s a world:Person }"
    ]
    
    results = []
    for query in queries:
        result = client.sparql_query(query)
        results.append(result)

Complete Example
---------------

Here's a complete example that demonstrates all major features::

    #!/usr/bin/env python3
    import json
    from example import ParamusWorldClient
    
    def main():
        # Initialize client
        client = ParamusWorldClient(token="your-token")
        
        try:
            # 1. Check system health
            print("=== System Health ===")
            health = client.check_system_health()
            print(f"Status: {health['status']}")
            print(f"Active sessions: {health['active_sessions']}")
            
            # 2. Chat interaction
            print("\n=== Chat Interaction ===")
            chat_response = client.submit_chat(
                "What types of entities are in the knowledge graph?"
            )
            print(f"AI: {chat_response['response']}")
            
            # 3. SPARQL query
            print("\n=== SPARQL Query ===")
            query = """
            SELECT ?type (COUNT(?entity) as ?count)
            WHERE {
                ?entity a ?type .
            }
            GROUP BY ?type
            """
            results = client.sparql_query(query)
            print(f"Entity types:\n{results['result']}")
            
            # 4. Follow-up chat
            print("\n=== Follow-up Chat ===")
            followup = client.submit_chat(
                "Can you explain what these entities represent?",
                context={"previous_query": "entity_types"}
            )
            print(f"AI: {followup['response']}")
            
        except Exception as e:
            print(f"Error: {e}")
    
    if __name__ == "__main__":
        main()

Next Steps
----------

* Explore the :doc:`api_reference` for detailed method documentation
* Check out more :doc:`examples` for advanced usage patterns
* Learn about :doc:`troubleshooting` common issues
