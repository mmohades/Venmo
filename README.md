# Venmo API

Disclaimer: This is an individual effort and is not PayPal/Venmo sponsored or maintained. 

## Introduction

This is a wrapper for the Venmo API. This library provides a Python interface for the Venmo API. It's compatible with Python versions 3.6+.

## Installing

You can install or upgrade venmo-api with:

```bash
$ pip3 install venmo-api --upgrade
```

Or you can install it from the source:

```bash
$ git clone https://github.com/mmohades/Venmo.git --recursive
$ cd Venmo
$ python3 setup.py install
```

## Getting Started

### Usage

In short, you can send money, request for money, get a user's public transactions, get a user's public profile info, etc. The following is an example of initializing and working with it.

 ```python
from venmo_api import Client

# Get your access token. You will need to complete the 2FA process
access_token = Client.get_access_token(username='myemail@random.com',
                                        password='your password')
venmo = Client(access_token=access_token)

# Search for users. You get 50 results per page.
users = venmo.user.search_for_users(query="Peter",
                                     page=2)
for user in users:
    print(user.username)

# Or, you can pass a callback to make it multi-threaded
def callback(users):
    for user in users:
        print(user.username)
venmo.user.search_for_users(query="peter",
                             callback=callback,
                             page=2,
                             count=10)

 ```
Keep this in mind that your access token never expires! You will need to revoke it by yoursef.

```Python
venmo.log_out("Bearer a40fsdfhsfhdsfjhdkgljsdglkdsfj3j3i4349t34j7d")
```

```python
# Request money
venmo.payment.request_money(32.5, "house expenses", "1122334455667")
```

```python
# Send money
venmo.payment.send_money(13.68, "thanks for the 🍔", "1122334455667")
```



Getting a user's transactions (public, friends and privates that happen between your account and user_id account)

```python
def callback(transactions_list):
    for transaction in transactions_list:
        print(transaction)

# callback is optional. Max number of transactions per request is 50.
venmo_api.user.get_user_transactions(user_id='0000000000000',
                                     callback=callback) 
```



### Documentation

`venmo-api`'s documentation lives at [readthedocs.io](https://venmo.readthedocs.io/en/latest/).

## Contributing

Contributions of all sizes are welcome. You can help with the wrapper documentation located in /docs. You can also help by [reporting bugs](https://github.com/mmohades/VenmoApi/issues/new). You can add more routes to both  [Venmo Unofficial API Documentation](https://github.com/mmohades/VenmoApiDocumentation) and the `venmo-api` wrapper. 

## Venmo Unofficial API Documentation

You can find and contribute to the [Venmo Unofficial API Documentation](https://github.com/mmohades/VenmoApiDocumentation).