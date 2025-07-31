Installation
============

You can install Cronian directly from this git repository:

.. code-block:: bash

   python3 -m pip install "cronian[gurobi] @ git+https://gitlab.tudelft.nl/demoses/cronian"


Note: this includes the optional `gurobi` dependency, since the Gurobi solver is used by default.
If omitted, please make sure to pass your own preferred solver instead when solving through Cronian.
