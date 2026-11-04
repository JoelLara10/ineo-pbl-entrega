import xml.etree.ElementTree as ET
from ci.sprint10_coverage import changed_lines, measure

DIFF = '+++ b/backend/api_hospital/app.py\n@@ -1 +1,2 @@\n'


def test_rejects_under_80_percent():
    xml = ET.fromstring('<coverage><class filename="app.py"><lines><line number="1" hits="1"/><line number="2" hits="0"/></lines></class></coverage>')
    result = measure(DIFF, xml)
    assert result['percent'] == 50 and not result['passed']


def test_accepts_covered_executable_lines_without_counting_comments():
    xml = ET.fromstring('<coverage><class filename="app.py"><lines><line number="1" hits="2"/></lines></class></coverage>')
    assert measure(DIFF, xml)['passed']


def test_missing_changed_file_is_failure():
    assert not measure(DIFF, ET.fromstring('<coverage/>'))['passed']


def test_deleted_hunk_does_not_invent_added_lines():
    assert changed_lines('+++ b/x.py\n@@ -1,2 +1,0 @@\n')['x.py'] == set()
