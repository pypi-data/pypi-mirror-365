import os

from antgent.config import config


def test_config_test_env():
    assert config().app.env == "test"


def test_config_fields():
    assert config().logging.level == "info"
    assert config().conf.app.env == "test"
    assert config().conf.app.prometheus_dir == "/tmp/testprom"
    assert config().conf.name == "antgent-test"


def test_config_reinit():
    conf = config().dump()
    _ = config(reload=True)
    assert config().dump() == conf
    # Changes are ignored without reinit
    config("tests/data/config-2.yaml")
    assert config().dump() == conf
    # Changes are applied after reinit
    config("tests/data/config-2.yaml", reload=True)
    assert config().dump() != conf




def test_config_env_precedence(monkeypatch):
    assert config(reload=True).app.env == "test"
    monkeypatch.setattr(
        os, "environ", {"ANTGENT_APP__ENV": "test-3", "ANTGENT_CONFIG": "tests/data/test_config.yaml"}
    )
    # Env setting has precedence over config file
    assert config(reload=True).app.env == "test-3"
    # Other env are not affected
    assert config().conf.name == "antgent-test"
    monkeypatch.setattr(
        os, "environ", {"ANTGENT_NAME": "antgent-test-3", "ANTGENT_CONFIG": "tests/data/test_config.yaml"}
    )
    assert config(reload=True).conf.name == "antgent-test-3"
    assert config(reload=True).conf.app.env == "test"


def test_config_path_failed_path_fallback():
    config("tests/data/config-dontexist.yaml", reload=True)
    assert config().app.env == "dev"
