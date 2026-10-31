"""Gate policy checks: a reviewed fixture cannot exempt a different secret/file."""
import importlib.util
from pathlib import Path
import pytest

spec = importlib.util.spec_from_file_location('security_review', Path(__file__).with_name('security_review.py'))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_unreviewed_secret_blocks_gate():
    scan = {'results': {'source.py': [{'type': 'Secret Keyword', 'hashed_secret': 'new-hash', 'line_number': 8}]}}
    assert module.secret_findings(scan, []) == [{'file': 'source.py', 'type': 'Secret Keyword', 'line': 8}]


def test_exception_is_scoped_to_file_type_and_value_on_both_platforms():
    reviewed = [{'file': 'tests/fixture.py', 'type': 'Secret Keyword', 'hashed_secret': 'reviewed-hash'}]
    scan = {'results': {
        'tests\\fixture.py': [{'type': 'Secret Keyword', 'hashed_secret': 'reviewed-hash', 'line_number': 2},
                              {'type': 'Secret Keyword', 'hashed_secret': 'changed-hash', 'line_number': 3}],
        'production.py': [{'type': 'Secret Keyword', 'hashed_secret': 'reviewed-hash', 'line_number': 4}],
    }}
    assert [x['line'] for x in module.secret_findings(scan, reviewed)] == [3, 4]


def test_exception_catalog_rejects_plaintext_or_additional_fields():
    with pytest.raises(ValueError):
        module.validate_reviewed([{'file': 'tests/demo.py', 'type': 'Secret Keyword',
                                  'hashed_secret': 'plaintext-is-not-a-digest', 'reason': 'fixture'}])
    with pytest.raises(ValueError):
        module.validate_reviewed([{'file': 'tests/demo.py', 'type': 'Secret Keyword',
                                  'hashed_secret': '0' * 40, 'reason': 'fixture', 'secret': 'not allowed'}])
