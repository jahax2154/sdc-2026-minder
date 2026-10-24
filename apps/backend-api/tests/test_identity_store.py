from concurrent.futures import ThreadPoolExecutor
from support import AppCase
from minder_app.auth_adapter import VerifiedIdentity
from minder_app.identity_store import owner_for_identity
from minder_app.store import Store, AppError


class IdentityStoreTests(AppCase):
    def test_verified_mapping_is_stable_concurrent_and_never_claims_anonymous(self):
        anonymous = self.save()
        identity = VerifiedIdentity("https://issuer.invalid", "synthetic-subject", "synthetic-session", 2000000000)
        with ThreadPoolExecutor(max_workers=8) as pool:
            owners = list(pool.map(lambda _: owner_for_identity(self.store, identity), range(16)))
        self.assertEqual(len(set(owners)), 1)
        self.assertNotEqual(owners[0], anonymous["profile_id"])
        self.assertEqual(Store(self.store.path).list(owners[0], "profile"), [])
        self.assertEqual(owner_for_identity(Store(self.store.path), identity), owners[0])
        other = owner_for_identity(self.store, VerifiedIdentity(identity.issuer, "other-user", "other-session", 2000000000))
        self.assertNotEqual(other, owners[0])
        other_issuer = owner_for_identity(self.store, VerifiedIdentity("https://other.invalid", identity.subject, "other-session", 2000000000))
        self.assertNotEqual(other_issuer, owners[0])
        self.assertEqual(self.store.get(anonymous["profile_id"], "profile", anonymous["profile_id"]), anonymous)

    def test_unverified_browser_mapping_rejected(self):
        for identity in ({"issuer":"https://issuer.invalid", "subject":"claimed-user"}, None,
                         VerifiedIdentity("", "user", "session", 2000000000)):
            with self.assertRaises(AppError) as error:
                owner_for_identity(self.store, identity)
            self.assertEqual(error.exception.status, 401)
