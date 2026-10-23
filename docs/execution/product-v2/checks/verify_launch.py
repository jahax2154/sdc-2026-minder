"""Check an unreleased local lane; never stop an existing server or call a provider."""
import argparse
import json
import os
from pathlib import Path
import socket
import subprocess
import time
import urllib.error
import urllib.request


def get(url):
    try:
        with urllib.request.urlopen(url, timeout=2) as response:
            return response.status, response.read()
    except urllib.error.HTTPError as error:
        return error.code, error.read()


def verify(root, lane):
    root = Path(root).resolve()
    manifest = json.loads((root / 'docs/execution/product-v2/OWNERSHIP.json').read_text())
    item = manifest['lanes'][lane]
    for relative in ('AGENTS.md', 'docs/Minder_Three_Hour_Prototype_Launch.md',
                     'docs/Minder_Profile_Explore_Parallel_Execution_Pack_v1/README.md',
                     'docs/minder-ui-html-previews/README.md',
                     'docs/execution/product-v2/OWNERSHIP.json',
                     'docs/execution/product-v2/CONTRACTS.md',
                     'contracts/parallel-services.v1.schema.json'):
        assert (root / relative).is_file(), relative
    branch = subprocess.check_output(['git', '--no-optional-locks', 'branch', '--show-current'], cwd=root, text=True).strip()
    assert branch == item['branch'], branch
    assert not subprocess.check_output(['git', '--no-optional-locks', 'diff', '--name-only', 'HEAD'], cwd=root).strip()
    # Refuse to interfere with already running services. Only terminate our child.
    for port in (item['api_port'], item['ui_port']):
        with socket.socket() as probe:
            probe.bind(('127.0.0.1', port))
    command = 'source .env.local; exec "$MINDER_PYTHON" -m minder_ml.intelligence.product_runtime --lane ' + lane
    process = subprocess.Popen(['/bin/zsh', '-c', command], cwd=root,
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        api = 'http://127.0.0.1:' + str(item['api_port'])
        ui = 'http://127.0.0.1:' + str(item['ui_port'])
        deadline = time.monotonic() + 25
        while True:
            if process.poll() is not None:
                raise RuntimeError('owned_runtime_exited_' + str(process.returncode))
            try:
                health_status, health = get(api + '/api/health')
                break
            except (OSError, urllib.error.URLError):
                if time.monotonic() > deadline:
                    raise RuntimeError('owned_runtime_start_timeout')
                time.sleep(.15)
        assert health_status == 200
        assert json.loads(health)['status'] == 'ok'
        protected, _ = get(api + '/api/product/capabilities')
        ui_health, _ = get(ui + '/api/health')
        frontend, _ = get(ui + '/')
        assert protected == 401
        assert ui_health == 200
        assert frontend == 503  # F has not implemented the product root at bootstrap.
        return dict(lane=lane, directory=str(root), branch=branch,
                    sha=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip(),
                    api_port=item['api_port'], ui_port=item['ui_port'],
                    api_health=health_status, same_origin_health=ui_health,
                    private_route_without_token=protected, frontend_not_yet_implemented=frontend,
                    provider_requests=0, deployment=False)
    finally:
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()  # Only the exact test child created above.
                process.wait(timeout=5)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', required=True)
    parser.add_argument('--lane', required=True, choices=('D', 'E', 'F'))
    args = parser.parse_args()
    print(json.dumps(verify(args.root, args.lane), indent=2))
