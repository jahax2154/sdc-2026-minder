"""Real synthetic CV library DTOs validate against A's exact public export."""
import base64,json,tempfile
from pathlib import Path
from jsonschema import Draft202012Validator
from minder_app.store import Store
from minder_app.documents import DocumentLibrary
from minder_app.document_storage import LocalDocumentStorage
from minder_ml.intelligence.policy import ROOT


def main():
    schema=json.loads((ROOT/'docs/execution/product-v2/contracts.schema.json').read_text())
    def check(kind,value):
        Draft202012Validator(dict(schema,**{'$ref':'#/$defs/'+kind})).validate(value)
    root=ROOT/'ml/artifacts/session-a/product/morning';root.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(dir=root) as tmp:
        store=Store(Path(tmp)/'contract.sqlite3');owner=store.session()['profile_id']
        lib=DocumentLibrary(store,LocalDocumentStorage(Path(tmp)/'private-docs'))
        check('DocumentList',lib.list(owner))
        uploaded=lib.upload(owner,dict(filename='synthetic-resume.txt',content_type='text/plain',purpose='resume',
            content_base64=base64.b64encode(b'Fictional student: built a bus-delay notebook.').decode(),idempotency_key='upload'))
        check('DocumentUploadResult',uploaded)
        check('DocumentList',lib.list(owner))
        did=uploaded['document']['document_id']
        check('DocumentExtractResult',lib.extract(owner,dict(document_id=did)))
        check('DocumentDownloadResult',lib.download(owner,dict(document_id=did)))
        check('DocumentDeleted',lib.delete(owner,dict(document_id=did,expected_version=lib.list(owner)['documents'][0]['version'],idempotency_key='delete')))
    print('Actual synthetic list/upload/extract/download/delete DTO contracts passed; local development storage only.')

if __name__=='__main__':main()
