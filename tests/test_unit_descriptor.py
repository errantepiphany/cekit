import pytest
import yaml

from cekit.config import Config
from cekit.errors import CekitError
from cekit.descriptor import Label, Port, Env, Volume, Packages, Image, Osbs, \
    Repository


config = Config()
config.configure('/dev/null', {'redhat': True})


def test_label():
    label = Label(yaml.safe_load("""
      name: "io.k8s.display-name"
      value: "JBoss A-MQ 6.2"
"""))
    assert label['name'] == "io.k8s.display-name"
    assert label['value'] == "JBoss A-MQ 6.2"


def test_env():
    env = Env(yaml.safe_load("""
      name: "io.k8s.display-name"
      value: "JBoss A-MQ 6.2"
"""))
    assert env['name'] == "io.k8s.display-name"
    assert env['value'] == "JBoss A-MQ 6.2"


def test_port():
    env = Port(yaml.safe_load("""
      value: 8788
      expose: False
"""))
    assert env['value'] == 8788
    assert env['name'] == 8788
    assert not env['expose']


def test_volume():
    volume = Volume(yaml.safe_load("""
    name: vol1
    path: /tmp/a
"""))
    assert volume['name'] == 'vol1'
    assert volume['path'] == '/tmp/a'


def test_volume_name():
    volume = Volume(yaml.safe_load("""
    path: /tmp/a
"""))
    assert volume['name'] == 'a'
    assert volume['path'] == '/tmp/a'


def test_osbs():
    osbs = Osbs(yaml.safe_load("""
    repository:
      name: foo
      branch: bar
"""), "a/path/image.yaml")

    assert osbs['repository']['name'] == 'foo'
    assert osbs['repository']['branch'] == 'bar'


def test_packages():
    pkg = Packages(yaml.safe_load("""
      install:
          - pkg-foo"""), "a/path/image.yaml")

    assert 'pkg-foo' in pkg['install']


def test_packages_invalid_old_repository_definition():
    with pytest.raises(CekitError, match=r"Cannot validate schema: Repository"):
        Packages(yaml.safe_load("""
        repositories:
            - repo-foo
            - repo-bar
        install:
            - pkg-foo"""), "a/path/image.yaml")


def test_image():
    image = Image(yaml.safe_load("""
    from: foo
    name: test/foo
    version: 1.9
    labels:
      - name: test
        value: val1
      - name: label2
        value: val2
    envs:
      - name: env1
        value: env1val
    """), 'foo')

    assert image['name'] == 'test/foo'
    assert type(image['labels'][0]) == Label
    assert image['labels'][0]['name'] == 'test'


def test_image_missing_name():
    with pytest.raises(CekitError):
        Image(yaml.safe_load("""
        from: foo
        version: 1.9"""), 'foo')


def test_remove_none_key():
    image = Image(yaml.safe_load("""
    from: foo
    name: test/foo
    version: 1.9
    envs:
     - name: foo
       value: ~
    """), 'foo')
    image.remove_none_keys()

    assert 'envs' in image
    assert 'value' not in image['envs'][0]
