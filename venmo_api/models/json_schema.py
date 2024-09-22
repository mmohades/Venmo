class JSONSchema:

    @staticmethod
    def transaction(json):
        return TransactionParser(json=json)

    @staticmethod
    def user(json, is_profile=None):
        return UserParser(json=json, is_profile=is_profile)

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

    @staticmethod
    def eligibility_token(json):
        return EligibilityTokenParser(json)

    @staticmethod
    def fee(json):
        return FeeParser(json)


class TransactionParser:

    def __init__(self, json):
        if not json:
            return

        self.json = json
        self.payment = json.get(transaction_json_format['payment'])

    def get_story_id(self):
        return self.json.get(transaction_json_format['story_id'])

    def get_date_created(self):
        return self.json.get(transaction_json_format['date_created'])

    def get_date_updated(self):
        return self.json.get(transaction_json_format['date_updated'])

    def get_actor_app(self):
        return self.json.get(transaction_json_format['app'])

    def get_audience(self):
        return self.json.get(transaction_json_format['aud'])

    def get_likes(self):
        return self.json.get(transaction_json_format['likes'])

    def get_comments(self):
        comments = self.json.get(transaction_json_format['comments'])
        return comments.get(transaction_json_format['comments_list']) if comments else comments

    def get_transaction_type(self):
        return self.json.get(transaction_json_format['transaction_type'])

    def get_payment_id(self):
        return self.payment.get(payment_json_format['payment_id'])

    def get_type(self):
        return self.payment.get(payment_json_format['type'])

    def get_date_completed(self):
        return self.payment.get(payment_json_format['date_completed'])

    def get_story_note(self):
        return self.payment.get(payment_json_format['note'])

    def get_actor(self):
        return self.payment.get(payment_json_format['actor'])

    def get_target(self):
        return self.payment.get(payment_json_format['target']).get('user')

    def get_status(self):
        return self.payment.get(payment_json_format['status'])

    def get_amount(self):
        return self.payment.get(payment_json_format['amount'])


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
    "transaction_type": "type"
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

class EligibilityTokenParser:
    def __init__(self, json):
        self.json = json

    def get_eligibility_token(self):
        return self.json.get(eligibility_token_json_format['eligibility_token'])

    def get_eligible(self):
        return self.json.get(eligibility_token_json_format['eligible'])

    def get_fees(self):
        return self.json.get(eligibility_token_json_format['fees'])

    def get_fee_disclaimer(self):
        return self.json.get(eligibility_token_json_format['fee_disclaimer'])

eligibility_token_json_format = {
    'eligibility_token': 'eligibility_token',
    'eligible': 'eligible',
    'fees': 'fees',
    'fee_disclaimer': 'fee_disclaimer'
}

class FeeParser:
    def __init__(self, json):
        self.json = json

    def get_product_uri(self):
        return self.json.get(fee_json_format['product_uri'])

    def get_applied_to(self):
        return self.json.get(fee_json_format['applied_to'])

    def get_base_fee_amount(self):
        return self.json.get(fee_json_format['base_fee_amount'])

    def get_fee_percentage(self):
        return self.json.get(fee_json_format['fee_percentage'])

    def get_calculated_fee_amount_in_cents(self):
        return self.json.get(fee_json_format['calculated_fee_amount_in_cents'])

    def get_fee_token(self):
        return self.json.get(fee_json_format['fee_token'])

fee_json_format = {
    'product_uri': 'product_uri',
    'applied_to': 'applied_to',
    'base_fee_amount': 'base_fee_amount',
    'fee_percentage': 'fee_percentage',
    'calculated_fee_amount_in_cents': 'calculated_fee_amount_in_cents',
    'fee_token': 'fee_token'
}