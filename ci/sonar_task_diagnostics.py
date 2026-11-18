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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--task-id')
    args = parser.parse_args()
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
