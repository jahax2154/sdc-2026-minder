import os
from unittest.mock import patch
from support import AppCase
from minder_app.store import AppError


class BoundaryTests(AppCase):
    def test_local_explicit_contract_and_private_isolation(self):
        with patch.dict(os.environ,{'MINDER_ENV':'development','MINDER_AUTH_PROVIDER':''}):
            config=self.app.dispatch('GET','/api/auth/config',{},'')
            self.assertTrue(config['anonymous_session_allowed'])
            result=self.app.dispatch('GET','/api/auth/session',{},self.token)
            self.assertEqual(result['user']['id'],self.session['profile_id'])
            with self.assertRaises(AppError):self.app.dispatch('GET','/api/auth/session',{},'')
            self.assertNotIn('secret',str(config))

    def test_hosted_never_accepts_local_capability_or_unavailable_auth(self):
        with patch.dict(os.environ,{'MINDER_ENV':'production','MINDER_AUTH_PROVIDER':''}):
            config=self.app.dispatch('GET','/api/auth/config',{},'')
            self.assertFalse(config['anonymous_session_allowed'])
            with self.assertRaises(AppError) as e:self.app.dispatch('POST','/api/session',{},'')
            self.assertEqual(e.exception.status,401)
            with self.assertRaises(AppError) as e:self.app.dispatch('GET','/api/profile',{},self.token)
            self.assertEqual(e.exception.status,503)

    def test_csp_exact_identity_hosts_and_no_wildcard(self):
        from types import SimpleNamespace
        from minder_ml.intelligence.product_runtime import content_security_policy
        with patch('minder_app.auth_adapter.AuthConfig.from_env',return_value=SimpleNamespace(issuer='https://synthetic.clerk.accounts.dev')):
            with patch.dict(os.environ,{'MINDER_CLERK_ADDITIONAL_ORIGINS':'https://tenant.protect.clerk.com'}):
                policy=content_security_policy()
                self.assertIn('https://synthetic.clerk.accounts.dev',policy)
                self.assertIn('https://tenant.protect.clerk.com',policy)
                self.assertNotIn('*',policy)
                self.assertNotIn('unsafe-eval',policy)
            with patch.dict(os.environ,{'MINDER_CLERK_ADDITIONAL_ORIGINS':'https://*.protect.clerk.com'}):
                with self.assertRaises(ValueError):content_security_policy()
