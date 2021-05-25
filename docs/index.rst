
Venmo API
=========

Disclaimer: This is an individual effort and is not PayPal/Venmo sponsored or maintained. 

Introduction
------------

This is a wrapper for the Venmo API. This library provides a Python interface for the Venmo API. It's compatible with Python versions 3.6+.

Installing
----------

You can install or upgrade venmo-api with:

.. code-block:: bash

   $ pip3 install venmo-api --upgrade

Or you can install it from the source:

.. code-block:: bash

   $ git clone https://github.com/mmohades/Venmo.git --recursive
   $ cd Venmo
   $ python3 setup.py install

Getting Started
---------------

Usage
^^^^^

To use the API client, you first need to get your account's access token. Store your access token somewhere safe as anyone with the token can do everything with your Venmo account (e.g., transferring money). Also, make sure to revoke your access token once you are done using it using `log_out() <#revoke-token>`_.

.. code-block:: python

   from venmo_api import Client

   # Get your access token. You will need to complete the 2FA process
   # Please store it somewhere safe and use it next time
   # Never commit your credentials or token to a git repository
   access_token = Client.get_access_token(username='myemail@random.com',
                                           password='your password')
   print("My token:", access_token)

The following is an example of initializing and working with the api client.

.. code-block:: python

   access_token = "YOUR_ACCESS_TOKEN"

   # Initialize api client using an access-token
   client = Client(access_token=access_token)

   # Search for users. You get a maximum of 50 results per request.
   users = client.user.search_for_users(query="Peter")
   for user in users:
       print(user.username)

   # Or pass a callback to make it multi-threaded
   def callback(users):
       for user in users:
           print(user.username)

   client.user.search_for_users(query="peter",
                                callback=callback,
                                limit=10)

Revoke token
""""""""""""

Keep this in mind that your access token never expires! You will need to revoke it yoursef:

.. code-block:: Python

   client.log_out("Bearer a40fsdfhsfhdsfjhdkgljsdglkdsfj3j3i4349t34j7d")

Payment methods
"""""""""""""""

Get all your payment methods to use one's id for sending_money

.. code-block:: python

   payment_methods = client.payment.get_payment_methods()
   for payment_method in payment_methods:
       print(payment_method.to_json())

Sending or requesting money
"""""""""""""""""""""""""""

.. code-block:: python

   # Request money
   client.payment.request_money(32.5, "house expenses", "0000000000000000000")
   # Send money (with default payment method)
   client.payment.send_money(13.68, "thanks for the 🍔", "0000000000000000000")

   # Send money (with the provided payment method id)
   client.payment.send_money(amount=13.68,
                             note="thanks for the 🍔",
                             target_user_id="0000000000000000000",
                             funding_source_id='9999999999999999999')

Transactions
""""""""""""

Getting a user's transactions (only the ones that are visible to you, e.g, their ``public`` transactions)

.. code-block:: python

   def callback(transactions_list):
       for transaction in transactions_list:
           print(transaction)

   # callback is optional. Max number of transactions per request is 50.
   client.user.get_user_transactions(user_id='0000000000000000000',
                                        callback=callback)

Friends list
""""""""""""

.. code-block:: python

   # Get a user's friend's list
   users = client.user.get_user_friends_list(user_id='0000000000000000000')
   for user in users:
       print(user)

Pagination
""""""""""

Here is a pagination example:

.. code-block:: python

   # Get all the transactions possible (prints 50 per request until nothing has left)
   transactions = client.user.get_user_transactions(user_id='0000000000000000000')
   while transactions:
       for transaction in transactions:
           print(transaction)

       print("\n" + "=" * 15 + "\n\tNEXT PAGE\n" + "=" * 15 + "\n")
       transactions = transactions.get_next_page()

Documentation
^^^^^^^^^^^^^

``venmo-api``\ 's documentation lives at `readthedocs.io <https://venmo.readthedocs.io/en/latest/>`_.

Contributing
------------

Contributions of all sizes are welcome. You can help with the wrapper documentation located in /docs. You can also help by `reporting bugs <https://github.com/mmohades/VenmoApi/issues/new>`_. You can add more routes to both  `Venmo Unofficial API Documentation <https://github.com/mmohades/VenmoApiDocumentation>`_ and the ``venmo-api`` wrapper. 

Venmo Unofficial API Documentation
----------------------------------

You can find and contribute to the `Venmo Unofficial API Documentation <https://github.com/mmohades/VenmoApiDocumentation>`_.

.. toctree::
   :maxdepth: 2