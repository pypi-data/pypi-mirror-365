from pydantic import BaseModel


class AddressSchema(BaseModel):
    """
    Schema to validate address inputs.
    """

    firstname: str
    lastname: str
    companyname: str
    address1: str
    postalcode: str
    city: str
    phone: str
    c_message: str
