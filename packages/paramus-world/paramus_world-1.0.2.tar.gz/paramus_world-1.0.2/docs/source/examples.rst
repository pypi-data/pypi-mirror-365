Examples
========

This section provides comprehensive examples for using the Paramus World Client.

Basic Examples
--------------

Simple Health Check
~~~~~~~~~~~~~~~~~~~

.. literalinclude:: ../../examples/example.py
   :language: python
   :lines: 184-195
   :caption: Basic health check example

Chat Interaction
~~~~~~~~~~~~~~~

.. code-block:: python
   :caption: Chat with context

   from example import ParamusWorldClient

   client = ParamusWorldClient(token="your-token")

   # Simple chat
   response = client.submit_chat("Hello, how are you?")
   print(f"AI: {response['response']}")

   # Chat with context
   context = {
       "user_role": "researcher",
       "current_task": "data_analysis",
       "timestamp": "2025-07-28"
   }

   response = client.submit_chat(
       "Can you help me analyze the laboratory data?",
       context=context
   )
   print(f"AI: {response['response']}")

SPARQL Examples
--------------

Basic Queries
~~~~~~~~~~~~

.. code-block:: python
   :caption: Simple SPARQL queries

   # Get all entities and their types
   query = """
   SELECT ?entity ?type WHERE {
       ?entity a ?type .
   }
   LIMIT 10
   """
   results = client.sparql_query(query)

   # Count entities by type
   query = """
   SELECT ?type (COUNT(?entity) as ?count) WHERE {
       ?entity a ?type .
   }
   GROUP BY ?type
   ORDER BY DESC(?count)
   """
   results = client.sparql_query(query)

Laboratory Data Queries
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python
   :caption: Laboratory-specific queries

   # Find all laboratories and their devices
   query = """
   PREFIX world: <https://paramus.ai/world/>
   SELECT ?lab ?device ?deviceType WHERE {
       ?lab a world:Laboratory .
       ?lab world:hasDevice ?device .
       ?device a ?deviceType .
   }
   """
   results = client.sparql_query(query)

   # Get laboratory capacity information
   query = """
   PREFIX world: <https://paramus.ai/world/>
   SELECT ?lab ?capacity WHERE {
       ?lab a world:Laboratory .
       ?lab world:capacity ?capacity .
   }
   """
   results = client.sparql_query(query)

Data Updates
~~~~~~~~~~~

.. code-block:: python
   :caption: Adding new data to the knowledge graph

   # Add a new laboratory
   update = """
   PREFIX world: <https://paramus.ai/world/>
   INSERT DATA {
       world:NewLab a world:Laboratory .
       world:NewLab world:capacity 25 .
       world:NewLab rdfs:label "Advanced Research Lab" .
   }
   """
   result = client.sparql_update(update)

   # Add a new device to an existing lab
   update = """
   PREFIX world: <https://paramus.ai/world/>
   INSERT DATA {
       world:NewMicroscope a world:LabDevice .
       world:NewMicroscope world:model "Advanced SEM" .
       world:BiologyLab world:hasDevice world:NewMicroscope .
   }
   """
   result = client.sparql_update(update)

Advanced Examples
----------------

Error Handling and Retry Logic
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python
   :caption: Robust error handling with retry logic

   import time
   import requests
   from example import ParamusWorldClient

   def robust_api_call(client, method, *args, max_retries=3, **kwargs):
       """Make API calls with retry logic."""
       for attempt in range(max_retries):
           try:
               if method == "chat":
                   return client.submit_chat(*args, **kwargs)
               elif method == "query":
                   return client.sparql_query(*args, **kwargs)
               elif method == "health":
                   return client.check_system_health()
           except requests.RequestException as e:
               print(f"Attempt {attempt + 1} failed: {e}")
               if attempt < max_retries - 1:
                   time.sleep(2 ** attempt)  # Exponential backoff
               else:
                   raise
           except ValueError as e:
               print(f"API error: {e}")
               raise

   # Usage
   client = ParamusWorldClient(token="your-token")
   health = robust_api_call(client, "health")

Batch Processing
~~~~~~~~~~~~~~~

.. code-block:: python
   :caption: Process multiple queries efficiently

   def batch_sparql_queries(client, queries):
       """Execute multiple SPARQL queries in batch."""
       results = []
       
       for i, query in enumerate(queries):
           try:
               print(f"Executing query {i+1}/{len(queries)}")
               result = client.sparql_query(query)
               results.append({
                   "query_index": i,
                   "query": query,
                   "result": result,
                   "success": True
               })
           except Exception as e:
               results.append({
                   "query_index": i,
                   "query": query,
                   "error": str(e),
                   "success": False
               })
       
       return results

   # Example usage
   queries = [
       "SELECT ?s WHERE { ?s a world:Laboratory }",
       "SELECT ?s WHERE { ?s a world:LabDevice }",
       "SELECT ?s WHERE { ?s a world:Person }"
   ]

   client = ParamusWorldClient(token="your-token")
   results = batch_sparql_queries(client, queries)

   # Process results
   for result in results:
       if result["success"]:
           print(f"Query {result['query_index']}: Success")
       else:
           print(f"Query {result['query_index']}: Error - {result['error']}")

Data Analysis Workflow
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python
   :caption: Complete data analysis workflow

   import json
   from example import ParamusWorldClient

   def analyze_laboratory_data(client):
       """Complete workflow for analyzing laboratory data."""
       
       # 1. Check system health
       print("=== System Health Check ===")
       health = client.check_system_health()
       print(f"System Status: {health['status']}")
       print(f"Total entities: {health['world_stats']['things_count']}")
       print(f"Total triples: {health['world_stats']['triples_count']}")
       
       # 2. Get laboratory statistics
       print("\n=== Laboratory Statistics ===")
       lab_query = """
       PREFIX world: <https://paramus.ai/world/>
       SELECT ?lab ?capacity WHERE {
           ?lab a world:Laboratory .
           OPTIONAL { ?lab world:capacity ?capacity }
       }
       """
       lab_results = client.sparql_query(lab_query)
       print(f"Laboratory data:\n{lab_results['result']}")
       
       # 3. Get device information
       print("\n=== Device Analysis ===")
       device_query = """
       PREFIX world: <https://paramus.ai/world/>
       SELECT ?device ?type ?lab WHERE {
           ?device a ?type .
           ?lab world:hasDevice ?device .
           FILTER(?type != world:Thing)
       }
       """
       device_results = client.sparql_query(device_query)
       print(f"Device information:\n{device_results['result']}")
       
       # 4. AI analysis
       print("\n=== AI Analysis ===")
       analysis_request = """
       Based on the laboratory and device data in the knowledge graph,
       can you provide insights about:
       1. Laboratory utilization
       2. Equipment distribution
       3. Potential optimization opportunities
       """
       
       ai_response = client.submit_chat(
           analysis_request,
           context={"analysis_type": "laboratory_optimization"}
       )
       print(f"AI Insights:\n{ai_response['response']}")
       
       return {
           "health": health,
           "laboratories": lab_results,
           "devices": device_results,
           "ai_insights": ai_response
       }

   # Run the analysis
   client = ParamusWorldClient(token="your-token")
   analysis_results = analyze_laboratory_data(client)

Interactive Examples
-------------------

Command Line Interface
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python
   :caption: Simple CLI for interacting with Paramus World

   #!/usr/bin/env python3
   import sys
   from example import ParamusWorldClient

   def main():
       if len(sys.argv) < 2:
           print("Usage: python cli.py <token> [command]")
           sys.exit(1)
       
       token = sys.argv[1]
       command = sys.argv[2] if len(sys.argv) > 2 else "interactive"
       
       client = ParamusWorldClient(token=token)
       
       if command == "health":
           health = client.check_system_health()
           print(f"System Status: {health['status']}")
           
       elif command == "interactive":
           print("Paramus World Client - Interactive Mode")
           print("Commands: chat <message>, query <sparql>, health, quit")
           
           while True:
               try:
                   cmd = input("> ").strip()
                   
                   if cmd == "quit":
                       break
                   elif cmd == "health":
                       health = client.check_system_health()
                       print(f"Status: {health['status']}")
                   elif cmd.startswith("chat "):
                       message = cmd[5:]
                       response = client.submit_chat(message)
                       print(f"AI: {response['response']}")
                   elif cmd.startswith("query "):
                       query = cmd[6:]
                       results = client.sparql_query(query)
                       print(f"Results:\n{results['result']}")
                   else:
                       print("Unknown command")
                       
               except KeyboardInterrupt:
                   break
               except Exception as e:
                   print(f"Error: {e}")
       
       else:
           print(f"Unknown command: {command}")

   if __name__ == "__main__":
       main()

Jupyter Notebook Integration
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python
   :caption: Use in Jupyter notebooks

   # Cell 1: Setup
   from example import ParamusWorldClient
   import pandas as pd
   import json

   client = ParamusWorldClient(token="your-token")

   # Cell 2: Get data
   query = """
   SELECT ?lab ?device ?capacity WHERE {
       ?lab a world:Laboratory .
       OPTIONAL { ?lab world:capacity ?capacity }
       OPTIONAL { ?lab world:hasDevice ?device }
   }
   """
   results = client.sparql_query(query)

   # Cell 3: Parse and visualize
   # Parse SPARQL results into structured data
   lines = results['result'].split('\n')[2:]  # Skip headers
   data = []
   for line in lines:
       if line.strip():
           parts = line.split(' | ')
           if len(parts) >= 2:
               data.append({
                   'lab': parts[0].strip(),
                   'device': parts[1].strip() if len(parts) > 1 else None,
                   'capacity': parts[2].strip() if len(parts) > 2 else None
               })

   df = pd.DataFrame(data)
   display(df)

   # Cell 4: AI analysis
   ai_response = client.submit_chat(
       "What insights can you provide about this laboratory data?",
       context={"data_source": "jupyter_analysis"}
   )
   print(f"AI Analysis: {ai_response['response']}")

Complete Application Example
---------------------------

.. literalinclude:: ../../examples/example.py
   :language: python
   :caption: Complete working example

This example demonstrates all the major features of the Paramus World Client in a single application.
