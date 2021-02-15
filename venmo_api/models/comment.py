from venmo_api import string_to_timestamp, BaseModel, User, Mention, JSONSchema


class Comment(BaseModel):

    def __init__(self, id_, message, date_created, mentions, user, json=None):
        """
        Comment model
        :param id_:
        :param message:
        :param date_created:
        :param mentions:
        :param user:
        :param json:
        """
        super().__init__()

        self.id = id_
        self.message = message
        self.user = user

        self.date_created = date_created

        self.mentions = mentions
        self._json = json

    @classmethod
    def from_json(cls, json):
        """
        Create a new Comment from the given json.
        :param json:
        :return:
        """

        if not json:
            return

        parser = JSONSchema.comment(json)

        mentions_list = parser.get_mentions()
        mentions = [Mention.from_json(mention) for mention in mentions_list] if mentions_list else []

        return cls(id_=parser.get_id(),
                   message=parser.get_message(),
                   date_created=string_to_timestamp(parser.get_date_created()),
                   mentions=mentions,
                   user=User.from_json(parser.get_user()),
                   json=json)
