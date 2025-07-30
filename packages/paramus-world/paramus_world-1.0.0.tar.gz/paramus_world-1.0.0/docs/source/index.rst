.. Paramus World Client documentation master file

Paramus World Client Documentation
===================================

A Python client library for interacting with the Paramus World API, providing access to knowledge graphs, AI chat functionality, and SPARQL query/update capabilities.

Created by: **Thorsten Gressling** (gressling@paramus.ai)

.. image:: https://img.shields.io/badge/Python-3.8%2B-blue
   :alt: Python Version

.. image:: https://img.shields.io/badge/License-MIT-green
   :alt: License

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installation
   quickstart
   api_reference
   examples_real
   authentication

Overview
--------

The Paramus World Client is a Python library that provides access to the Paramus World API through a simple, easy-to-use interface. The API supports:

- **Chat Interface**: Submit messages to the AI chat system
- **SPARQL Operations**: Execute queries and updates on the knowledge graph
- **System Monitoring**: Check system health and status
- **Authentication**: Secure API access with JWT tokens

Key Features
------------

- **Simple API**: Easy-to-use Python interface for all Paramus World operations
- **Type Hints**: Full type annotation support for better development experience
- **Error Handling**: Comprehensive error handling with clear error messages
- **Session Management**: Automatic session handling with authentication
- **JSON-RPC Protocol**: Built on standard JSON-RPC 2.0 for reliable communication

Quick Example
-------------

Here's a quick example of how to use the Paramus World Client:

.. code-block:: python

   from paramus_world import ParamusWorldClient

   # Initialize the client
   client = ParamusWorldClient(token="your-jwt-token")

   # Check system health
   health = client.check_system_health()
   print(f"System status: {health['status']}")

   # Submit a chat message
   response = client.submit_chat("Hello, Paramus World!")
   print(f"AI Response: {response['response']}")

   # Execute a SPARQL query
   query = "SELECT ?s ?p ?o WHERE { ?s ?p ?o } LIMIT 10"
   results = client.sparql_query(query)
   print(f"Query results: {results}")

Installation
------------

Install the Paramus World Client using pip:

.. code-block:: bash

   pip install paramus-world

API Endpoints
-------------

The client connects to the following endpoints:

- **Base URL**: ``http://127.0.0.1:8051`` (configurable)
- **JSON-RPC Endpoint**: ``/api/jsonrpc``
- **Authentication Endpoint**: ``/api/auth/token``

Available Methods
-----------------

The client provides access to these API methods:

- ``chat.submit`` - Submit chat messages to the AI system
- ``sparql.query`` - Execute SPARQL queries against the knowledge graph
- ``sparql.update`` - Execute SPARQL updates to modify the knowledge graph
- ``system.health`` - Check the health status of the system

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

- **Chat Interface**: Submit messages to the AI system and receive intelligent responses
- **SPARQL Queries**: Execute SPARQL queries against the knowledge graph
- **SPARQL Updates**: Perform updates to the knowledge graph data
- **System Health**: Monitor the health and status of the Paramus World system
- **Authentication**: JWT token-based authentication

Quick Start
-----------

Installation::

    pip install requests

Basic Usage::

    from example import ParamusWorldClient

    # Initialize client with authentication token
    client = ParamusWorldClient(token="your-jwt-token")

    # Check system health
    health = client.check_system_health()
    print(f"System status: {health['status']}")

    # Submit a chat message
    response = client.submit_chat("Hello, how can you help me?")
    print(f"AI Response: {response['response']}")

    # Execute a SPARQL query
    query = "SELECT ?s ?p ?o WHERE { ?s ?p ?o } LIMIT 10"
    results = client.sparql_query(query)
    print(f"Query results: {results}")

API Configuration
-----------------

**Default Configuration:**

- **Base URL**: ``http://127.0.0.1:8051``
- **JSON-RPC Endpoint**: ``/api/jsonrpc``
- **Authentication Endpoint**: ``/api/auth/token``

**Available Methods:**

- ``chat.submit`` - Submit chat messages to the AI system
- ``sparql.query`` - Execute SPARQL queries against the knowledge base
- ``sparql.update`` - Execute SPARQL updates to modify the knowledge base
- ``system.health`` - Check the health status of the system

Contents
--------

.. toctree::
   :maxdepth: 2
   :caption: Documentation:

   installation
   quickstart
   api_reference
   examples
   troubleshooting

.. toctree::
   :maxdepth: 2
   :caption: API Reference:

   client
   methods

Installation
============

Requirements
------------

* Python 3.8 or higher
* requests library

Install from source::

    git clone https://github.com/Gressling/paramus-world-client.git
    cd paramus-world-client
    python -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    pip install -r examples/requirements.txt

Quick Start
===========

Authentication
--------------

To use the Paramus World Client, you need a valid JWT authentication token. Contact your system administrator or obtain it through the authentication endpoint.

Basic Example
-------------

.. literalinclude:: ../../examples/example.py
   :language: python
   :lines: 184-220
   :caption: Basic usage example

API Reference
=============

ParamusWorldClient Class
------------------------

.. automodule:: example
   :members:
   :undoc-members:
   :show-inheritance:

Methods
-------

The client provides the following main methods:

Chat Interface
~~~~~~~~~~~~~~

Submit messages to the AI system and receive intelligent responses.

SPARQL Operations
~~~~~~~~~~~~~~~~~

Execute queries and updates against the knowledge graph using SPARQL.

System Monitoring
~~~~~~~~~~~~~~~~~

Check system health and retrieve status information.

Examples
========

Complete Examples
-----------------

Check the ``examples/`` directory for complete working examples:

* ``example.py`` - Complete client demonstration
* ``example_quickstart.ipynb`` - Jupyter notebook tutorial

Troubleshooting
===============

Common Issues
-------------

**Authentication Errors (401 Unauthorized)**

- Verify your JWT token is valid and not expired
- Check that the token is properly formatted
- Ensure you're using the correct authentication endpoint

**Connection Errors (404 Not Found)**

- Verify the base URL is correct (default: ``http://127.0.0.1:8051``)
- Check that the Paramus World server is running
- Confirm the API endpoints are available

**Method Not Found (-32601)**

- Ensure you're using supported API methods
- Check the method name spelling and case sensitivity
- Verify the API version compatibility

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. toctree::
   :maxdepth: 2
   :caption: User Guide

   guide/index
   user_guide/index

.. toctree::
   :maxdepth: 2
   :caption: Tutorials and Examples

   tutorials/index
   case_studies/index

.. toctree::
   :maxdepth: 2
   :caption: Unit Operations

   unit/index

.. toctree::
   :maxdepth: 2
   :caption: Transport Systems

   transport/index

.. toctree::
   :maxdepth: 2
   :caption: Control Systems

   controller/index

.. toctree::
   :maxdepth: 2
   :caption: Process Optimization

   optimization/index

.. toctree::
   :maxdepth: 2
   :caption: Semantic Plant Design

   plant/index

.. toctree::
   :maxdepth: 3
   :caption: Programming Interfaces (API)

   api/index
   api/units_package
   api/transport_package
   api/controllers_package
   api/analysis_package
   api/simulation_package
   api/optimization_package
   api/scheduling_package
   api/utilities_package

.. toctree::
   :maxdepth: 2
   :caption: Theory and Background

   theory/index

.. toctree::
   :maxdepth: 1
   :caption: Developer Resources

   developer/index

.. toctree::
   :maxdepth: 1
   :caption: Project Information

   project/index

Process Control Documentation
-----------------------------

The PARAMUS-WORLD-CLIENT Process Control API is organized into focused packages:

**Modern Modular Packages (Recommended):**

* **Analysis Package** - Transfer functions, system analysis, and model identification tools
* **Simulation Package** - Dynamic process simulation with control loop integration
* **Optimization Package** - Economic optimization, parameter estimation, and process optimization
* **Scheduling Package** - Batch process scheduling using State-Task Networks
* **Transport Package** - Fluid transport systems, pipeline modeling, and multiphase flow
* **Utilities Package** - Control design utilities, mathematical tools, and data processing
* **Units Package** - Physical process equipment (tanks, pumps, reactors, etc.)
* **Controllers Package** - Control algorithms and implementations

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

