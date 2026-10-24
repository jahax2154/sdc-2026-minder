"""Package/verify only four licensed, hash-pinned O*NET runtime CSVs.

No crawler or new market collection. Other nine local inputs, held Galaxy data,
raw employer descriptions, user data and model weights are not exported here.
"""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import tarfile
import tempfile
from urllib.parse import urlsplit
from urllib.request import HTTPSHandler, HTTPRedirectHandler, build_opener, Request

ROOT = Path(__file__).resolve().parents[1]
SOURCE_IDS = {"onet_occupation_data", "onet_essential_skills", "onet_scales_reference", "onet_software_skills"}
ATTRIBUTION = ("O*NET 31.0 Database, U.S. Department of Labor, Employment and Training Administration, "
    "National Center for O*NET Development, https://www.onetcenter.org/database.html . "
    "CC BY 4.0, https://creativecommons.org/licenses/by/4.0/ . Original CSV bytes unchanged. "
    "Minder namespaces identifiers and projects occupational ratings into evidence; "
    "U.S. ratings are not Malaysian demand or individual competence.")


def inventory(*, root=ROOT, verify=False):
    base = root / "ml/minder_ml_starter"
    manifest = json.loads((base / "sources_manifest.json").read_text())
    selected = [dict(item) for item in manifest["sources"] if item["id"] in SOURCE_IDS]
    if {i["id"] for i in selected} != SOURCE_IDS or len(selected) != 4:
        raise ValueError("runtime_source_manifest_mismatch")
    for item in selected:
        part = PurePosixPath(item["relative_path"])
        if (part.is_absolute() or ".." in part.parts or part.parts[0] != "raw"
                or not item["license"].startswith("CC BY 4.0") or item["documented_version"] != "31.0"):
            raise ValueError("unapproved_runtime_source")
        if verify:
            path = base / part
            if path.is_symlink() or not path.resolve().is_relative_to(base.resolve()):
                raise ValueError("unsafe_runtime_source_path")
            if hashlib.sha256(path.read_bytes()).hexdigest() != item["sha256"]:
                raise ValueError("runtime_source_hash_mismatch")
    return dict(attribution=ATTRIBUTION, sources=selected)


def checked_url(url):
    part = urlsplit(url)
    if (part.scheme != "https" or part.hostname not in ("www.onetcenter.org", "onetcenter.org")
            or part.username or part.password or part.port not in (None, 443)):
        raise ValueError("runtime_source_target_rejected")
    return url


class PinnedRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return super().redirect_request(req, fp, code, msg, headers, checked_url(newurl))


def fetch(*, root=ROOT):
    data = inventory(root=root)
    opener = build_opener(HTTPSHandler(), PinnedRedirect())
    for item in data["sources"]:
        base = root / "ml/minder_ml_starter"
        path = base / item["relative_path"]
        if not path.resolve().is_relative_to(base.resolve()):
            raise ValueError("unsafe_runtime_source_path")
        if path.exists():
            if path.is_symlink() or hashlib.sha256(path.read_bytes()).hexdigest() != item["sha256"]:
                raise ValueError("existing_runtime_source_mismatch_no_overwrite")
            if path.stat().st_mode & 0o222:
                raise ValueError("existing_runtime_source_not_read_only")
            continue
        request = Request(checked_url(item["url"]), headers={"User-Agent": "MinderPinnedBuild/1.0"})
        with opener.open(request, timeout=30) as response:
            payload = response.read(8_000_001)
        if len(payload) > 8_000_000 or hashlib.sha256(payload).hexdigest() != item["sha256"]:
            raise ValueError("runtime_source_download_hash_mismatch")
        path.parent.mkdir(parents=True, exist_ok=True)
        # No clobber publication; the selected source bytes must remain exact.
        with path.open("xb") as handle:
            handle.write(payload)
        path.chmod(0o444)
    return inventory(root=root, verify=True)


def pack(output, *, root=ROOT):
    data = inventory(root=root, verify=True)
    if output.exists():
        raise ValueError("runtime_pack_exists_no_overwrite")
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as directory:
        notice = Path(directory) / "ATTRIBUTION.txt"
        notice.write_text(ATTRIBUTION + "\n")
        with tarfile.open(output, "x:gz") as archive:
            archive.add(notice, arcname="ATTRIBUTION.txt")
            for item in data["sources"]:
                archive.add(root / "ml/minder_ml_starter" / item["relative_path"],
                            arcname="ml/minder_ml_starter/" + item["relative_path"], recursive=False)
    return {"sha256": hashlib.sha256(output.read_bytes()).hexdigest(), "source_count": 4}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=("inventory", "verify", "fetch", "pack"))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.operation == "pack":
        if args.output is None:
            parser.error("pack requires --output")
        result = pack(args.output)
    elif args.operation == "fetch":
        result = fetch()
    else:
        result = inventory(verify=args.operation == "verify")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
