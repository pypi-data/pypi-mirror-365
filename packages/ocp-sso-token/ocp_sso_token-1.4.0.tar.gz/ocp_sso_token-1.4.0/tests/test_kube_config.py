"""Test ocp_sso_token.kube_config module."""

from contextlib import redirect_stderr
import io
import os
import pathlib
import tempfile
import unittest
from unittest import mock

import yaml

from ocp_sso_token import kube_config


class TestKubeConfig(unittest.TestCase):
    """Test KubeConfig processing."""

    def test_new(self) -> None:
        """Test adding a token to a kubeconfig."""
        with tempfile.TemporaryDirectory() as tempdir:
            tempconf = pathlib.Path(tempdir, 'conf')
            with mock.patch('ocp_sso_token.kube_config.KUBE_CONFIG_PATH_DEFAULT', str(tempconf)), \
                    mock.patch.dict(os.environ, {'KUBECONFIG': ''}):  # should be ignored
                config = kube_config.KubeConfig('my-context', 'https://api-url:1234', 'namespace')
                self.assertEqual(config.config_path, tempconf)

                with redirect_stderr(stderr := io.StringIO()):
                    config.try_read_config()
                self.assertEqual(config.config, {
                    "apiVersion": "v1", "kind": "Config",
                    "clusters": [], "users": [], "contexts": [],
                })
                self.assertIn('not found', stderr.getvalue())

                config.update('token')
                self.assertEqual(config.config, {
                    "apiVersion": "v1", "kind": "Config",
                    'clusters': [{
                        'name': 'api-url:1234',
                        'cluster': {'server': 'https://api-url:1234'},
                    }],
                    'users': [{
                        'name': 'api-url:1234',
                        'user': {'token': 'token'},
                    }],
                    'contexts': [{
                        'name': 'my-context',
                        'context': {
                            'cluster': 'api-url:1234',
                            'user': 'api-url:1234',
                            'namespace': 'namespace',
                        },
                    }],
                })

                config.write_config()
                self.assertEqual(
                    yaml.safe_load(tempconf.read_text(encoding='utf8')),
                    {
                        "apiVersion": "v1", "kind": "Config",
                        'clusters': [{
                            'name': 'api-url:1234',
                            'cluster': {'server': 'https://api-url:1234'},
                        }],
                        'users': [{
                            'name': 'api-url:1234',
                            'user': {'token': 'token'},
                        }],
                        'contexts': [{
                            'name': 'my-context',
                            'context': {
                                'cluster': 'api-url:1234',
                                'user': 'api-url:1234',
                                'namespace': 'namespace',
                            },
                        }],
                    }
                )

                config = kube_config.KubeConfig('my-context', 'https://api-url:1234', 'namespace2')
                config.try_read_config()
                config.update('token2')
                self.assertEqual(config.config, {
                    "apiVersion": "v1", "kind": "Config",
                    'clusters': [{
                        'name': 'api-url:1234',
                        'cluster': {'server': 'https://api-url:1234'},
                    }],
                    'users': [{
                        'name': 'api-url:1234',
                        'user': {'token': 'token2'},
                    }],
                    'contexts': [{
                        'name': 'my-context',
                        'context': {
                            'cluster': 'api-url:1234',
                            'user': 'api-url:1234',
                            'namespace': 'namespace2',
                        },
                    }],
                })

                config.write_config()
                self.assertEqual(
                    yaml.safe_load(tempconf.read_text(encoding='utf8')),
                    {
                        "apiVersion": "v1", "kind": "Config",
                        'clusters': [{
                            'name': 'api-url:1234',
                            'cluster': {'server': 'https://api-url:1234'},
                        }],
                        'users': [{
                            'name': 'api-url:1234',
                            'user': {'token': 'token2'},
                        }],
                        'contexts': [{
                            'name': 'my-context',
                            'context': {
                                'cluster': 'api-url:1234',
                                'user': 'api-url:1234',
                                'namespace': 'namespace2',
                            },
                        }],
                    }
                )

    def test_no_namespace(self) -> None:
        """Test adding a token to a kubeconfig without a namespace."""
        with tempfile.TemporaryDirectory() as tempdir:
            tempconf = pathlib.Path(tempdir, 'conf')
            with mock.patch('ocp_sso_token.kube_config.KUBE_CONFIG_PATH_DEFAULT', str(tempconf)):
                config = kube_config.KubeConfig('my-context', 'https://api-url:1234', None)
                self.assertEqual(config.config_path, tempconf)

                config.try_read_config()
                self.assertEqual(config.config, {
                    "apiVersion": "v1", "kind": "Config",
                    "clusters": [], "users": [], "contexts": [],
                })

                config.update('token')
                self.assertEqual(config.config, {
                    "apiVersion": "v1", "kind": "Config",
                    'clusters': [{
                        'name': 'api-url:1234',
                        'cluster': {'server': 'https://api-url:1234'},
                    }],
                    'users': [{
                        'name': 'api-url:1234',
                        'user': {'token': 'token'},
                    }],
                    'contexts': [{
                        'name': 'my-context',
                        'context': {
                            'cluster': 'api-url:1234',
                            'user': 'api-url:1234',
                        },
                    }],
                })

                config = kube_config.KubeConfig('my-context', 'https://api-url:1234', 'namespace')
                config.try_read_config()
                config.update('token2')
                config.write_config()
                self.assertEqual(
                    yaml.safe_load(tempconf.read_text(encoding='utf8')),
                    {
                        "apiVersion": "v1", "kind": "Config",
                        'clusters': [{
                            'name': 'api-url:1234',
                            'cluster': {'server': 'https://api-url:1234'},
                        }],
                        'users': [{
                            'name': 'api-url:1234',
                            'user': {'token': 'token2'},
                        }],
                        'contexts': [{
                            'name': 'my-context',
                            'context': {
                                'cluster': 'api-url:1234',
                                'user': 'api-url:1234',
                                'namespace': 'namespace',
                            },
                        }],
                    }
                )

                config = kube_config.KubeConfig('my-context', 'https://api-url:1234', None)
                config.try_read_config()
                config.update('token3')
                config.write_config()
                self.assertEqual(
                    yaml.safe_load(tempconf.read_text(encoding='utf8')),
                    {
                        "apiVersion": "v1", "kind": "Config",
                        'clusters': [{
                            'name': 'api-url:1234',
                            'cluster': {'server': 'https://api-url:1234'},
                        }],
                        'users': [{
                            'name': 'api-url:1234',
                            'user': {'token': 'token3'},
                        }],
                        'contexts': [{
                            'name': 'my-context',
                            'context': {
                                'cluster': 'api-url:1234',
                                'user': 'api-url:1234',
                                'namespace': 'namespace',
                            },
                        }],
                    }
                )

    def test_override(self) -> None:
        """Test adding a token to a kubeconfig determined by KUBECONFIG."""
        with tempfile.TemporaryDirectory() as tempdir:
            tempconf = pathlib.Path(tempdir, 'conf')
            with mock.patch.dict(os.environ, {'KUBECONFIG': str(tempconf)}):
                config = kube_config.KubeConfig('my-context', 'https://api-url:1234', 'namespace')
                self.assertEqual(config.config_path, tempconf)

                config.try_read_config()
                self.assertEqual(config.config, {
                    "apiVersion": "v1", "kind": "Config",
                    "clusters": [], "users": [], "contexts": [],
                })

                config.update('token')
                config.write_config()
                self.assertEqual(
                    yaml.safe_load(tempconf.read_text(encoding='utf8')),
                    {
                        "apiVersion": "v1", "kind": "Config",
                        'clusters': [{
                            'name': 'api-url:1234',
                            'cluster': {'server': 'https://api-url:1234'},
                        }],
                        'users': [{
                            'name': 'api-url:1234',
                            'user': {'token': 'token'},
                        }],
                        'contexts': [{
                            'name': 'my-context',
                            'context': {
                                'cluster': 'api-url:1234',
                                'user': 'api-url:1234',
                                'namespace': 'namespace',
                            },
                        }],
                    }
                )

                config = kube_config.KubeConfig('my-context', 'https://api-url:1234', 'namespace2')
                config.try_read_config()
                config.update('token2')
                config.write_config()
                self.assertEqual(
                    yaml.safe_load(tempconf.read_text(encoding='utf8')),
                    {
                        "apiVersion": "v1", "kind": "Config",
                        'clusters': [{
                            'name': 'api-url:1234',
                            'cluster': {'server': 'https://api-url:1234'},
                        }],
                        'users': [{
                            'name': 'api-url:1234',
                            'user': {'token': 'token2'},
                        }],
                        'contexts': [{
                            'name': 'my-context',
                            'context': {
                                'cluster': 'api-url:1234',
                                'user': 'api-url:1234',
                                'namespace': 'namespace2',
                            },
                        }],
                    })

    def test_multiple_existing(self) -> None:
        """Test adding a token to the first existing kubeconfig."""
        with tempfile.TemporaryDirectory() as tempdir:
            tempconf = pathlib.Path(tempdir, 'conf')
            with mock.patch('ocp_sso_token.kube_config.KUBE_CONFIG_PATH_DEFAULT', str(tempconf)):
                config = kube_config.KubeConfig('my-context', 'https://other-api-url:1234', None)
                config.update('token')
                config.write_config()
                self.assertEqual(
                    yaml.safe_load(tempconf.read_text(encoding='utf8')),
                    {
                        "apiVersion": "v1", "kind": "Config",
                        'clusters': [{
                            'name': 'other-api-url:1234',
                            'cluster': {'server': 'https://other-api-url:1234'},
                        }],
                        'users': [{
                            'name': 'other-api-url:1234',
                            'user': {'token': 'token'},
                        }],
                        'contexts': [{
                            'name': 'my-context',
                            'context': {
                                'cluster': 'other-api-url:1234',
                                'user': 'other-api-url:1234',
                            },
                        }],
                    }
                )

            with mock.patch.dict(os.environ, {'KUBECONFIG': f'non-existing:{tempconf}'}):
                config = kube_config.KubeConfig('context2', 'https://api-url:1234', 'namespace')
                self.assertEqual(config.config_path, tempconf)
                config.try_read_config()
                self.assertEqual(config.config, {
                    "apiVersion": "v1", "kind": "Config",
                    'clusters': [{
                        'name': 'other-api-url:1234',
                        'cluster': {'server': 'https://other-api-url:1234'},
                    }],
                    'users': [{
                        'name': 'other-api-url:1234',
                        'user': {'token': 'token'},
                    }],
                    'contexts': [{
                        'name': 'my-context',
                        'context': {
                                'cluster': 'other-api-url:1234',
                                'user': 'other-api-url:1234',
                        },
                    }],
                })

                config.update('token2')
                config.write_config()
                self.assertEqual(
                    yaml.safe_load(tempconf.read_text(encoding='utf8')),
                    {
                        "apiVersion": "v1", "kind": "Config",
                        'clusters': [{
                            'name': 'other-api-url:1234',
                            'cluster': {'server': 'https://other-api-url:1234'},
                        }, {
                            'name': 'api-url:1234',
                            'cluster': {'server': 'https://api-url:1234'},
                        }],
                        'users': [{
                            'name': 'other-api-url:1234',
                            'user': {'token': 'token'},
                        }, {
                            'name': 'api-url:1234',
                            'user': {'token': 'token2'},
                        }],
                        'contexts': [{
                            'name': 'my-context',
                            'context': {
                                'cluster': 'other-api-url:1234',
                                'user': 'other-api-url:1234',
                            },
                        }, {
                            'name': 'context2',
                            'context': {
                                'cluster': 'api-url:1234',
                                'user': 'api-url:1234',
                                'namespace': 'namespace',
                            },
                        }],
                    }
                )

    def test_multiple_matching(self) -> None:
        """Test adding a token to the first matching kubeconfig."""
        with tempfile.TemporaryDirectory() as tempdir:
            tempconf1 = pathlib.Path(tempdir, 'conf1')
            with mock.patch('ocp_sso_token.kube_config.KUBE_CONFIG_PATH_DEFAULT', str(tempconf1)):
                config = kube_config.KubeConfig('other-context', 'https://other-api-url:1234', None)
                config.update('token')
                config.write_config()

            tempconf2 = pathlib.Path(tempdir, 'conf2')
            with mock.patch('ocp_sso_token.kube_config.KUBE_CONFIG_PATH_DEFAULT', str(tempconf2)):
                config = kube_config.KubeConfig('my-context', 'https://api-url:1234', None)
                config.update('token2')
                config.write_config()

            with mock.patch.dict(os.environ, {'KUBECONFIG': f'{tempconf1}:{tempconf2}'}):
                config = kube_config.KubeConfig('my-context', 'https://api-url:1234', 'namespace')
                self.assertEqual(config.config_path, tempconf2)
                config.try_read_config()
                self.assertEqual(config.config, {
                    "apiVersion": "v1", "kind": "Config",
                    'clusters': [{
                        'name': 'api-url:1234',
                        'cluster': {'server': 'https://api-url:1234'},
                    }],
                    'users': [{
                        'name': 'api-url:1234',
                        'user': {'token': 'token2'},
                    }],
                    'contexts': [{
                        'name': 'my-context',
                        'context': {
                                'cluster': 'api-url:1234',
                                'user': 'api-url:1234',
                        },
                    }],
                })

                config.update('token3')
                config.write_config()
                self.assertEqual(
                    yaml.safe_load(tempconf2.read_text(encoding='utf8')),
                    {
                        "apiVersion": "v1", "kind": "Config",
                        'clusters': [{
                            'name': 'api-url:1234',
                            'cluster': {'server': 'https://api-url:1234'},
                        }],
                        'users': [{
                            'name': 'api-url:1234',
                            'user': {'token': 'token3'},
                        }],
                        'contexts': [{
                            'name': 'my-context',
                            'context': {
                                'cluster': 'api-url:1234',
                                'user': 'api-url:1234',
                                'namespace': 'namespace',
                            },
                        }],
                    }
                )

    def test_directory(self) -> None:
        """Test creating intermediate directories."""
        with tempfile.TemporaryDirectory() as tempdir:
            tempconf = pathlib.Path(tempdir, 'config/conf')
            with mock.patch('ocp_sso_token.kube_config.KUBE_CONFIG_PATH_DEFAULT', str(tempconf)):
                config = kube_config.KubeConfig('my-context', 'https://api-url:1234', 'namespace')
                config.try_read_config()
                self.assertEqual(config.config, {
                    "apiVersion": "v1", "kind": "Config",
                    "clusters": [], "users": [], "contexts": [],
                })
                config.update('token')
                config.write_config()
                self.assertEqual(
                    yaml.safe_load(tempconf.read_text(encoding='utf8')),
                    {
                        "apiVersion": "v1", "kind": "Config",
                        'clusters': [{
                            'name': 'api-url:1234',
                            'cluster': {'server': 'https://api-url:1234'},
                        }],
                        'users': [{
                            'name': 'api-url:1234',
                            'user': {'token': 'token'},
                        }],
                        'contexts': [{
                            'name': 'my-context',
                            'context': {
                                'cluster': 'api-url:1234',
                                'user': 'api-url:1234',
                                'namespace': 'namespace',
                            },
                        }],
                    }
                )
