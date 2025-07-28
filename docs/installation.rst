Installation
============

Metapub can be installed using pip:

.. code-block:: bash

   pip install metapub

Requirements
------------

* Python 3.7+
* lxml
* requests
* eutils
* habanero
* Other dependencies listed in setup.py

Optional Dependencies
--------------------

For testing:

.. code-block:: bash

   pip install metapub[test]

Environment Variables
--------------------

**NCBI_API_KEY**
   Your NCBI API key for increased rate limits. Obtain from https://www.ncbi.nlm.nih.gov/account/

**METAPUB_CACHE_DIR** 
   Directory for caching NCBI responses. Defaults to user cache directory.

Example:

.. code-block:: bash

   export NCBI_API_KEY="your_api_key_here"
   export METAPUB_CACHE_DIR="/path/to/cache"
