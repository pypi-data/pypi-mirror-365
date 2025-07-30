import os
import pytest
from rick.resource.config import EnvironmentConfig
from rick.base import ShallowContainer


class ConfigTest1(EnvironmentConfig):
    OPTION_1 = None
    OPTION_2 = "x"
    OPTION_3 = "xyz"


class ConfigTest2(EnvironmentConfig):
    FOO_LIST = []
    FOO_INT = 1
    FOO_STR = None
    FOO_DICT = {}


fixture_configtest_prefix = [
    (ConfigTest1, {"PREFIX_OPTION_1": "abc", "PREFIX_OPTION_2": "def"})
]

fixtures = [
    [  # simple override
        ConfigTest1,
        {"OPTION_1": "abc", "OPTION_2": "def"},
        {"option_1": "abc", "option_2": "def", "option_3": "xyz"},
        "",  # no prefix
    ],
    [  # simple override
        ConfigTest1,
        {"PREFIX_OPTION_1": "abc", "PREFIX_OPTION_2": "def"},
        {"option_1": "abc", "option_2": "def", "option_3": "xyz"},
        "PREFIX_",  # no prefix
    ],
    [  # multiple types
        ConfigTest2,
        {  # env vars
            "FOO_LIST": "abc,def",
            "FOO_INT": "5",
            "FOO_STR": "joe",
            "FOO_DICT": '{"key":"value"}',
        },  # expected result
        {
            "foo_list": ["abc", "def"],
            "foo_int": 5,
            "foo_str": "joe",
            "foo_dict": {"key": "value"},
        },
        "",  # no prefix
    ],
]


@pytest.mark.parametrize("cls,env_vars, expected_result, prefix", fixtures)
def test_EnvConfig_types(cls, env_vars: dict, expected_result: dict, prefix: str):
    obj = cls()

    # first, check that build() processes correctly without any set env variables
    cfg = obj.build(prefix)
    for name in dir(obj):
        if name.isupper():
            value = cfg.get(name.lower())
            if isinstance(value, ShallowContainer):
                # unrap dict from ShallowContainer
                value = value.asdict()
            assert value == getattr(obj, name)

    # now set env variables
    for name, value in env_vars.items():
        os.environ[name] = str(value)

    # re-build cfg with overriden values
    cfg = obj.build()
    # verify overriden values match expected values
    for name in expected_result.keys():
        value = cfg.get(name)
        if isinstance(value, ShallowContainer):
            value = value.asdict()
        assert value == expected_result[name]
