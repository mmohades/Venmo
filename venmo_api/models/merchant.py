from venmo_api import string_to_timestamp, BaseModel, JSONSchema


class Merchant(BaseModel):

    def __init__(self, merchant_id, braintree_merchant_id, paypal_merchant_id, display_name, is_subscription, image_url, image_datetime_updated, datetime_updated, datetime_created, json=None):
        """
        Merchant model
        :param merchant_id:
        :param braintree_merchant_id:
        :param paypal_merchant_id:
        :param display_name:
        :param is_subscription:
        :param image_url:
        :param image_datetime_updated:
        :param datetime_updated
        :param datetime_created:
        :return:
        """
        super().__init__()

        self.id = merchant_id
        self.braintree_merchant_id = braintree_merchant_id
        self.paypal_merchant_id = paypal_merchant_id
        self.display_name = display_name
        self.is_subscription = is_subscription
        self.image_url = image_url
        self.image_datetime_updated = image_datetime_updated
        self.datetime_updated = datetime_updated
        self.datetime_created = datetime_created
        self._json = json

    @classmethod
    def from_json(cls, json):
        """
        init a new Merchant form JSON
        :param json:
        :return:
        """
        if not json:
            return

        parser = JSONSchema.merchant(json)

        date_updated_timestamp = string_to_timestamp(parser.get_datetime_created())
        date_created_timestamp = string_to_timestamp(parser.get_datetime_updated())

        return cls(merchant_id=parser.get_merchant_id(),
                   braintree_merchant_id=parser.get_braintree_merchant_id(),
                   paypal_merchant_id=parser.get_paypal_merchant_id(),
                   display_name=parser.get_display_name(),
                   is_subscription=parser.get_is_subscription(),
                   image_url=parser.get_image_url(),
                   image_datetime_updated=parser.get_image_datetime_updated(),
                   datetime_updated=date_updated_timestamp,
                   datetime_created=date_created_timestamp,
                   json=json)
