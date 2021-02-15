from venmo_api import BaseModel, User, JSONSchema


class Mention(BaseModel):

    def __init__(self, username, user, json=None):
        """
        Mention model
        :param username:
        :param user:
        """
        super().__init__()

        self.username = username
        self.user = user

        self._json = json

    @classmethod
    def from_json(cls, json):
        """
        Create a new Mention from the given json.
        :param json:
        :return:
        """

        if not json:
            return

        parser = JSONSchema.mention(json)

        return cls(username=parser.get_username(),
                   user=User.from_json(parser.get_user()),
                   json=json)
