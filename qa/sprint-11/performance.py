"""Build and run JMeter against isolated QA; verify writes in real MongoDB."""
import argparse
import csv
import importlib.util
import json
import math
import os
from pathlib import Path
import sys
import uuid
import xml.etree.ElementTree as E
import requests
from pymongo import MongoClient
from common import ROOT, OUT, run, record

BASE='http://127.0.0.1:5110'
HERE=Path(__file__).resolve().parent

def build():
    # Reuse the established JMeter XML structure, replacing the old fixed host,
    # unsupported environment function and insufficient HTTP assertions.
    spec=importlib.util.spec_from_file_location('s10_plan',ROOT/'qa/sprint-10/jmeter/build_plan.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    root=module.root
    for node in root.iter('stringProp'):
        if node.attrib.get('name')=='HTTPSampler.port':node.text='5110'
        if node.attrib.get('name')=='Argument.value' and '__env' in (node.text or ''):
            node.text='{"username":"admin.test","password":"Prueba-Sprint7!"}'
    # Only bounded patient/study reads; expensive Spark work is a different case.
    group_tree=root.find('.//ThreadGroup/../hashTree')
    # Find the tree directly paired with ThreadGroup.
    for parent in root.iter('hashTree'):
        children=list(parent)
        for i, child in enumerate(children):
            if child.tag=='ThreadGroup': group_tree=children[i+1]
    children=list(group_tree)
    for i in range(0,len(children)-1,2):
        child=children[i]
        if child.tag=='HTTPSamplerProxy':
            group_tree.remove(child);group_tree.remove(children[i+1])
    module.sampler(group_tree,'patients','/api/v1/patients',checks='assert data.groups instanceof List')
    # Property-driven peak groups: 5 users initially, another 15 after 30 s.
    thread=root.find('.//ThreadGroup')
    for node in thread.findall('stringProp'):
        if node.attrib.get('name')=='ThreadGroup.ramp_time':node.text='${__P(ramp,60)}'
    HERE.joinpath('jmeter').mkdir(exist_ok=True)
    E.indent(root);E.ElementTree(root).write(HERE/'jmeter/read.jmx',encoding='utf-8',xml_declaration=True)
    # Separate write plan: use unique run/thread/counter IDs and alternating patients.
    for node in list(group_tree):
        if node.tag=='HTTPSamplerProxy' and node.attrib.get('testname')=='patients':
            nodes=list(group_tree);index=nodes.index(node);group_tree.remove(nodes[index+1]);group_tree.remove(node)
    payload='{"ingresos_orales":100,"ingresos_iv":50,"egresos_orina":25,"egresos_drenajes":5,"observaciones":"${__P(run_id)}-${__threadNum}-${__counter(FALSE,write_counter)}"}'
    result_tree=module.sampler(group_tree,'fluid_balance','/api/v1/appointments/${__groovy((ctx.getThreadNum() % 2) + 1)}/fluid-balance','POST',payload,
                              'assert data.id_balance instanceof Number')
    for node in result_tree.iter('stringProp'):
        if node.attrib.get('name')=='script':node.text=node.text.replace("== '200'","== '201'")
    E.indent(root);E.ElementTree(root).write(HERE/'jmeter/write.jmx',encoding='utf-8',xml_declaration=True)

def metrics(path):
    with path.open(encoding='utf-8-sig') as f: rows=list(csv.DictReader(f))
    rows=[r for r in rows if r['label']!='login']
    if not rows:raise AssertionError('No application samples')
    times=sorted(float(r['elapsed']) for r in rows)
    return dict(samples=len(rows),errors=sum(r['success'].lower()!='true' for r in rows),
        error_rate=sum(r['success'].lower()!='true' for r in rows)/len(rows),
        p95_ms=times[math.ceil(.95*len(times))-1],
        observed_threads=max(int(r.get('allThreads',0)) for r in rows),
        application_seconds=(max(int(r['timeStamp'])+int(r['elapsed']) for r in rows)-min(int(r['timeStamp']) for r in rows))/1000)

def main():
    p=argparse.ArgumentParser();p.add_argument('--home',required=True)
    p.add_argument('--case',choices=['nominal','peak','writes','all'],default='all')
    p.add_argument('--accept-thresholds',action='store_true',help='Use only after team ratification')
    a=p.parse_args();build()
    out=OUT/'jmeter';out.mkdir(exist_ok=True)
    scenarios=[('nominal','CP-S11-PERF-01',10,60,360,'read.jmx'),
        ('peak','CP-S11-PERF-02',20,1,120,'read.jmx'),
        ('writes','CP-S11-PERF-03',10,10,60,'write.jmx')]
    # Peak: keep exactly 5 users for 30 s; start 15 additional users together
    # for the following 60 s. Same plan, separate thread groups and schedulers.
    plan=E.parse(HERE/'jmeter/read.jmx');root=plan.getroot()
    import copy
    for parent in root.iter('hashTree'):
        children=list(parent)
        for i,node in enumerate(children):
            if node.tag=='ThreadGroup':
                extra=copy.deepcopy(node);extra_tree=copy.deepcopy(children[i+1])
                for n in node.findall('stringProp'):
                    if n.attrib['name']=='ThreadGroup.num_threads':n.text='5'
                    if n.attrib['name']=='ThreadGroup.duration':n.text='120'
                for n in extra.findall('stringProp'):
                    if n.attrib['name']=='ThreadGroup.num_threads':n.text='15'
                    if n.attrib['name']=='ThreadGroup.duration':n.text='60'
                E.SubElement(extra,'stringProp',name='ThreadGroup.delay').text='30'
                parent.extend([extra,extra_tree]);break
        else:continue
        break
    plan.write(HERE/'jmeter/peak.jmx',encoding='utf-8',xml_declaration=True)
    for name,case,users,ramp,duration,filename in scenarios:
        if a.case not in ('all',name):continue
        if name=='peak':filename='peak.jmx'
        target=out/name;target.mkdir(exist_ok=True)
        if (target/'results.jtl').exists():raise RuntimeError('Preserve original run; choose a fresh evidence directory before rerun')
        run_id='S11-'+uuid.uuid4().hex[:10]
        command=['java','-Xms128m','-Xmx512m','-jar',str(Path(a.home)/'bin/ApacheJMeter.jar'),
            '-n','-t',str(HERE/'jmeter'/filename),'-l',str(target/'results.jtl'),
            '-j',str(target/'jmeter.log'),'-e','-o',str(target/'html'),
            '-Jusers='+str(users),'-Jramp='+str(ramp),'-Jduration='+str(duration),
            '-Jpause=1000','-Jrun_id='+run_id,
            '-Jjmeter.save.saveservice.output_format=csv',
            '-Jjmeter.save.saveservice.response_data=false',
            '-Jjmeter.save.saveservice.response_data.on_error=false',
            '-Jjmeter.save.saveservice.samplerData=false',
            '-Jjmeter.save.saveservice.requestHeaders=false',
            '-Jjmeter.save.saveservice.responseHeaders=false']
        try:
            run('jmeter-'+name,command,cwd=Path(a.home)/'bin')
            value=metrics(target/'results.jtl')
            passed=value['error_rate']<=.01 and value['p95_ms']<=2000
            value.update(run_id=run_id,thresholds=dict(p95_ms=2000,error_rate=.01),
                thresholds_ratified=a.accept_thresholds,observed_threshold_result=passed,
                users=users,ramp_seconds=ramp,scheduled_seconds=duration)
            if name=='writes':
                with MongoClient('mongodb://127.0.0.1:27111/') as mongo:
                    rows=list(mongo.ineo_test_s11.fluid_balance.find({'observaciones':{'$regex':'^'+run_id}}))
                accepted=value['samples']-value['errors']
                assert len(rows)==accepted>0,(len(rows),accepted)
                assert len({r['id_balance'] for r in rows})==len(rows)
                assert len({r['observaciones'] for r in rows})==len(rows)
                assert all(r['Id_exp']==r['id_atencion'] and r['balance_neto']==120 for r in rows)
                assert {r['Id_exp'] for r in rows}=={1,2}
                value['persistence']=dict(accepted=accepted,stored=len(rows),unique_ids=True,
                    patients=[1,2],expected_total_balance=accepted*120,
                    actual_total_balance=sum(r['balance_neto'] for r in rows))
            (target/'metrics.json').write_text(json.dumps(value,indent=2),encoding='utf-8')
            status='Aprobado' if passed and a.accept_thresholds else ('Pendiente de ratificación' if passed else 'Fallido')
            record(case,{'nominal':'Carga nominal API','peak':'Pico acotado','writes':'Concurrencia de escrituras'}[name],
                [['Ejecutar escenario JMX','Carga real y reporte original',json.dumps(value,ensure_ascii=False)],
                 ['Evaluar métricas','p95 ≤ 2000 ms; errores ≤ 1 %','Cumple' if passed else 'No cumple']],
                status=status,detail='Umbrales propuestos de Azure; ratificación humana pendiente.' if not a.accept_thresholds else None)
        except Exception as exc:
            record(case,name,[],status='Fallido',detail=str(exc));raise
if __name__=='__main__':main()
