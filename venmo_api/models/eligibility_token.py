from venmo_api import BaseModel, JSONSchema
from venmo_api.models.fee import Fee


class EligibilityToken(BaseModel):
    def __init__(self, eligibility_token, eligible, fees, fee_disclaimer, json=None):
        super().__init__()

        self.eligibility_token = eligibility_token
        self.eligible = eligible
        self.fees = fees
        self.fee_disclaimer = fee_disclaimer
        self._json = json

    @classmethod
    def from_json(cls, json):
        """
        Initialize a new eligibility token object from JSON.
        :param json: JSON data to parse.
        :return: EligibilityToken object.
        """
        if not json:
            return None

        parser = JSONSchema.eligibility_token(json)

        fees = parser.get_fees()
        fee_objects = [Fee.from_json(fee) for fee in fees] if fees else []

        return cls(
            eligibility_token=parser.get_eligibility_token(),
            eligible=parser.get_eligible(),
            fees=fee_objects,
            fee_disclaimer=parser.get_fee_disclaimer(),
            json=json
        )
