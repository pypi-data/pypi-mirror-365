# Welcome to Pokie-gunicorn

[![pypi](https://img.shields.io/pypi/v/pokie-gunicorn.svg)](https://pypi.org/project/pokie-gunicorn/)
[![license](https://img.shields.io/pypi/l/pokie-gunicorn.svg)](https://git.oddbit.org/OddBit/pokie-gunicorn/src/branch/master/LICENSE)

Run a pokie application with an embedded gunicorn server

## Defaults

When running with no configuration, it will assume the following options:

- workers: (cpu_count * 2) + 1
- bind: localhost:5000
- threads: cpu_count * 4
- keepalive: 2



## Configuration

All gunicorn settings can be used by setting GUNICORN_<UPPERCASE_SETTING> env var, or by providing them via config provider
with a gunicorn_ prefix. 

The class *pokie_gunicorn.config.GunicornConfigTemplate* contains the basic options, but
can be extended to include most of the options from [Gunicorn's configuration](https://docs.gunicorn.org/en/stable/settings.html#config).




