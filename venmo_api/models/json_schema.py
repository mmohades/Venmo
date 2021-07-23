class JSONSchema:

    @staticmethod
    def transaction(json):
        return TransactionParser(json=json)

    @staticmethod
    def user(json, is_profile=None):
        return UserParser(json=json, is_profile=is_profile)

    @staticmethod
    def merchant(json):
        return MerchantParser(json)

    @staticmethod
    def payment_method(json):
        return PaymentMethodParser(json)

    @staticmethod
    def payment(json):
        return PaymentParser(json)

    @staticmethod
    def comment(json):
        return CommentParser(json)

    @staticmethod
    def mention(json):
        return MentionParser(json)


class TransactionParser:

    def __init__(self, json):
        if not json:
            return

        self.json = json
        self.transaction_type = json.get(transaction_json_format['transaction_type'])
        if self.transaction_type == "authorization":
            self.authorization = json.get(transaction_json_format['authorization'])
        else:
            self.payment = json.get(transaction_json_format['payment'])


    def get_story_id(self):
        return self.authorization.get(authorization_format['story_id']) if hasattr(self, 'authorization') else self.json.get(transaction_json_format['story_id'])

    def get_date_created(self):
        return self.json.get(transaction_json_format['date_created'])

    def get_date_updated(self):
        return self.json.get(transaction_json_format['date_updated'])

    def get_actor_app(self):
        return self.authorization.get(authorization_format['app']) if hasattr(self, 'authorization') else self.json.get(transaction_json_format['app'])

    def get_audience(self):
        return self.json.get(transaction_json_format['aud'])

    def get_likes(self):
        return self.json.get(transaction_json_format['likes'])

    def get_comments(self):
        comments = self.json.get(transaction_json_format['comments'])
        return comments.get(transaction_json_format['comments_list']) if comments else comments

    def get_transaction_type(self):
        return self.transaction_type

    def get_payment_id(self):
        return self.payment.get(payment_json_format['payment_id'])

    def get_type(self):
        return self.payment.get(payment_json_format['type'])

    def get_date_completed(self):
        return self.payment.get(payment_json_format['date_completed'])

    def get_story_note(self):
        return "" if hasattr(self, 'authorization') else self.payment.get(payment_json_format['note'])

    def get_actor(self):
        return self.authorization.get(authorization_format['user']) if hasattr(self, 'authorization') else self.payment.get(payment_json_format['actor'])

    def get_target(self):
        return self.authorization.get(authorization_format['merchant']) if hasattr(self, 'authorization') else self.payment.get(payment_json_format['target']).get('user')

    def get_status(self):
        return self.authorization.get(authorization_format['status']) if hasattr(self, 'authorization') else self.payment.get(payment_json_format['status'])

    def get_amount(self):
        return self.get_captures()[0].get(authorization_format['amount_cents']) if hasattr(self, 'authorization') else self.payment.get(payment_json_format['amount'])

    def get_authorization_types(self):
        return self.authorization.get(authorization_format['authorization_types'])

    def get_rewards(self):
        return self.authorization.get(authorization_format['rewards'])

    def get_is_venmo_card(self):
        return self.authorization.get(authorization_format['is_venmo_card'])

    def get_decline(self):
        return self.authorization.get(authorization_format['decline'])

    def get_payment_method(self):
        return self.authorization.get(authorization_format['payment_method'])
    
    def get_acknowledged(self):
        return self.authorization.get(authorization_format['acknowledged'])

    def get_atm_fees(self):
        return self.authorization.get(authorization_format['atm_fees'])

    def get_rewards_earned(self):
        return self.authorization.get(authorization_format['rewards_earned'])

    def get_descriptor(self):
        return self.authorization.get(authorization_format['descriptor'])

    def get_captures(self):
        return self.authorization.get(authorization_format['captures'])

    def get_point_of_sale(self):
        return self.authorization.get(authorization_format['point_of_sale'])


transaction_json_format = {
    "story_id": "id",
    "date_created": "date_created",
    "date_updated": "date_updated",
    "aud": "audience",
    "note": "note",
    "app": "app",
    "payment": "payment",
    "comments": "comments",
    "comments_list": "data",
    "likes": "likes",
    "transaction_type": "type",
    "authorization": "authorization",
}
payment_json_format = {
    "status": "status",
    "payment_id": "id",
    "date_completed": "date_completed",
    "target": "target",
    "actor": "actor",
    "note": "note",
    'type': 'action',
    'amount': 'amount'
}
authorization_format = {
    "status": "status",
    "merchant": "merchant",
    "authorization_types": "authorization_types",
    "rewards": "rewards",
    "is_venmo_card": "is_venmo_card",
    "decline": "decline",
    "payment_method": "payment_method",
    "story_id": "story_id",
    # "created_at": "created_at", # Duplicate
    "acknowledged": "acknowledged",
    "atm_fees": "atm_fees",
    "rewards_earned": "rewards_earned",
    "descriptor": "descriptor",
    "amount": "amount",
    "user": "user",
    "captures": "captures",
    # "id": "id", # Duplicate
    "point_of_sale": "point_of_sale",
    "app": "app",
    "amount_cents": "amount_cents",
}


class MerchantParser:
    def __init__(self, json):

        if not json:
            return

        self.json = json
    
    def get_merchant_id(self):
        return self.json.get(merchant_json_format['merchant_id'])
    
    def get_braintree_merchant_id(self):
        return self.json.get(merchant_json_format['braintree_id'])

    def get_paypal_merchant_id(self):
        return self.json.get(merchant_json_format['paypal_id'])

    def get_display_name(self):
        return self.json.get(merchant_json_format['display_name'])

    def get_is_subscription(self):
        return self.json.get(merchant_json_format['is_sub'])

    def get_image_url(self):
        return self.json.get(merchant_json_format['img_url'])

    def get_image_datetime_updated(self):
        return self.json.get(merchant_json_format['img_updated'])

    def get_datetime_updated(self):
        return self.json.get(merchant_json_format['updated'])

    def get_datetime_created(self):
        return self.json.get(merchant_json_format['created'])


merchant_json_format = {
    "merchant_id": "id",
    "braintree_id": "braintree_merchant_id",
    "paypal_id": "paypal_merchant_id",
    "display_name": "display_name",
    "is_sub": "is_subscription",
    "img_url": "image_url",
    "img_updated": "image_datetime_updated",
    "updated": "datetime_updated",
    "created": "datetime_created",
}


class UserParser:

    def __init__(self, json, is_profile=False):

        if not json:
            return

        self.json = json
        self.is_profile = is_profile

        if is_profile:
            self.parser = profile_json_format
        else:
            self.parser = user_json_format

    def get_user_id(self):
        return self.json.get(self.parser.get('user_id'))

    def get_username(self):
        return self.json.get(self.parser.get('username'))

    def get_first_name(self):
        return self.json.get(self.parser.get('first_name'))

    def get_last_name(self):
        return self.json.get(self.parser.get('last_name'))

    def get_full_name(self):
        return self.json.get(self.parser.get('full_name'))

    def get_phone(self):
        return self.json.get(self.parser.get('phone'))

    def get_picture_url(self):
        return self.json.get(self.parser.get('picture_url'))

    def get_about(self):
        return self.json.get(self.parser.get('about'))

    def get_date_created(self):
        return self.json.get(self.parser.get('date_created'))

    def get_is_group(self):
        if self.is_profile:
            return False
        return self.json.get(self.parser.get('is_group'))

    def get_is_active(self):
        if self.is_profile:
            return False
        return self.json.get(self.parser.get('is_active'))


user_json_format = {
    'user_id': 'id',
    'username': 'username',
    'first_name': 'first_name',
    'last_name': 'last_name',
    'full_name': 'display_name',
    'phone': 'phone',
    'picture_url': 'profile_picture_url',
    'about': 'about',
    'date_created': 'date_joined',
    'is_group': 'is_group',
    'is_active': 'is_active'
}

profile_json_format = {
    'user_id': 'external_id',
    'username': 'username',
    'first_name': 'firstname',
    'last_name': 'lastname',
    'full_name': 'name',
    'phone': 'phone',
    'picture_url': 'picture',
    'about': 'about',
    'date_created': 'date_created',
    'is_business': 'is_business'
}


class PaymentMethodParser:

    def __init__(self, json):
        self.json = json

    def get_id(self):
        return self.json.get(payment_method_json_format['id'])

    def get_payment_method_role(self):
        return self.json.get(payment_method_json_format['payment_role'])

    def get_payment_method_name(self):
        return self.json.get(payment_method_json_format['name'])

    def get_payment_method_type(self):
        return self.json.get(payment_method_json_format['type'])


payment_method_json_format = {'id': 'id',
                              'payment_role': 'peer_payment_role',
                              'name': 'name',
                              'type': 'type'
                              }


class PaymentParser:

    def __init__(self, json):
        self.json = json

    def get_id(self):
        return self.json.get(payment_request_json_format['id'])

    def get_actor(self):
        return self.json.get(payment_request_json_format['actor'])

    def get_target(self):
        return self.json.get(payment_request_json_format['target']) \
            .get(payment_request_json_format['target_user'])

    def get_action(self):
        return self.json.get(payment_request_json_format['action'])

    def get_amount(self):
        return self.json.get(payment_request_json_format['amount'])

    def get_audience(self):
        return self.json.get(payment_request_json_format['audience'])

    def get_date_authorized(self):
        return self.json.get(payment_request_json_format['date_authorized'])

    def get_date_completed(self):
        return self.json.get(payment_request_json_format['date_completed'])

    def get_date_created(self):
        return self.json.get(payment_request_json_format['date_created'])

    def get_date_reminded(self):
        return self.json.get(payment_request_json_format['date_reminded'])

    def get_note(self):
        return self.json.get(payment_request_json_format['note'])

    def get_status(self):
        return self.json.get(payment_request_json_format['status'])


payment_request_json_format = {
    'id': 'id',
    'actor': 'actor',
    'target': 'target',
    'target_user': 'user',
    'action': 'action',
    'amount': 'amount',
    'audience': 'audience',
    'date_authorized': 'date_authorized',
    'date_completed': 'date_completed',
    'date_created': 'date_created',
    'date_reminded': 'date_reminded',
    'note': 'note',
    'status': 'status'
}


class CommentParser:

    def __init__(self, json):
        self.json = json

    def get_date_created(self):
        return self.json.get(comment_json_format['date_created'])

    def get_message(self):
        return self.json.get(comment_json_format['message'])

    def get_mentions(self):
        mentions = self.json.get(comment_json_format['mentions'])
        return mentions.get(comment_json_format['mentions_list']) if mentions else mentions

    def get_id(self):
        return self.json.get(comment_json_format['id'])

    def get_user(self):
        return self.json.get(comment_json_format['user'])


comment_json_format = {
    "date_created": "date_created",
    "message": "message",
    "message_list": "data",
    "mentions": "mentions",
    "mentions_list": "data",
    "id": "id",
    "user": "user"
}


class MentionParser:

    def __init__(self, json):
        self.json = json

    def get_username(self):
        return self.json.get(mention_json_format['username'])

    def get_user(self):
        return self.json.get(mention_json_format['user'])


mention_json_format = {
    "username": "username",
    "user": "user"
}
