"""Verify/provision only the 13 pinned inputs from an authorised local pack.

No downloads, staging, credential copy, source modification or overwrite. This
does not grant redistribution rights; a remote teammate supplies a permitted copy.
Run without --source-root to verify existing inputs without any mutation.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import tempfile

ROOT = Path(__file__).resolve().parents[5]


def digest(path):
    result = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            result.update(block)
    return result.hexdigest()


def contained(base, relative):
    part = PurePosixPath(relative)
    if part.is_absolute() or '..' in part.parts or part.parts[0] not in ('raw', 'derived'):
        raise ValueError('invalid_manifest_path')
    path = base.joinpath(*part.parts)
    if path.is_symlink() or not path.resolve().is_relative_to(base):
        raise ValueError('input_must_be_contained_regular_file')
    return path


def provision(*, source_root=None, destination_root=None):
    manifest = json.loads((ROOT / 'docs/execution/parallel/source_snapshot.v1.json').read_text())
    destination = Path(destination_root or ROOT / 'ml/minder_ml_starter').resolve()
    if not destination.is_relative_to(ROOT):
        raise ValueError('destination_must_stay_in_current_worktree')
    source = Path(source_root).resolve() if source_root is not None else destination
    entries = manifest['source_files']
    if len(entries) != 13 or len({x['path'] for x in entries}) != 13:
        raise ValueError('unexpected_manifest_population')
    missing = []
    # Complete preflight before writing: unknown/mismatched existing inputs are
    # never replaced, and a partial/incorrect supplied pack never starts a copy.
    for entry in entries:
        src, dst = contained(source, entry['path']), contained(destination, entry['path'])
        if not src.is_file() or digest(src) != entry['sha256']:
            raise ValueError('source_missing_or_hash_mismatch')
        if dst.exists():
            if not dst.is_file() or digest(dst) != entry['sha256']:
                raise ValueError('existing_destination_hash_mismatch_no_overwrite')
            if dst.stat().st_mode & 0o222:
                raise ValueError('existing_destination_not_read_only')
        elif source_root is None:
            raise ValueError('missing_input_supply_authorised_source_root')
        else:
            missing.append((entry, src, dst))
    for entry, src, dst in missing:
        dst.parent.mkdir(parents=True, exist_ok=True)
        fd, temporary = tempfile.mkstemp(prefix='.input-copy-', dir=dst.parent)
        try:
            with os.fdopen(fd, 'wb') as output, src.open('rb') as stream:
                shutil.copyfileobj(stream, output)
            temp = Path(temporary)
            if digest(temp) != entry['sha256']:
                raise ValueError('source_changed_during_copy')
            temp.chmod(0o444)
            # Atomic no-clobber publication, unlike rename/replace. Destination
            # creation races fail instead of replacing somebody else's file.
            os.link(temp, dst, follow_symlinks=False)
        finally:
            Path(temporary).unlink(missing_ok=True)
    return dict(snapshot_id=manifest['snapshot_id'], input_count=13,
                copied=len(missing), preserved_existing=13-len(missing),
                all_hashes_verified=True, all_destinations_read_only=True,
                public_download_or_upload=False, git_staging=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-root', type=Path,
                        help='Authorised existing raw/derived pack root; omit for read-only verification')
    parser.add_argument('--destination-root', type=Path,
                        help='Defaults to current worktree ml/minder_ml_starter')
    args = parser.parse_args()
    try:
        print(json.dumps(provision(source_root=args.source_root, destination_root=args.destination_root)))
    except (ValueError, OSError) as error:
        # Fixed codes only; no file contents or private source path in output.
        code = str(error) if isinstance(error, ValueError) else 'input_access_or_copy_failed'
        print(json.dumps(dict(status='failed', code=code)))
        raise SystemExit(1)


if __name__ == '__main__':
    main()
