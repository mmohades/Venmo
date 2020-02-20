
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


class TransactionParser:

    def __init__(self, json):
        self.json = json
        self.payment = json[transaction_json_format['payment']]

    def get_story_id(self):
        return self.json[transaction_json_format['story_id']]

    def get_date_created(self):
        return self.json[transaction_json_format['date_created']]

    def get_date_updated(self):
        return self.json[transaction_json_format['date_updated']]

    def get_actor_app(self):
        return self.json[transaction_json_format['app']]

    def get_audience(self):
        return self.json[transaction_json_format['aud']]

    def get_likes(self):
        return self.json[transaction_json_format['likes']]

    def get_comments(self):
        return self.json[transaction_json_format['comments']]

    def get_payment_id(self):
        return self.payment[payment_json_format['payment_id']]

    def get_type(self):
        return self.payment[payment_json_format['type']]

    def get_date_completed(self):
        return self.payment[payment_json_format['date_completed']]

    def get_story_note(self):
        return self.payment[payment_json_format['note']]

    def get_actor(self):
        return self.payment[payment_json_format['actor']]

    def get_target(self):
        return self.payment[payment_json_format['target']]['user']

    def get_status(self):
        return self.payment[payment_json_format['status']]


transaction_json_format = {
    "story_id": "id",
    "date_created": "date_created",
    "date_updated": "date_updated",
    "aud": "audience",
    "note": "note",
    "app": "app",
    "payment": "payment",
    "comments": "comments",
    "likes": "likes"
}
payment_json_format = {
    "status": "status",
    "payment_id": "id",
    "date_completed": "date_completed",
    "target": "target",
    "actor": "actor",
    "note": "note",
    'type': 'action'
}


class UserParser:

    def __init__(self, json, is_profile=False):
        self.json = json
        self.is_profile = is_profile

        if is_profile:
            self.parser = profile_json_format
        else:
            self.parser = user_json_format

    def get_user_id(self):
        return self.json[self.parser.get('user_id')]

    def get_username(self):
        return self.json[self.parser.get('username')]

    def get_first_name(self):
        return self.json[self.parser.get('first_name')]

    def get_last_name(self):
        return self.json[self.parser.get('last_name')]

    def get_full_name(self):
        return self.json[self.parser.get('full_name')]

    def get_picture_url(self):
        return self.json[self.parser.get('picture_url')]

    def get_about(self):
        return self.json[self.parser.get('about')]

    def get_date_created(self):
        return self.json[self.parser.get('date_created')]

    def get_is_group(self):
        if self.is_profile:
            return False
        return self.json[self.parser.get('is_group')]

    def get_is_active(self):
        if self.is_profile:
            return False
        return self.json[self.parser.get('is_active')]


user_json_format = {
    'user_id': 'id',
    'username': 'username',
    'first_name': 'first_name',
    'last_name': 'last_name',
    'full_name': 'display_name',
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
