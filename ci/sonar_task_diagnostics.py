"""Report a failed Sonar compute task without changing its acceptance gate."""
import json
import os
from pathlib import Path
from urllib.parse import urlsplit
import requests


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
    metadata = Path('backend/api_hospital/.scannerwork/report-task.txt')
    if not metadata.is_file():
        print('No Sonar compute-task metadata; inspect the original failed step.')
        return
    props = dict(line.split('=', 1) for line in metadata.read_text().splitlines() if '=' in line)
    host = os.environ['SONAR_HOST_URL']
    credential = os.environ['SONAR_TOKEN']
    target = trusted_task_url(host, props['ceTaskUrl'])
    response = requests.get(target, headers={'Authorization': 'Bearer ' + credential},
                            timeout=30, allow_redirects=False)
    response.raise_for_status()
    task = response.json()['task']
    detail = {name: task.get(name) for name in ('status', 'errorMessage', 'warningCount')}
    output = json.dumps(detail, ensure_ascii=True).replace(credential, '[redacted]').replace(host, '[Sonar server]')
    print('Sonar compute-task diagnostic: ' + output[:3000])


if __name__ == '__main__':
    main()
