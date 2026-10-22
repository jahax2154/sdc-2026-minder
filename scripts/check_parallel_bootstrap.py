"""Read-only G0 launch verification. Never pushes, starts services or spends."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def git(directory, *args):
    return subprocess.check_output(['git', '-C', str(directory), *args], text=True).strip()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--expected-commit', required=True)
    args = parser.parse_args()
    manifest = json.loads((ROOT / 'docs/execution/parallel/ownership.v1.json').read_text())
    source_manifest = json.loads((ROOT / 'ml/minder_ml_starter/sources_manifest.json').read_text())
    sources = [e for e in source_manifest['sources'] + source_manifest['derived_files']
               if e.get('relative_path') and e.get('sha256')]
    results = []
    for session, lane in manifest['lanes'].items():
        directory = Path(lane['directory'])
        head = git(directory, 'rev-parse', 'HEAD')
        branch = git(directory, 'branch', '--show-current')
        assert head == args.expected_commit, (session, 'HEAD mismatch')
        assert branch == lane['branch'], (session, 'branch mismatch')
        for path in [manifest['canonical_context'], lane['prompt'],
                     'docs/execution/parallel/ownership.v1.json',
                     'docs/execution/parallel/G0.3.json',
                     'contracts/parallel-services.v1.schema.json']:
            assert (directory / path).is_file(), (session, path)
            assert (directory / path).read_bytes() == (ROOT / path).read_bytes(), (session, path)
        assert not git(directory, 'diff', '--name-only'), (session, 'unstaged tracked edits')
        assert not git(directory, 'diff', '--cached', '--name-only'), (session, 'staged edits')
        status = git(directory, 'status', '--porcelain=v1', '--untracked-files=all').splitlines()
        allowed = {'?? ml/minder_ml_starter/' + e['relative_path'] for e in sources}
        assert set(status) == allowed, (session, 'unexpected untracked state')
        for entry in sources:
            source = directory / 'ml/minder_ml_starter' / entry['relative_path']
            assert hashlib.sha256(source.read_bytes()).hexdigest() == entry['sha256']
            assert source.stat().st_mode & 0o222 == 0
        assert (directory / '.env.local').is_file(), (session, 'runtime reservations absent')
        results.append({'session': session, 'directory': str(directory), 'branch': branch,
                        'starting_commit': head, 'prompt': str(directory / lane['prompt']),
                        'tracked_clean': True, 'known_untracked_readonly_inputs': len(status),
                        'source_hashes': 'matched', 'launch_files': 'matched final checkpoint'})
    for field in ['directory', 'branch', 'api_port', 'ui_port']:
        assert len({lane[field] for lane in manifest['lanes'].values()}) == 3, field
    print(json.dumps({'parallel_launch': 'ready', 'sessions': results,
                      'push_status': 'not pushed — awaiting explicit instruction',
                      'service_activation': 'not claimed; this verifies bootstrap isolation only'}, indent=2))


if __name__ == '__main__':
    main()
