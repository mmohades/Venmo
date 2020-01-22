from utils import string_to_timestamp
from models.user import User
from utils import get_phone_model_from_json


class Transaction(object):

    def __init__(self, story_id, payment_id, date_completed, date_created,
                 date_updated, payment_type, audience, status,
                 note, device_used, actor, target):

        super()

        self.id = story_id
        self.payment_id = payment_id

        self.date_completed = date_completed
        self.date_created = date_created
        self.date_updated = date_updated

        self.payment_type = payment_type
        self.audience = audience
        self.status = status

        self.note = note
        self.device_used = device_used

        self.actor = actor
        self.target = target

    @classmethod
    def from_json(cls, json):

        parser = TransactionParser(json)
        date_created = string_to_timestamp(parser.get_date_created())
        date_updated = string_to_timestamp(parser.get_date_updated())
        date_completed = string_to_timestamp(parser.get_date_completed())

        target = User.from_json(json=parser.get_target())
        actor = User.from_json(json=parser.get_actor())
        device_used = get_phone_model_from_json(parser.get_actor_app())

        return cls(story_id=parser.get_story_id(),
                   payment_id=parser.get_payment_id(),
                   date_completed=date_completed,
                   date_created=date_created,
                   date_updated=date_updated,
                   payment_type=parser.get_type(),
                   audience=parser.get_audience(),
                   status=parser.get_status(),
                   note=parser.get_story_note(),
                   device_used=device_used,
                   actor=actor,
                   target=target)

    def __str__(self):

        return f'story_id: {self.id}, payment_id: {self.payment_id}, date_completed: {self.date_completed},' \
            f'date_created: {self.date_created}, date_updated: {self.date_updated}, payment_type: {self.payment_type},' \
            f'audience: {self.audience}, status: {self.status}, note: {self.note}, device_used: {self.device_used},' \
            f'\nactor_user: {self.actor},\n' \
            f'target_user: {self.target}\n'


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
