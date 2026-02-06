import strawberry

from app.graphql.geography.models import Country, Subdivision


@strawberry.type
class CountryResponse:
    id: strawberry.ID
    name: str
    code: str

    @staticmethod
    def from_model(country: Country) -> "CountryResponse":
        return CountryResponse(
            id=strawberry.ID(str(country.id)),
            name=country.name,
            code=country.code,
        )


@strawberry.type
class SubdivisionResponse:
    id: strawberry.ID
    name: str
    iso_code: str
    country_id: strawberry.ID

    @staticmethod
    def from_model(subdivision: Subdivision) -> "SubdivisionResponse":
        return SubdivisionResponse(
            id=strawberry.ID(str(subdivision.id)),
            name=subdivision.name,
            iso_code=subdivision.iso_code,
            country_id=strawberry.ID(str(subdivision.country_id)),
        )

    @property
    def abbreviation(self) -> str:
        parts = self.iso_code.split("-")
        return parts[1] if len(parts) > 1 else self.iso_code
