"""Send synthetic ESP32 data to QA using a provisioned device credential.
Never uses or seeds production patient records. Explicit QA URL and device required.
"""
import argparse
import json
import os
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from urllib.parse import urlsplit

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--api-url', required=True, help='QA API base including /api/v1')
parser.add_argument('--device-id', required=True)
parser.add_argument('--scenario', choices=['normal', 'fall', 'low-spo2', 'no-contact'], default='normal')
parser.add_argument('--event-id', help='Stable ID for retries of the same fall')
args = parser.parse_args()
if urlsplit(args.api_url).scheme not in ('http', 'https'):
    parser.error('La URL QA debe usar HTTP o HTTPS')
token = os.getenv('MONITORING_DEVICE_TOKEN')
if not token:
    parser.error('Set MONITORING_DEVICE_TOKEN to the one-time provisioning credential')
payload = {'device_id': args.device_id}
if args.scenario == 'fall':
    payload.update(type='fall', acceleration=3.5)
    if args.event_id:
        payload['event_id'] = args.event_id
else:
    payload.update(heart_rate=75, spo2=88 if args.scenario == 'low-spo2' else 98,
                   finger_detected=args.scenario != 'no-contact', movement=False,
                   fall=False, temperature=28.0, acceleration=1.0)
request = Request(args.api_url.rstrip('/') + '/monitoring/data',
                  data=json.dumps(payload).encode(), method='POST',
                  headers={'Content-Type': 'application/json', 'X-Device-Token': token})
try:
    with urlopen(request, timeout=20) as response:  # nosec B310
        result = json.load(response)
        print('Accepted:', response.status, 'alerts:', len(result['data']['alerts']))
except HTTPError as error:
    raise SystemExit(f'API rejected request: HTTP {error.code}')


