import base64
import unittest
from jsonschema.exceptions import ValidationError
from minder_app.documents import DocumentLimits, validate_upload
from minder_app.store import AppError


def upload_body(content=b"Fictional student", filename="fictional.txt", content_type="text/plain", key="upload"):
    return dict(filename=filename, content_type=content_type,
                content_base64=base64.b64encode(content).decode("ascii"), idempotency_key=key)


class DocumentValidationTests(unittest.TestCase):
    def test_pdf_txt_and_exact_size(self):
        limits = DocumentLimits(max_file_bytes=40)
        for body in (upload_body(b"x"*40), upload_body(b"%PDF-1.4\n%%EOF\n", "fictional.pdf", "application/pdf")):
            self.assertEqual(validate_upload(body, limits), base64.b64decode(body["content_base64"]))
        with self.assertRaises(AppError) as error:
            validate_upload(upload_body(b"x"*41), limits)
        self.assertEqual(error.exception.status, 413)

    def test_invalid_formats_names_encoding_and_owner_fields(self):
        bodies = [upload_body(b"binary", "file.pdf", "application/pdf"),
            upload_body(b"x", "file.exe"), upload_body(b"x", "file.pdf"),
            upload_body(b"\x00binary"), upload_body(b"\xff"), upload_body(b""),
            upload_body(b"x", "../file.txt"), upload_body(b"x", "evil\n.txt"),
            dict(upload_body(), content_base64="!invalid!"), dict(upload_body(), owner="other")]
        for body in bodies:
            with self.subTest(filename=body["filename"]):
                with self.assertRaises((AppError, ValidationError)):
                    validate_upload(body, DocumentLimits())

    def test_configuration_is_bounded_and_transport_accounts_for_base64(self):
        limits = DocumentLimits.from_environment({"MINDER_DOCUMENT_MAX_FILE_BYTES": "1024", "MINDER_DOCUMENT_MAX_FILES": "2"})
        self.assertEqual((limits.max_file_bytes, limits.max_files), (1024, 2))
        self.assertGreaterEqual(limits.upload_request_bytes, 4*((1024+2)//3))
        for env in ({"MINDER_DOCUMENT_MAX_FILE_BYTES": "0"}, {"MINDER_DOCUMENT_MAX_FILES": "bad"},
                    {"MINDER_DOCUMENT_MAX_USER_BYTES": str(65*1024*1024)}):
            with self.assertRaises(AppError):
                DocumentLimits.from_environment(env)
