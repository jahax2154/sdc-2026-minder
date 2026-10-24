"""SDK boundary fixtures, explicitly not real bucket/hosted durability evidence."""
import unittest
from unittest.mock import patch
try:
    from replit.object_storage.errors import ObjectNotFoundError
except ImportError:
    ObjectNotFoundError = None
from support import AppCase
from test_documents import upload_body
from minder_app.document_storage import ReplitAppStorage
from minder_app.documents import DocumentLibrary
from minder_app.store import AppError


class FakeBucket:
    def __init__(self):
        self.objects={};self.calls=[];self.fail_after_upload=False;self.fail_after_delete=False;self.fail_read=False
    def download_as_bytes(self,name):
        self.calls.append(('read',name))
        if self.fail_read:raise RuntimeError('private SDK credentials must never escape')
        if name not in self.objects:raise ObjectNotFoundError('not found')
        return self.objects[name]
    def upload_from_bytes(self,name,content):
        self.calls.append(('upload',name));self.objects[name]=content
        if self.fail_after_upload:
            self.fail_after_upload=False
            raise RuntimeError('private upload response lost')
    def delete(self,name,ignore_not_found=False):
        self.calls.append(('delete',name));self.objects.pop(name,None)
        if self.fail_after_delete:
            self.fail_after_delete=False
            raise RuntimeError('private delete response lost')
    def list(self,**kwargs):
        if self.fail_read:raise RuntimeError('private config error')
        return []


@unittest.skipUnless(ObjectNotFoundError, 'optional replit-object-storage SDK not installed')
class ReplitStorageTests(unittest.TestCase):
    def setUp(self):
        self.bucket=FakeBucket()
        self.storage=ReplitAppStorage('synthetic-private-bucket',client=self.bucket)
        self.key='a'*32
    def test_exact_retry_unknown_upload_outcome_and_bounded_read(self):
        self.bucket.fail_after_upload=True
        with self.assertRaises(AppError) as error:self.storage.put(self.key,b'Fictional CV')
        self.assertEqual(error.exception.code,'document_storage_write_outcome_unconfirmed')
        self.assertNotIn('private upload',str(error.exception))
        self.storage.put(self.key,b'Fictional CV')
        self.assertEqual(sum(call[0]=='upload' for call in self.bucket.calls),1)
        self.assertEqual(self.storage.get(self.key,12),b'Fictional CV')
        with self.assertRaises(AppError):self.storage.get(self.key,1)
        with self.assertRaises(AppError):self.storage.put(self.key,b'Changed CV')
        with self.assertRaises(AppError):self.storage.get('../secret',100)
        self.assertEqual(self.storage.probe()['read_access'],'verified')
        self.assertFalse(self.storage.probe()['durable_hosting_verified'])
    def test_delete_verifies_absence_and_retries_lost_response(self):
        self.storage.put(self.key,b'Fictional CV')
        self.bucket.fail_after_delete=True
        with self.assertRaises(AppError):self.storage.delete(self.key)
        self.storage.delete(self.key)
        self.storage.delete(self.key)
        self.assertEqual(self.bucket.objects,{})
        self.bucket.fail_read=True
        for operation in (lambda:self.storage.get(self.key,100),self.storage.probe):
            with self.assertRaises(AppError) as error:operation()
            self.assertNotIn('credentials',str(error.exception))
    def test_requires_explicit_bucket_and_valid_prefix_and_pg(self):
        for bucket,prefix in ((None,'minder/private/'),('','minder/private/'),('bucket','../'),
                              ('bucket','/public/'),('bucket','a//b/')):
            with self.assertRaises(AppError):ReplitAppStorage(bucket,prefix,client=self.bucket)
        class SQLite:
            engine='sqlite'
        with self.assertRaises(AppError) as error:
            DocumentLibrary.from_environment(SQLite(),{'MINDER_DOCUMENT_STORAGE':'replit-app-storage'})
        self.assertEqual(error.exception.code,'replit_document_storage_requires_postgresql')
        class PostgreSQL:
            engine='postgresql'
        with patch('replit.object_storage.Client',return_value=self.bucket):
            storage=ReplitAppStorage.from_environment({'MINDER_DOCUMENT_STORAGE_BUCKET_ID':'bucket'})
            self.assertIs(storage._client,self.bucket)


@unittest.skipUnless(ObjectNotFoundError, 'optional replit-object-storage SDK not installed')
class ReplitLibraryTests(AppCase):
    def setUp(self):
        super().setUp()
        self.owner=self.session['profile_id'];self.bucket=FakeBucket()
        self.library=DocumentLibrary(self.store,ReplitAppStorage('synthetic-bucket',client=self.bucket))
    def test_owner_retry_reconnect_review_delete_and_unknown_outcomes(self):
        body=upload_body()
        self.bucket.fail_after_upload=True
        with self.assertRaises(AppError):self.library.upload(self.owner,body)
        pending=self.library.list(self.owner)
        self.assertEqual(pending['documents'][0]['status'],'uploading')
        self.assertEqual(pending['usage']['file_count'],1)
        doc=self.library.upload(self.owner,body)['document']
        second=DocumentLibrary(self.store,ReplitAppStorage('synthetic-bucket',client=self.bucket))
        self.assertEqual(second.upload(self.owner,body)['document'],doc)
        self.assertEqual(second.list(self.owner)['documents'][0],doc)
        with self.assertRaises(AppError):second.download('other-owner',{'document_id':doc['document_id']})
        self.assertEqual(sum(call[0]=='upload' for call in self.bucket.calls),1)
        extraction=second.extract(self.owner,{'document_id':doc['document_id']})
        self.assertEqual(extraction['extraction']['status'],'review_available')
        doc=extraction['document']
        deletion={'document_id':doc['document_id'],'expected_version':doc['version'],'idempotency_key':'delete'}
        self.bucket.fail_after_delete=True
        with self.assertRaises(AppError):second.delete(self.owner,deletion)
        self.assertEqual(second.list(self.owner)['documents'][0]['status'],'deleting')
        with self.store.connect() as db:
            self.assertEqual(db.execute('SELECT count(*) FROM library_drafts WHERE owner=?',(self.owner,)).fetchone()[0],0)
            self.assertEqual(db.execute('SELECT count(*) FROM drafts WHERE owner=?',(self.owner,)).fetchone()[0],0)
        self.assertEqual(second.delete(self.owner,deletion)['status'],'deleted')
        self.assertEqual(self.bucket.objects,{})
        self.assertEqual(second.list(self.owner)['usage'],{'file_count':0,'stored_or_reserved_bytes':0})
