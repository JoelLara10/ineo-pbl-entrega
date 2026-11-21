"""Real Terraform/Docker reconstruction, out-of-band drift and state isolation."""
import argparse
import json
import os
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import ROOT, OUT, record, run

BASE = Path(__file__).resolve().parent

def tf(label, command, side='a', expected=(0,)):
    env = dict(os.environ, TF_DATA_DIR=str(ROOT.parent / 'tf-s11' / side / 'data'))
    state = ROOT.parent / 'tf-s11' / side / 'terraform.tfstate'
    state.parent.mkdir(parents=True, exist_ok=True)
    args = ['terraform', '-chdir='+str(BASE), *command]
    if command[0] in ('plan','apply','destroy'):
        args += ['-input=false', '-no-color', '-state='+str(state)]
        if not any(x.startswith('-var=environment_name=') for x in command):
            args += ['-var=environment_name=ineo-test-s11-qa-'+side]
        args += ['-var=mongo_port='+('27111' if side=='a' else '27112')]
    if command[0]=='state': args += ['-state='+str(state)]
    return run(label,args,expected=expected,env=env)

def main():
    p=argparse.ArgumentParser();p.add_argument('--cleanup',action='store_true');args=p.parse_args()
    if args.cleanup:
        for side in ('b','a'): tf('cleanup-'+side,['destroy','-auto-approve'],side)
        return
    current='CP-S11-IAC-01'
    try:
        run('docker-version',['docker','version'])
        run('terraform-version',['terraform','version','-no-color'])
        run('terraform-fmt',['terraform','-chdir='+str(BASE),'fmt','-check','-recursive'])
        for side in ('a','b'):
            tf('init-'+side,['init','-input=false','-no-color'],side)
            tf('validate-'+side,['validate','-no-color'],side)
        tf('invalid-name',['plan','-var=environment_name=production'],expected=(1,))
        tf('create-plan-a',['plan'])
        tf('create-a',['apply','-auto-approve'])
        tf('idempotency-a',['plan','-detailed-exitcode'])
        run('mongo-smoke-a',['docker','exec','ineo-test-s11-qa-a','mongosh','--quiet','--eval',"JSON.stringify(db.adminCommand('ping'))"])
        record(current,'Reconstrucción desde cero',[
            ['Inicializar y validar','Proveedor y configuración válidos','init y validate exit 0'],
            ['Crear QA desde módulos','MongoDB real disponible','apply exit 0; mongosh ping ok'],
            ['Repetir plan','Sin cambios','plan -detailed-exitcode exit 0']],
            detail='logs/create-a.txt; logs/mongo-smoke-a.txt; logs/idempotency-a.txt')
        current='CP-S11-IAC-02'
        run('introduce-drift',['docker','rename','ineo-test-s11-qa-a','ineo-test-s11-qa-a-drift'])
        drift=tf('detect-drift',['plan','-detailed-exitcode'],expected=(2,))
        assert 'ineo-test-s11-qa-a-drift' in drift.stdout
        assert 'docker_container.mongo' in drift.stdout
        record(current,'Deriva controlada',[
            ['Cambiar nombre fuera de Terraform','Cambio real en Docker','docker rename exit 0'],
            ['Generar plan','Detectar deriva del contenedor','exit 2; nombre alterado observado']],
            detail='logs/introduce-drift.txt; logs/detect-drift.txt')
        current='CP-S11-IAC-04'
        tf('restore-a',['apply','-auto-approve'])
        tf('restored-plan-a',['plan','-detailed-exitcode'])
        record(current,'Restauración de configuración',[
            ['Reaplicar configuración','Recuperar nombre versionado','apply exit 0'],
            ['Plan final','Sin cambios','plan exit 0']],detail='logs/restore-a.txt; logs/restored-plan-a.txt')
        current='CP-S11-IAC-03'
        tf('create-b',['apply','-auto-approve'],'b')
        containers=[]
        for side in ('a','b'):
            raw=run('inspect-'+side,['docker','inspect','--format',
                '{{json .}}','ineo-test-s11-qa-'+side]).stdout
            value=json.loads(raw)
            containers.append(value)
            tf('isolated-plan-'+side,['plan','-detailed-exitcode'],side)
        assert containers[0]['Id'] != containers[1]['Id']
        assert containers[0]['Mounts'][0]['Name'] != containers[1]['Mounts'][0]['Name']
        assert containers[0]['NetworkSettings']['Ports']['27017/tcp'] != containers[1]['NetworkSettings']['Ports']['27017/tcp']
        states=[json.loads((ROOT.parent/'tf-s11'/side/'terraform.tfstate').read_text(encoding='utf-8')) for side in ('a','b')]
        assert states[0]['lineage'] != states[1]['lineage']
        for side,state,container in zip(('a','b'),states,containers):
            resources=[r for r in state['resources'] if r['type']=='docker_container']
            assert len(resources)==1 and resources[0]['instances'][0]['attributes']['id']==container['Id']
        (OUT/'state-isolation.json').write_text(json.dumps(dict(
            independent_lineages=True,matching_container_ids=True,independent_volumes=True,
            loopback_ports=[27111,27112],shared_dependency='Immutable MongoDB image only'),indent=2),encoding='utf-8')
        record(current,'Aislamiento de estado',[
            ['Crear qa-a y qa-b','Estados distintos','Archivos de estado y TF_DATA_DIR independientes'],
            ['Comparar contenedores y volúmenes','Identificadores distintos','Aserciones de IDs y volúmenes aprobadas'],
            ['Comparar puertos','27111 y 27112 en loopback','Puertos independientes; planes exit 0']],
            detail='La imagen MongoDB es una dependencia inmutable compartida de lectura; contenedores, volúmenes y estados son exclusivos. logs/inspect-a.txt; logs/inspect-b.txt')
    except Exception as exc:
        record(current,current,[],status='Fallido',detail=str(exc));raise

if __name__=='__main__':main()
