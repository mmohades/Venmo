from venmo_api import string_to_timestamp, BaseModel
from venmo_api import JSONSchema


class User(BaseModel):

    def __init__(self, user_id, username, first_name, last_name, display_name, phone,
                profile_picture_url, about, date_joined, is_group, is_active):
        """
        Initialize a new user
        :param user_id:
        :param username:
        :param first_name:
        :param last_name:
        :param display_name:
        :param phone:
        :param profile_picture_url:
        :param about:
        :param date_joined:
        :param is_group:
        :param is_active:
        :return:
        """
        super().__init__()

        self.id = user_id
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.display_name = display_name
        self.phone = phone
        self.profile_picture_url = profile_picture_url
        self.about = about
        self.date_joined = date_joined
        self.is_group = is_group
        self.is_active = is_active

    @classmethod
    def from_json(cls, json, is_profile=False):
        """
        init a new user form JSON
        :param json:
        :param is_profile:
        :return:
        """
        if not json:
            return

        parser = JSONSchema.user(json, is_profile=is_profile)

        date_joined_timestamp = string_to_timestamp(parser.get_date_created())

        return cls(user_id=parser.get_user_id(),
                   username=parser.get_username(),
                   first_name=parser.get_first_name(),
                   last_name=parser.get_last_name(),
                   display_name=parser.get_full_name(),
                   phone=parser.get_phone(),
                   profile_picture_url=parser.get_picture_url(),
                   about=parser.get_about(),
                   date_joined=date_joined_timestamp,
                   is_group=parser.get_is_group(),
                   is_active=parser.get_is_active())
