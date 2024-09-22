from venmo_api import BaseModel, JSONSchema


class Fee(BaseModel):
    def __init__(self, product_uri, applied_to, base_fee_amount, fee_percentage, calculated_fee_amount_in_cents,
                 fee_token, json=None):
        super().__init__()

        self.product_uri = product_uri
        self.applied_to = applied_to
        self.base_fee_amount = base_fee_amount
        self.fee_percentage = fee_percentage
        self.calculated_fee_amount_in_cents = calculated_fee_amount_in_cents
        self.fee_token = fee_token
        self._json = json

    @classmethod
    def from_json(cls, json):
        """
        Initialize a new Fee object from JSON using the FeeParser.
        :param json: JSON data to parse.
        :return: Fee object.
        """
        if not json:
            return None

        parser = JSONSchema.fee(json)

        return cls(
            product_uri=parser.get_product_uri(),
            applied_to=parser.get_applied_to(),
            base_fee_amount=parser.get_base_fee_amount(),
            fee_percentage=parser.get_fee_percentage(),
            calculated_fee_amount_in_cents=parser.get_calculated_fee_amount_in_cents(),
            fee_token=parser.get_fee_token(),
            json=json
        )
