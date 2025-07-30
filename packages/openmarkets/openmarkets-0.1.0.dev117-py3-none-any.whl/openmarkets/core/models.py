from pydantic import BaseModel, PositiveFloat, field_validator


class Symbol(BaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def name_must_be_uppercase(cls, value: str) -> str:
        if not value.isupper():
            raise ValueError("Symbol name must be uppercase")
        return value


class Price(BaseModel):
    symbol: Symbol
    value: PositiveFloat  # Ensures value is positive and a float
