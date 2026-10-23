"""Pinned O*NET occupational catalogue for initial exploration, independent of plans.

Changes to the CC BY 4.0 O*NET 31.0 data: namespace IDs, project ratings into
Evidence DTOs, and withhold suppressed/not-relevant measures from requirements.
Original rows, flags, dates and descriptions remain available via reference().
US occupational ratings are neither Malaysian demand nor user proficiency.
"""
import copy
import csv
import hashlib
import json
import math
import re
from collections import Counter, defaultdict

from .policy import ROOT, fingerprint
from .catalogue_repair import read_source_facts

CATALOGUE_VERSION = 'onet31-anchored-reference-v3'
SOURCE_IDS = ('onet_occupation_data', 'onet_essential_skills',
              'onet_scales_reference', 'onet_software_skills')


class OccupationalCatalogue:
    """Read-only batch projection. No draft allowlist or milestone activation."""

    def __init__(self):
        base = ROOT / 'ml/minder_ml_starter'
        manifest = json.loads((base / 'sources_manifest.json').read_text())
        entries = {s['id']: s for s in manifest['sources']}
        tables, sources = {}, {}
        for sid in SOURCE_IDS:
            entry = entries[sid]
            path = (base / entry['relative_path']).resolve()
            if not path.is_relative_to(ROOT.resolve()):
                raise ValueError('source must stay in repository')
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            if digest != entry['sha256'] or entry['documented_version'] != '31.0':
                raise ValueError('pinned source/version mismatch: ' + sid)
            with path.open(encoding='utf-8-sig', newline='') as stream:
                tables[sid] = list(csv.DictReader(stream))
            sources[sid] = dict(source_id=sid, version='31.0', sha256=digest,
                                uri=entry['url'], geography='US',
                                available_at=entry['checked_at_utc'],
                                evidence_type='source-derived')
        facts = read_source_facts()
        relation = next(c for c in facts['captures'] if c['source_id'] == 'onet-version-relationship')
        if relation['facts']['database_version'] != '31.0':
            raise ValueError('taxonomy/database relationship mismatch')
        edition = relation['facts']['taxonomy_edition']
        scales = {r['Scale ID']: r for r in tables['onet_scales_reference']}
        skills, software = defaultdict(list), defaultdict(list)
        for line, row in enumerate(tables['onet_essential_skills'], 2):
            skills[row['O*NET-SOC Code']].append((line, row))
        for row in tables['onet_software_skills']:
            software[row['O*NET-SOC Code']].append(row)
        self._roles, self._references, self.rejected = {}, {}, []
        seen = Counter(r['O*NET-SOC Code'] for r in tables['onet_occupation_data'])
        for row in tables['onet_occupation_data']:
            code = row['O*NET-SOC Code']
            if (not re.fullmatch(r'\d{2}-\d{4}\.\d{2}', code)
                    or not row['Title'].strip() or seen[code] != 1):
                self.rejected.append({'source_id': 'onet_occupation_data', 'code': code,
                                      'reason': 'invalid_or_duplicate_occupation_identity'})
                continue
            rid = 'onet:' + code
            requirements, mappings = [], {}
            for line, measure in skills[code]:
                scale_id = measure['Scale ID']
                try:
                    value = float(measure['Data Value'])
                    scale = scales[scale_id]
                    valid = (scale_id in ('IM', 'LV') and math.isfinite(value)
                             and float(scale['Minimum']) <= value <= float(scale['Maximum'])
                             and measure['Title'] == row['Title'])
                except (ValueError, KeyError):
                    valid = False
                if not valid:
                    self.rejected.append({'source_id': 'onet_essential_skills', 'line': line,
                                          'code': code, 'reason': 'invalid_measure_or_scale'})
                    continue
                if measure['Recommend Suppress'] != 'N' or measure['Not Relevant'] not in ('', 'N'):
                    continue
                subject = 'onet:element:' + measure['Element ID']
                requirements.append(dict(
                    evidence_id=f'onet31:essential_skills:{line}', subject_id=subject,
                    value=value, unit='onet:' + scale_id, state='known',
                    provenance=sources['onet_essential_skills'],
                    method_id='onet-occupational-rating-not-user-rubric-v1'))
                mappings[subject] = dict(target_id=subject, source=sources['onet_essential_skills'],
                                         relation='native_skill_association', status='source_accepted')
            supported = any(r['unit'] == 'onet:LV' for r in requirements)
            missing = ['occupational_to_person_evidence_rubric_unavailable',
                       'source_grounded_industry_mappings_unavailable',
                       'interests_and_work_context_not_acquired']
            if not supported:
                missing.append('usable_occupational_skill_level_unavailable')
            role = dict(role_id=rid, taxonomy_id='O*NET-SOC', taxonomy_version=edition,
                        database_version='31.0', label=row['Title'],
                        source=sources['onet_occupation_data'],
                        eligibility='supported' if supported else 'partial',
                        industry_mappings=[], skill_mappings=list(mappings.values()),
                        requirements=requirements, missing_reasons=missing)
            reference = dict(occupation=row, essential_skills=[m for _, m in skills[code]],
                             software_examples=software[code], scales=list(scales.values()),
                             sources=list(sources.values()), taxonomy_evidence=relation,
                             tasks=[], interests=[], work_context=[],
                             unavailable_fields=['tasks', 'interests', 'work_context', 'industry_mappings'],
                             notice='US reference; software flags are not Malaysian demand or proficiency.')
            role['version'] = CATALOGUE_VERSION + ':' + fingerprint({'role': role, 'reference': reference})
            self._roles[rid], self._references[rid] = role, reference
        from .policy_sources import role_reference_v3
        extension = role_reference_v3()
        for rid, role in self._roles.items():
            role['industry_mappings'] = [dict(target_id=iid, source=extension['sources']['industries'],
                relation='US_2025_employment_presence_top_industries_not_MY_demand', status='source_accepted')
                for iid, _ in extension['industry_mappings'].get(rid, [])]
            role['work_style_mappings'] = [dict(target_id=sid, source=extension['sources']['work_styles'],
                relation='positive_work_style_impact_not_personal_competence', status='source_accepted')
                for sid, *_ in extension['work_style_mappings'].get(rid, [])]
            role['missing_reasons'] = [m for m in role['missing_reasons']
                if m != 'occupational_to_person_evidence_rubric_unavailable'
                and not (m == 'source_grounded_industry_mappings_unavailable' and role['industry_mappings'])]
            role['assessment_scope'] = 'Partial essential-skill anchored evidence comparison; not employment qualification'
            role['version'] = CATALOGUE_VERSION + ':' + fingerprint({'role': role, 'extension': extension['version'],
                                                                    'sources': extension['sources']})
        known_codes = {r['occupation']['O*NET-SOC Code'] for r in self._references.values()}
        for sid, codes in [('onet_essential_skills', skills), ('onet_software_skills', software)]:
            for code in sorted(set(codes) - known_codes):
                self.rejected.append(dict(source_id=sid, code=code, reason='orphan_occupation_identity'))
        self.coverage = dict(
            catalogue_version=CATALOGUE_VERSION, raw_rows={sid: len(tables[sid]) for sid in SOURCE_IDS},
            raw_unique_occupations=len(seen), normalized_roles=len(self._roles),
            runtime_roles=len(self._roles), eligible_roles=sum(r['eligibility'] == 'supported'
                                                              for r in self._roles.values()),
            partial_roles=sum(r['eligibility'] == 'partial' for r in self._roles.values()),
            roles_with_software=sum(bool(r['software_examples']) for r in self._references.values()),
            roles_with_industry_mappings=sum(bool(r['industry_mappings']) for r in self._roles.values()),
            roles_with_work_style_mappings=sum(bool(r['work_style_mappings']) for r in self._roles.values()),
            anchored_essential_skills=len(extension['skill_rubrics']),
            rejected=self.rejected, sources=list(sources.values()) + list(extension['sources'].values()),
            legacy_runtime_roles=3, scoring_coverage='profile-dependent; reported by assessment service',
            limitations=['US anchors/industry relationships are reference context, not Malaysian market evidence',
                         'Anchored self-report/project claims are provisional, not independently verified competence',
                         'Partial references remain browseable; no plan prerequisite'])

    def roles(self, *, eligible_only=False):
        return copy.deepcopy([r for r in self._roles.values()
                              if not eligible_only or r['eligibility'] == 'supported'])

    def role(self, role_id):
        return copy.deepcopy(self._roles[role_id])

    def reference(self, role_id):
        return copy.deepcopy(self._references[role_id])
