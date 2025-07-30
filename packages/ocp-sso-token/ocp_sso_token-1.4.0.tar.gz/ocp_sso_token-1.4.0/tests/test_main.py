"""Test ocp_sso_token.__main__ module."""
import contextlib
import io
import os
import pathlib
import tempfile
import typing
import unittest
from unittest import mock

import yaml

from ocp_sso_token import __main__
from tests import helpers


class TestMain(unittest.TestCase):
    """Test ocp_sso_token.__main__ module."""

    def test_main(self) -> None:
        """Test the main method."""
        cases: typing.Iterable[
            typing.Tuple[typing.List[str], str, Exception | None, typing.Any]
        ] = (
            (['https://api.cluster:6443'],
             'sha256~code2', None, None),
            (['https://api.cluster:6443', '--identity-providers', 'foo'],
             '', Exception('find OpenID'), None),
            (['https://api.cluster:6443', '--context', 'context', '--namespace', 'namespace'],
             '', None, {
                "apiVersion": "v1", "kind": "Config",
                'clusters': [{
                    'name': 'api-cluster:6443',
                    'cluster': {'server': 'https://api.cluster:6443'},
                }],
                'users': [{
                    'name': 'api-cluster:6443',
                    'user': {'token': 'sha256~code2'}
                }],
                'contexts': [{
                    'name': 'context',
                    'context': {'cluster': 'api-cluster:6443',
                                'user': 'api-cluster:6443',
                                'namespace': 'namespace'},
                }],
            }),
            (
                ['https://api.cluster:6443', '--insecure-skip-tls-verify'],
                'sha256~code2',
                None,
                None,
            ),
        )
        for args, output, exception, config in cases:
            with self.subTest(args=args), \
                    tempfile.TemporaryDirectory() as tempdir, \
                    helpers.setup_responses():
                tempconf = pathlib.Path(tempdir, 'conf')
                raises = (self.assertRaisesRegex(Exception, str(exception))
                          if isinstance(exception, Exception) else contextlib.nullcontext())
                with mock.patch.dict(os.environ, {'KUBECONFIG': str(tempconf)}), \
                        contextlib.redirect_stdout(stdout := io.StringIO()), \
                        raises:
                    __main__.main(args)
                self.assertEqual(stdout.getvalue().strip(), output)
                if config:
                    self.assertEqual(yaml.safe_load(tempconf.read_text(encoding='utf8')), config)
