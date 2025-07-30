"""Obtain an OCP OAuth token for an SSO IdP with Kerberos support."""

from __future__ import annotations

import argparse
import typing

from . import kube_config
from . import ocp_oauth_login


def main(argv: typing.List[str] | None = None) -> None:
    """Obtain an OCP OAuth token for an SSO IdP with Kerberos support."""
    parser = argparse.ArgumentParser(description='Obtain an OCP OAuth token for a Kerberos ticket',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('api_url',
                        help='Cluster API URL like https://api.cluster:6443')
    parser.add_argument('--identity-providers', default='SSO,OpenID',
                        help='Identity provider names')
    parser.add_argument('--context',
                        help='Instead of printing the token, store it in the given context')
    parser.add_argument('--namespace',
                        help='Namespace to use for --context')
    parser.add_argument('--insecure-skip-tls-verify', action='store_true', default=False,
                        help='Disable TLS certificate verification (INSECURE)')

    args = parser.parse_args(argv)

    login = ocp_oauth_login.OcpOAuthLogin(
        args.api_url,
        insecure_skip_tls_verify=args.insecure_skip_tls_verify,
    )

    token = login.token(args.identity_providers.split(','))
    if args.context:
        config = kube_config.KubeConfig(args.context, args.api_url, args.namespace)
        config.try_read_config()
        config.update(token)
        config.write_config()
    else:
        print(token)


if __name__ == '__main__':
    main()
