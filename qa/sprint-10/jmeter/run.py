"""Run smoke/baseline and a separate expected failing gate against local QA."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--home', required=True)
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    home, out = Path(args.home).resolve(), Path(args.out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    java = os.getenv('JAVA_EXE', 'java')
    metadata = {'tested_sha': subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        'started_utc':datetime.now(timezone.utc).isoformat(),
        'executor':'Marcelino Zahid Galicia Bonifacio',
        'approved_thresholds':{'p95_ms':2000,'max_error_rate':.01}, 'runs':[]}
    for name, users, ramp, duration in [('smoke',1,1,60),('baseline',5,30,210),('negative',1,1,15)]:
        target=out/name
        target.mkdir()
        options=['-Jusers='+str(users),'-Jramp='+str(ramp),'-Jduration='+str(duration)]
        if name=='negative':options+=['-Jloops=1','-Jpause=0','-Jpath=/api/v1/nonexistent-negative-control']
        command=[java,'-Xms64m','-Xmx256m','-jar',str(home/'bin/ApacheJMeter.jar'),
            '-n','-t',str(Path(__file__).with_name('api.jmx')),'-l',str(target/'results.jtl'),
            '-j',str(target/'jmeter.log'),'-e','-o',str(target/'html'),
            '-Jjmeter.save.saveservice.output_format=csv',
            '-Jjmeter.save.saveservice.response_data=false',
            '-Jjmeter.save.saveservice.response_data.on_error=false',
            '-Jjmeter.save.saveservice.samplerData=false',
            '-Jjmeter.save.saveservice.requestHeaders=false',
            '-Jjmeter.save.saveservice.responseHeaders=false',*options]
        print('Starting',name,flush=True)
        result=subprocess.run(command,cwd=home/'bin',capture_output=True,text=True,encoding='utf8',errors='replace')
        (target/'execution.txt').write_text((result.stdout+result.stderr).replace(str(ROOT),'[repo]'),encoding='utf8')
        if result.returncode:raise RuntimeError(name+' JMeter failed')
        gate=subprocess.run([sys.executable,str(Path(__file__).with_name('evaluate.py')),
            str(target/'results.jtl'),'--out',str(target/'metrics.json')],capture_output=True,text=True)
        (target/'gate.txt').write_text(gate.stdout+gate.stderr,encoding='utf8')
        expected=1 if name=='negative' else 0
        metadata['runs'].append({'name':name,'users':users,'ramp_seconds':ramp,'duration_seconds':duration,
            'jmeter_exit':result.returncode,'gate_exit':gate.returncode,'expected_gate_exit':expected})
        (out/'campaign.json').write_text(json.dumps(metadata,indent=2),encoding='utf8')
        print(name,'JMeter exit',result.returncode,'gate exit',gate.returncode,flush=True)
        if gate.returncode!=expected:raise RuntimeError(name+' gate did not match expected outcome')


if __name__=='__main__':main()
