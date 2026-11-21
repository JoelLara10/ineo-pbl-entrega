"""Report a failed Sonar compute task without changing its acceptance gate."""
import json
import os
import argparse
from pathlib import Path
from urllib.parse import urlsplit, urlencode
from urllib.request import Request, HTTPRedirectHandler, build_opener


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


def trusted_task_url(host, task_url):
    base = urlsplit(host)
    task = urlsplit(task_url)
    if (base.scheme != 'https' or task.scheme != 'https' or not base.hostname
            or task.username or task.password
            or (base.hostname, base.port) != (task.hostname, task.port)
            or task.path != '/api/ce/task'):
        raise ValueError('Task endpoint must belong to the configured HTTPS Sonar server')
    return task_url


def make_project_public(host, credential):
    """Explicit owner-authorized action, never invoked by PR analysis."""
    base = urlsplit(host)
    if base.scheme != 'https' or not base.hostname or base.username or base.password:
        raise ValueError('Sonar configuration must identify an HTTPS server without embedded credentials')
    opener = build_opener(NoRedirect())
    headers = {'Authorization': 'Bearer ' + credential}
    project = 'jaimediaz25'
    request = Request(host.rstrip('/') + '/api/projects/update_visibility',
        data=urlencode({'project': project, 'visibility': 'public'}).encode(),
        headers={**headers, 'Content-Type': 'application/x-www-form-urlencoded'}, method='POST')
    with opener.open(request, timeout=30) as response:
        response.read()
    request = Request(host.rstrip('/') + '/api/components/show?' + urlencode({'component': project}), headers=headers)
    with opener.open(request, timeout=30) as response:
        component = json.load(response)['component']
    if component.get('visibility') != 'public':
        raise RuntimeError('Sonar did not confirm public visibility')
    print('Confirmed Sonar project visibility: ' + json.dumps({'project': project, 'visibility': 'public'}))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--task-id')
    parser.add_argument('--make-project-public', action='store_true')
    args = parser.parse_args()
    if args.make_project_public:
        make_project_public(os.environ['SONAR_HOST_URL'], os.environ['SONAR_TOKEN'])
        return
    metadata = Path('backend/api_hospital/.scannerwork/report-task.txt')
    if not args.task_id and not metadata.is_file():
        print('No Sonar compute-task metadata; inspect the original failed step.')
        return
    host = os.environ['SONAR_HOST_URL']
    credential = os.environ['SONAR_TOKEN']
    if args.task_id:
        endpoint = host.rstrip('/') + '/api/ce/task?' + urlencode({'id': args.task_id})
    else:
        props = dict(line.split('=', 1) for line in metadata.read_text().splitlines() if '=' in line)
        endpoint = props['ceTaskUrl']
    target = trusted_task_url(host, endpoint)
    request = Request(target, headers={'Authorization': 'Bearer ' + credential})
    with build_opener(NoRedirect()).open(request, timeout=30) as response:
        task = json.load(response)['task']
    detail = {name: task.get(name) for name in ('status', 'errorMessage', 'warningCount')}
    output = json.dumps(detail, ensure_ascii=True).replace(credential, '[redacted]').replace(host, '[Sonar server]')
    print('Sonar compute-task diagnostic: ' + output[:3000])


if __name__ == '__main__':
    main()
