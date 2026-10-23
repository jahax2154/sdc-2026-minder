"""Export fictional API responses; provider selection is mocked, sources are real."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
from jsonschema import validate as schema_validate
from minder_app.runtime import application, ROOT
from minder_ml.intelligence.service_contracts import validate

OUT = ROOT / 'docs/execution/product/llm'

class SelectAll:
    def complete_tool(self, messages, tool):
        ids = tool['function']['parameters']['properties']['statement_ids']['items']['enum']
        return dict(status='available', model='mock-selection', text=json.dumps(dict(statement_ids=ids)))


def main():
    with tempfile.TemporaryDirectory(dir=ROOT / 'ml/artifacts/session-c') as folder:
        os.environ['MINDER_DB_PATH'] = str(Path(folder) / 'contract.sqlite3')
        app = application()
        app.provider = SelectAll()
        session = app.store.session()
        token = session['token']
        def call(method, path, body=None):
            return app.dispatch(method, '/api/' + path, body or {}, token)
        profile = dict(profile_id='new',profile_group_id='new',version='new',synthetic=True,
            evidence=[],preferences=[],current_fields=[],constraints=[],timezone='Asia/Kuala_Lumpur')
        profile = call('PUT','profile',dict(profile=profile,expected_version=None))
        validate('Profile', profile)
        role = 'onet:15-1252.00'
        request = dict(message='Explain the source scope, with no forecast inferred.',
            expected_profile_version=profile['version'],selected_role_ids=[role])
        chat = call('POST','chat',request)
        evidence = call('POST','role-evidence',dict(role_id=role))
        for record in evidence['records']:
            validate('MarketEvidence',record)
        for passage in evidence['passages']:
            validate('EvidencePassage',passage)
        examples = dict(backend_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            synthetic_user=True,provider='mock-selection; not a live provider check',
            profile=profile,chat_request=request,chat_response=chat,role_evidence=evidence,
            proposals=call('GET','proposals'),action_history=call('GET','action-history'),agents=call('GET','agents'))
        schema_validate(chat,json.loads((OUT / 'frontend-envelope.schema.json').read_text()))
        (OUT / 'examples.json').write_text(json.dumps(examples,indent=2)+'\n')
        print('frontend_examples_validated=true; provider_mocked=true; source_services_real=true')

if __name__ == '__main__':
    main()
