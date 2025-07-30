"""Obtain an OCP OAuth token for an SSO IdP with Kerberos support."""

import functools
import sys
import typing
from urllib import parse
from xml.etree.ElementTree import Element

import html5lib
import requests
import requests_gssapi


class OcpOAuthLogin:
    """Obtain an OCP OAuth token for an SSO IdP with Kerberos support."""

    def __init__(self, api_url: str,
                 insecure_skip_tls_verify: bool = False):
        """Create an instance for a certain cluster represented by its API URL."""
        self.session = requests.Session()

        # Disable insecure TLS warnings if insecure_skip_tls_verify is True
        if insecure_skip_tls_verify:
            self.session.verify = False
            print("WARNING: Using --insecure-skip-tls-verify", file=sys.stderr)

        self.auth = requests_gssapi.HTTPSPNEGOAuth(mutual_authentication=requests_gssapi.OPTIONAL)
        self.meta_url = parse.urljoin(api_url, '/.well-known/oauth-authorization-server')

    @functools.cached_property
    def _token_endpoint(self) -> str:
        """Return the URL of the OAuth token endpoint."""
        response = self.session.get(self.meta_url)
        response.raise_for_status()
        return str(response.json()['token_endpoint'])

    def request(
        self,
        url: str,
        *,
        method: str = 'GET',
        data: typing.Any = None,
    ) -> typing.Tuple[Element, requests.Response]:
        """Perform an authenticated request and return the parsed HTML tree."""
        response = self.session.request(method, url, data=data, auth=self.auth)
        response.raise_for_status()
        return html5lib.parse(response.text, namespaceHTMLElements=False), response

    def idp_url(
        self,
        root: Element,
        identity_providers: typing.Collection[str],
    ) -> str:
        """Return the first matching IDP url."""
        # https://github.com/openshift/oauth-server/blob/master/pkg/server/selectprovider/templates.go
        for idp in root.iterfind('.//a[@href]'):
            idp_url = parse.urlparse(idp.attrib['href'])
            if set(identity_providers) & set(parse.parse_qs(idp_url.query).get('idp', ())):
                return parse.urljoin(self._token_endpoint, idp.attrib['href'])
        raise Exception(f'Unable to find OpenID provider: {", ".join(identity_providers)}')

    def token(self, identity_providers: typing.Collection[str]) -> str:
        """Authenticate with one of the given identity providers and return an access token."""
        # https://github.com/openshift/library-go/blob/master/pkg/oauth/oauthdiscovery/urls.go
        root, response = self.request(self._token_endpoint + '/request')

        # https://github.com/openshift/oauth-server/blob/master/pkg/server/tokenrequest/tokenrequest.go
        if root.find('.//input[@name="code"]') is None:
            root, response = self.request(self.idp_url(root, identity_providers))

        # https://github.com/openshift/oauth-server/blob/master/pkg/server/tokenrequest/tokenrequest.go
        data = {
            e.attrib['name']: e.attrib['value']
            for e in root.iterfind('.//form/input[@type="hidden"]')
        }

        root, response = self.request(response.url, data=data, method='POST')
        # https://github.com/openshift/oauth-server/blob/master/pkg/server/tokenrequest/tokenrequest.go
        if (code := root.find('.//code')) is None:
            raise Exception(f'Unable to find access token in response: {response.text}')
        return str(code.text)
