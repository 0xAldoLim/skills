import json
from pathlib import Path
import pytest
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]


def test_schema_and_historical_accepted_records():
    schema = json.loads((ROOT / 'schemas/learning.schema.json').read_text(encoding='utf-8'))
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)
    for path in (ROOT / 'knowledge/accepted').glob('*.json'):
        assert not list(validator.iter_errors(json.loads(path.read_text(encoding='utf-8')))), path.name


@pytest.mark.parametrize('field,value', [('flag_verified', 'true'), ('understood', 'true'), ('variant_dimensions', ['2.39'])])
def test_schema_rejects_wrong_operational_field_types(field, value):
    schema = json.loads((ROOT / 'schemas/learning.schema.json').read_text(encoding='utf-8'))
    path = next((ROOT / 'knowledge/accepted').glob('*.json'))
    record = json.loads(path.read_text(encoding='utf-8'))
    record[field] = value
    assert list(Draft202012Validator(schema).iter_errors(record))
