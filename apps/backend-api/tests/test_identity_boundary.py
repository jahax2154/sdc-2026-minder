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

    def test_csp_managed_identity_and_documented_protect_scope(self):
        from types import SimpleNamespace
        from minder_ml.intelligence.product_runtime import content_security_policy
        with patch('minder_app.auth_adapter.AuthConfig.from_env',return_value=SimpleNamespace(issuer='https://synthetic.clerk.accounts.dev')):
            with patch.dict(os.environ,{'MINDER_CLERK_ADDITIONAL_ORIGINS':'https://tenant.protect.clerk.com'}):
                policy=content_security_policy()
                self.assertIn('https://synthetic.clerk.accounts.dev',policy)
                self.assertIn('https://tenant.protect.clerk.com',policy)
                directives={part.split()[0]:part.split()[1:] for part in policy.split(';')}
                self.assertIn('https://*.protect.clerk.com',directives['script-src'])
                self.assertIn('https://*.protect.clerk.com',directives['frame-src'])
                self.assertIn('https://*.protect.clerk.com:*',directives['connect-src'])
                self.assertNotIn('https://*.protect.clerk.com:*',directives['script-src'])
                self.assertNotIn('https://*.protect.clerk.com:*',directives['frame-src'])
                for sources in directives.values():
                    self.assertFalse({'*','https:','http:'}.intersection(sources))
                self.assertNotIn("'unsafe-inline'",directives['script-src'])
                self.assertNotIn('unsafe-eval',policy)
            for invalid in ('https://*.protect.clerk.com','https://*.protect.clerk.com:*',
                            'https://tenant.protect.clerk.com:8443','http://tenant.protect.clerk.com',
                            'https://untrusted.example','https://protect.clerk.com.evil.example'):
                with self.subTest(origin=invalid), patch.dict(os.environ,{'MINDER_CLERK_ADDITIONAL_ORIGINS':invalid}):
                    with self.assertRaises(ValueError):content_security_policy()

    def test_csp_local_runtime_keeps_self_only_policy(self):
        from minder_ml.intelligence.product_runtime import content_security_policy
        with patch('minder_app.auth_adapter.AuthConfig.from_env',side_effect=AppError(503,'auth_unavailable')):
            policy=content_security_policy()
        directives={part.split()[0]:part.split()[1:] for part in policy.split(';')}
        for directive in ('default-src','script-src','connect-src','frame-src','form-action'):
            self.assertEqual(directives[directive],["'self'"])
        for directive in ('object-src','base-uri','frame-ancestors'):
            self.assertEqual(directives[directive],["'none'"])
        self.assertNotIn('clerk.com',policy)

    def test_static_response_exposes_managed_csp_header(self):
        from types import SimpleNamespace
        from minder_ml.intelligence.product_runtime import web_app
        response=[]
        with patch('minder_app.auth_adapter.AuthConfig.from_env',return_value=SimpleNamespace(issuer='https://synthetic.clerk.accounts.dev')):
            with patch.dict(os.environ,{'MINDER_CLERK_ADDITIONAL_ORIGINS':''}):
                body=web_app(self.app)({'PATH_INFO':'/','REQUEST_METHOD':'GET'},
                    lambda status,headers: response.append((status,dict(headers))))
        self.assertTrue(body)
        self.assertEqual(response[0][0],'200 OK')
        self.assertIn('https://*.protect.clerk.com:*',response[0][1]['Content-Security-Policy'])
