import csv
import io
from dataclasses import dataclass

from app.graphql.pos.organization_alias.exceptions import InvalidCsvColumnsError

EXPECTED_COLUMNS = ["Organization Name", "Alias"]


@dataclass
class CsvRow:
    row_number: int
    organization_name: str
    alias: str


def parse_csv(content: bytes) -> list[CsvRow]:
    text = content.decode("utf-8")
    reader = csv.DictReader(io.StringIO(text))

    if reader.fieldnames is None:
        raise InvalidCsvColumnsError("CSV file is empty or has no headers")

    actual_columns = list(reader.fieldnames)
    if actual_columns != EXPECTED_COLUMNS:
        raise InvalidCsvColumnsError(
            f"Invalid columns. Expected {EXPECTED_COLUMNS}, got {actual_columns}"
        )

    rows: list[CsvRow] = []
    for row_number, row in enumerate(reader, start=2):
        rows.append(
            CsvRow(
                row_number=row_number,
                organization_name=row.get("Organization Name", "").strip(),
                alias=row.get("Alias", "").strip(),
            )
        )

    return rows
