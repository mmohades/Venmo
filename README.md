# Venmo API

## Introduction

This is a wrapper for the Venmo API. This library provides a Python interface for the Venmo API. It's compatible with Python versions 3.6+.

## Usage

In short, you can send money, request for money, get a user's public transactions, get a user's public profile info, etc. The following is an example of initializing and working with it.

 ```python
from Venmo import VenmoApi

# Get your access token. You will need to complete the 2FA process
access_token = VenmoApi.get_access_token(username='myemail@random.com',
                                          password='your password')
venmo_api = VenmoApi(access_token=access_token)

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
Getting a user's public transactions

```python
def callback(transactions_list):
    for transaction in transactions_list:
        print(transaction)

# callback is optional
venmo_api.user.get_user_transactions(user_id='0000000000000',
                                     callback=callback) 
```


## Getting Started

### Installation



### Documentation



## Contributing

Contributions of all sizes are welcome. You can also help by [reporting bugs](https://github.com/mmohades/VenmoApi/issues/new).

## Venmo Unofficial API Documentation

You can find and contribute to the [Venmo Unofficial API Documentation](https://github.com/mmohades/VenmoApiDocumentation).