"""Test ocp_sso_token.ocp_oauth_login module."""
import unittest

from ocp_sso_token import ocp_oauth_login
from tests import helpers


class TestOcpOAuthLogin(unittest.TestCase):
    """Test OAuthLogin processing."""

    def test_flow(self) -> None:
        """Test the basic token flow."""
        cases = (
            ('list', False),
            ('single idp forward', True),
        )

        for description, forward in cases:
            with self.subTest(description), helpers.setup_responses(forward) as rsps:
                login = ocp_oauth_login.OcpOAuthLogin('https://api.cluster:6443')
                self.assertEqual(login.token(['OpenID']), 'sha256~code2')
                self.assertEqual(rsps.calls[-1].request.body, 'code=sha256~code1&csrf=csrf1')


class TestInsecureSkipTLSVerify(unittest.TestCase):
    """Test the insecure TLS verification flag."""

    def test_default_tls_verification_enabled(self) -> None:
        """By default, TLS verification is enabled."""
        login = ocp_oauth_login.OcpOAuthLogin('https://api.cluster:6443')
        self.assertTrue(login.session.verify)

    def test_tls_verification_disabled_with_flag(self) -> None:
        """When insecure_skip_tls_verify=True, TLS verification is disabled."""
        login = ocp_oauth_login.OcpOAuthLogin(
            'https://api.cluster:6443',
            insecure_skip_tls_verify=True
        )
        self.assertFalse(login.session.verify)
