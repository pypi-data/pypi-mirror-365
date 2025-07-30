Installation
============

System Requirements
-------------------

The Paramus World Client requires:

- Python 3.8 or higher
- ``requests`` library (automatically installed)

Installation Methods
--------------------

Install via pip
~~~~~~~~~~~~~~~

The recommended way to install the Paramus World Client is using pip:

.. code-block:: bash

   pip install paramus-world

Install from Source
~~~~~~~~~~~~~~~~~~~

You can also install directly from the source repository:

.. code-block:: bash

   git clone https://github.com/Gressling/paramus-world-client.git
   cd paramus-world-client
   pip install -e .

Virtual Environment (Recommended)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

It's recommended to use a virtual environment:

.. code-block:: bash

   # Create virtual environment
   python -m venv venv
   
   # Activate virtual environment
   # On macOS/Linux:
   source venv/bin/activate
   # On Windows:
   venv\Scripts\activate
   
   # Install the package
   pip install paramus-world

Verify Installation
-------------------

After installation, you can verify that the package is working correctly:

.. code-block:: python

   from paramus_world import ParamusWorldClient
   
   # This should not raise any import errors
   print("Paramus World Client successfully installed!")
    
    # On macOS/Linux:
    source .venv/bin/activate
    
    # On Windows:
    .venv\Scripts\activate

3. **Install Dependencies**::

    pip install -r examples/requirements.txt

4. **Verify Installation**::

    cd examples
    python example.py

Configuration
-------------

Environment Variables
~~~~~~~~~~~~~~~~~~~~

You can configure the client using environment variables:

* ``PARAMUS_WORLD_BASE_URL`` - Base URL for the API (default: http://127.0.0.1:8051)
* ``PARAMUS_WORLD_TOKEN`` - Authentication token

Example::

    export PARAMUS_WORLD_BASE_URL="https://api.paramus.ai"
    export PARAMUS_WORLD_TOKEN="your-jwt-token-here"

Authentication Setup
~~~~~~~~~~~~~~~~~~~

To obtain an authentication token, contact your system administrator or use the authentication endpoint::

    import requests
    
    response = requests.post(
        "http://127.0.0.1:8051/api/auth/token",
        json={"username": "your_username", "password": "your_password"}
    )
    
    token = response.json()["token"]

Development Setup
----------------

For development work, install additional dependencies::

    pip install pytest sphinx sphinx-rtd-theme

Run tests::

    pytest test/

Build documentation::

    cd docs
    ./sphinx.sh
