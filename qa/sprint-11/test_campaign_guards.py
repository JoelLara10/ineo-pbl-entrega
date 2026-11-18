"""Prevent false-positive load reports and accidental reuse of old targets."""
import csv
from pathlib import Path
import sys
import xml.etree.ElementTree as E
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parent))
from performance import build, metrics

def test_jmx_targets_are_isolated_and_complete():
    build()
    for name in ('read.jmx','write.jmx'):
        root=E.parse(Path(__file__).with_name('jmeter')/name)
        samplers=root.findall('.//HTTPSamplerProxy')
        assert len(samplers)>=2
        for sampler in samplers:
            properties={n.attrib['name']:n.text for n in sampler.findall('stringProp')}
            assert properties['HTTPSampler.domain']=='127.0.0.1'
            assert properties['HTTPSampler.port']=='5110'
        assert '__env(' not in E.tostring(root.getroot(),encoding='unicode')

def test_empty_result_cannot_pass(tmp_path):
    path=tmp_path/'empty.jtl'
    path.write_text('timeStamp,elapsed,label,success,allThreads\n')
    with pytest.raises(AssertionError,match='No application samples'):metrics(path)

def test_login_is_excluded_and_failure_is_retained(tmp_path):
    path=tmp_path/'mixed.jtl'
    path.write_text('timeStamp,elapsed,label,success,allThreads\n0,9000,login,true,1\n10000,15,patients,true,2\n11000,3000,patients,false,2\n')
    report=metrics(path)
    assert report['samples']==2 and report['errors']==1
    assert report['error_rate']==.5 and report['p95_ms']==3000
    assert report['observed_threads']==2
