# Venmo API

## Introduction

This is a wrapper for the Venmo API. This library provides a Python interface for the Venmo API. It's compatible with Python versions 3.6+ and PyPy.

## Usage

In short, you can send money, request for money, get anyone's public transactions, get public profile info, etc. You can use the wrapper for various reasons. One cool example could be crawling public transactions and using graph databases, like Neo4j, to find fraud or drug dealers. You can also run any analysis on transactions' notes.

 ```python
from Venmo import VenmoApi

# Get your access token
access_token = VenmoApi.get_access_token(username='myemail@random.com',
                                       password='your very difficult password')
venmo_api = VenmoApi(access_token=access_token)

# Search for users. You get 50 results per page.
users = venmo.user.search_for_users(query="Peter",
                                    page=2)
for user in users:
    print(user.username)

# Or, you can pass a callback to make it async

def callback(users):
    for user in users:
        print(user.username)
venmo.user.search_for_users(query="peter",
                            callback=callback,
                           page=2,
                           count=10)

 ```
Or you can get anyone's public transactions

```python
def callback(transactions_list):
    for transaction in transactions_list:
        print(transaction)

venmo_api.user.get_user_transactions(user_id='0000000000000',
                                     callback=callback) 
```
You can also make payments, request money, get friends_list, get public profile info and so on and so forth.

## Getting Started

### Installing



### Documentation



## Contributing

Contributions of all sizes are welcome. You can also help by [reporting bugs](https://github.com/mmohades/VenmoApi/issues/new).

## Venmo Unofficial API Documentation

You can find and contribute to the [Venmo Unofficial API Documentation](https://github.com/mmohades/VenmoApiDocumentation).