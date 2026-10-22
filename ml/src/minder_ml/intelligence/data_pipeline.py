"""Immutable DOSM source parsing, cell round-trip checks and deterministic snapshots."""

from calendar import monthrange
from datetime import date
import csv
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import xml.etree.ElementTree as ET
import zipfile

from .data_schemas import ROOT, VERSION, SCHEMA_PATH, validate_entity
from .market import build_market_views

PACK = ROOT / "ml/minder_ml_starter"
SNAPSHOTS = ROOT / "ml/data/snapshots"
PIPELINE_VERSION = "dosm-quarterly-cells-v1.1"
REFERENCES = [
    "https://www.dosm.gov.my/portal-main/release-content/big-data-analytics-job-market-insights-q22026",
    "https://www.oecd.org/en/publications/how-well-do-online-job-postings-match-national-sources-in-large-english-speaking-countries_c17cae09-en.html",
    "https://esco.ec.europa.eu/en/use-esco/download"]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def encoded(value):
    return json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False, allow_nan=False) + "\n"


def read_workbook(path):
    ns = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    with zipfile.ZipFile(path) as archive:
        strings = []
        if "xl/sharedStrings.xml" in archive.namelist():
            for si in ET.fromstring(archive.read("xl/sharedStrings.xml")):
                strings.append("".join(node.text or "" for node in si.iter() if node.tag.endswith("}t")))
        rels = {r.attrib["Id"]: r.attrib["Target"] for r in ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))}
        workbook = ET.fromstring(archive.read("xl/workbook.xml"))
        sheets = {}
        for sheet in workbook.findall("m:sheets/m:sheet", ns):
            target = rels[sheet.attrib["{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"]]
            member = target.lstrip("/") if target.startswith("/") else str(PurePosixPath("xl") / target)
            cells = {}
            for cell in ET.fromstring(archive.read(member)).findall(".//m:sheetData/m:row/m:c", ns):
                value = cell.find("m:v", ns)
                text = value.text if value is not None else None
                if cell.get("t") == "s" and text is not None:
                    text = strings[int(text)]
                elif cell.get("t") == "inlineStr":
                    text = "".join(n.text or "" for n in cell.findall(".//m:t", ns))
                cells[cell.attrib["r"]] = text
            sheets[sheet.attrib["name"]] = cells
        return sheets


def inspect_pack(pack=PACK):
    pack = Path(pack)
    manifest_path = pack / "sources_manifest.json"
    manifest = json.loads(manifest_path.read_text())
    derived = next(s for s in manifest["derived_files"] if s["id"] == "dosm_jmi_quarterly_long")
    source = next(s for s in manifest["sources"] if s["id"] == derived["source_id"])
    checked = []
    for record in (source, derived):
        path = (pack / record["relative_path"]).resolve()
        if not path.is_relative_to(pack.resolve()):
            raise ValueError("source path escapes source pack")
        checksum = sha(path)
        if checksum != record["sha256"]:
            raise ValueError("source checksum mismatch: " + record["relative_path"])
        checked.append({"relative_path": record["relative_path"], "sha256": checksum})
    return {"source": source, "derived": derived, "checksums": checked,
            "manifest_sha256": sha(manifest_path), "schema_sha256": sha(SCHEMA_PATH), "references": REFERENCES}


def _col_number(text):
    result = 0
    for char in text:
        result = result * 26 + ord(char) - 64
    return result


def parse_dosm(pack=PACK):
    pack = Path(pack)
    provenance = inspect_pack(pack)
    source, derived = provenance["source"], provenance["derived"]
    sheets = read_workbook(pack / source["relative_path"])
    with (pack / derived["relative_path"]).open(newline="") as stream:
        raw_rows = list(csv.DictReader(stream))
    accepted, rejected, seen = [], [], set()
    for row_number, row in enumerate(raw_rows, 2):
        try:
            if row["dimension"] not in ("economic_activity", "occupation_major_group") or row["geography"] != "Malaysia":
                raise ValueError("unsupported source dimension/geography")
            if row["source_id"] != source["id"] or row["file_release_date"] != source["documented_publication_date"]:
                raise ValueError("source provenance mismatch")
            match = re.fullmatch(r"(\d{4})-Q([1-4])", row["period"])
            if not match:
                raise ValueError("not an observed quarterly record")
            year, quarter = map(int, match.groups())
            month = 3 * quarter - 2
            start, end = date(year, month, 1), date(year, month + 2, monthrange(year, month + 2)[1])
            if start.isoformat() != row["period_start"] or row["period"] > source["documented_as_of"]:
                raise ValueError("window or vintage mismatch")
            cells = sheets[row["source_sheet"]]
            ref = re.fullmatch(r"([A-Z]+)(\d+)", row["source_cell"])
            if not ref:
                raise ValueError("invalid source cell")
            column, line = ref.groups()
            if cells.get("B" + line) != row["group_label"] or cells.get(column + "4") != "Q" + str(quarter):
                raise ValueError("source label/quarter header mismatch")
            year_cells = [(_col_number(re.match(r"[A-Z]+", c).group()), v) for c, v in cells.items()
                          if re.fullmatch(r"[A-Z]+3", c) and v and re.fullmatch(r"20\d{2}", v)]
            header_year = max((item for item in year_cells if item[0] <= _col_number(column)), default=(0, None))[1]
            if header_year != str(year):
                raise ValueError("source year header mismatch")
            raw_value = cells.get(row["source_cell"])
            status = row["value_status"]
            if status == "observed":
                value = int(row["online_job_offerings"])
                if value < 0 or raw_value is None or float(raw_value) != value or float(row["source_raw_value"]) != value:
                    raise ValueError("numeric source cell round-trip failed")
            elif status in ("source_dash", "source_blank"):
                value = None
                if row["online_job_offerings"] or (status == "source_dash" and raw_value != "-") or (status == "source_blank" and raw_value not in (None, "")):
                    raise ValueError("missing source cell round-trip failed")
            else:
                raise ValueError("unrecognized source missingness status")
            identity = (row["dimension"], row["group_label"], row["period"])
            if identity in seen:
                raise ValueError("duplicate source series/window")
            seen.add(identity)
            occupation = row["dimension"] == "occupation_major_group"
            flags = ["classification_coverage_review"] if not occupation and row["period"] == "2026-Q2" else []
            record = {
                "schema_version": VERSION, "entity_type": "MarketObservation",
                "observation_id": hashlib.sha256((source["sha256"] + row["source_sheet"] + row["source_cell"]).encode()).hexdigest(),
                "source_id": source["id"], "source_version": source["sha256"], "indicator_id": "online_job_offerings",
                "value": value, "unit": row["unit"], "denominator": None,
                "geography_code": "MYS", "geography_level": "country", "region_code": None,
                "period_start": start.isoformat(), "period_end": end.isoformat(), "frequency": "quarterly",
                "available_at": row["file_release_date"], "published_at": row["file_release_date"], "retrieved_at": source["checked_at_utc"],
                "taxonomy_system": "DOSM JMI published occupation labels" if occupation else "DOSM JMI published economic activity labels",
                "taxonomy_version": None, "occupation_code": None, "occupation_label": row["group_label"] if occupation else None,
                "skill_id": None, "employer_id": None, "industry_id": None, "industry_label": None if occupation else row["group_label"],
                "dimension_scope": "occupation" if occupation else "industry", "group_kind": row["group_kind"],
                "population_coverage": "Published Malaysia online offerings; separate marginal tables, not all vacancies or hires",
                "source_coverage": "DOSM JMI release coverage; provider representativeness not independently verified",
                "measurement_method": "Published online job offering counts", "methodology_version": None,
                "measurement_kind": "observed", "data_quality_status": "missing" if value is None else "review_required" if flags else "valid",
                "quality_flags": flags, "source_record": {"sheet": row["source_sheet"], "cell": row["source_cell"], "raw_value": row["source_raw_value"] or None, "value_status": status}}
            validate_entity(record, "MarketObservation")
            accepted.append(record)
        except (ValueError, KeyError, TypeError) as exc:
            rejected.append({"csv_row": row_number, "reason": str(exc), "source_cell": row.get("source_cell")})
    accepted.sort(key=lambda r: (r["dimension_scope"], r["period_start"], r["occupation_label"] or r["industry_label"]))
    quality = {"input_rows": len(raw_rows), "validated_rows": len(accepted), "rejected_rows": len(rejected), "rejections": rejected,
               "observed_numeric_rows": sum(r["value"] is not None for r in accepted), "missing_rows": sum(r["value"] is None for r in accepted),
               "source_cell_round_trip_rows": len(accepted), "period_min": min((r["period_start"] for r in accepted), default=None),
               "period_max": max((r["period_end"] for r in accepted), default=None),
               "exceptions": source["caveats"] + ["Taxonomy and methodology versions are not supplied: comparability is restricted to the same release and published labels.", "Missing source dates/quarters are not interpolated; skill and employer dimensions remain null."],
               "flagged_classification_rows": sum(bool(r["quality_flags"]) for r in accepted)}
    coverage = []
    for period in ("2026-01-01", "2026-04-01"):
        unclassified = next((r for r in accepted if r["dimension_scope"] == "industry" and r["industry_label"] == "Unclassified" and r["period_start"] == period), None)
        total = next((r for r in accepted if r["dimension_scope"] == "industry" and r["group_kind"] == "overall" and r["period_start"] == period), None)
        if unclassified and total:
            coverage.append({"period_start": period, "unclassified_observed_count": unclassified["value"],
                             "published_total": total["value"], "unclassified_share": unclassified["value"] / total["value"]
                             if unclassified["value"] is not None and total["value"] is not None and total["value"] > 0 else None})
    quality["classification_coverage_diagnostic"] = {"observations": coverage, "status": "requires_review",
                                                    "interpretation": "Observed classification share shift; cause/methodological continuity not established. Industry YoY involving flagged quarter is withheld."}
    return accepted, quality, provenance


def prepare_snapshot(pack=PACK, output_root=SNAPSHOTS):
    rows, quality, provenance = parse_dosm(pack)
    if quality["rejected_rows"]:
        raise ValueError("source rejected rows: " + encoded(quality))
    manifest = {"pipeline_version": PIPELINE_VERSION, "schema_version": VERSION,
                "inputs": provenance["checksums"], "source_manifest_sha256": provenance["manifest_sha256"],
                "schema_sha256": provenance["schema_sha256"]}
    snapshot_id = hashlib.sha256(encoded(manifest).encode()).hexdigest()[:24]
    manifest["snapshot_id"] = snapshot_id
    files = {"observations.jsonl": "".join(json.dumps(r, sort_keys=True, allow_nan=False) + "\n" for r in rows),
             "quality.json": encoded(quality), "source_manifest.json": encoded(provenance),
             "views.json": encoded(build_market_views(rows))}
    manifest["output_sha256"] = {name: hashlib.sha256(text.encode()).hexdigest() for name, text in files.items()}
    files["snapshot.json"] = encoded(manifest)
    target = Path(output_root) / snapshot_id
    if target.exists():
        if any(not (target / name).is_file() or (target / name).read_text() != text for name, text in files.items()):
            raise ValueError("frozen snapshot mismatch; refusing overwrite")
        reused = True
    else:
        target.mkdir(parents=True, exist_ok=False)
        for name, text in files.items():
            with (target / name).open("x") as stream:
                stream.write(text)
        reused = False
    return {"snapshot_id": snapshot_id, "path": str(target), "reused_identical_snapshot": reused,
            "quality": quality, "output_sha256": manifest["output_sha256"]}
