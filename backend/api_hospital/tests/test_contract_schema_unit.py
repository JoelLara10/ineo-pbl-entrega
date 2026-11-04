"""PBL-30 UT: the versioned schema itself, without HTTP or engine execution."""
import pytest
from jsonschema import Draft202012Validator, ValidationError
from tests.test_spark_contract import CONTRACT, validate


def test_versioned_schema_is_well_formed():
    Draft202012Validator.check_schema(CONTRACT)


@pytest.mark.parametrize('value', [None, [], {'error': 1}, {}])
def test_error_schema_rejects_incompatible_values(value):
    with pytest.raises(ValidationError):
        validate('error', value)


def test_error_schema_accepts_text():
    validate('error', {'error': 'Error sintético'})
