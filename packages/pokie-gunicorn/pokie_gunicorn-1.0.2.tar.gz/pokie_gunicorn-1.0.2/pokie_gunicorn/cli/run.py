import os
import multiprocessing
import gunicorn.app.base
from argparse import ArgumentParser

from pokie.constants import DI_SERVICES, DI_FLASK, DI_CONFIG
from pokie.core import CliCommand
import __main__


class GunicornApp(gunicorn.app.base.BaseApplication):
    def __init__(self, factory, options=None):
        self.options = options or {}
        self.factory = factory
        super().__init__()

    def load_config(self):
        config = {
            key: value
            for key, value in self.options.items()
            if key in self.cfg.settings and value is not None
        }
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        _, app = self.factory()
        return app


class RunCmd(CliCommand):
    BUILDER_FN = "build_pokie"
    ENV_PREFIX = "GUNICORN_"
    description = "run gunicorn server"

    def run(self, args) -> bool:
        if not callable(getattr(__main__, self.BUILDER_FN, None)):
            self.tty.error(
                "Error: missing factory {}() in the main application file".format(
                    self.BUILDER_FN
                )
            )
            return False

        self.tty.write("Running gunicorn...")
        options = {
            "bind": "%s:%s" % ("localhost", "5000"),
            "workers": (multiprocessing.cpu_count() * 2) + 1,
            "threads": (multiprocessing.cpu_count() * 4),
            "accesslog": "-",
            "errorlog": "-",
            "loglevel": "debug",
        }

        found_config = False

        # first, lookup for gunicorn_ vars in pokie config
        conf_prefix = self.ENV_PREFIX.lower()
        cfg = self.get_di().get(DI_CONFIG)
        for name in cfg.keys():
            if name.startswith(conf_prefix):
                var_name = name[len(conf_prefix) :]
                options[var_name] = cfg.get(name)
                found_config = True

        if not found_config:
            # if not found in config, lookup for GUNICORN_ vars in env
            for name, value in os.environ.items():
                if name.startswith(self.ENV_PREFIX):
                    var_name = name[len(self.ENV_PREFIX) :].lower()
                    options[var_name] = value

        GunicornApp(getattr(__main__, self.BUILDER_FN), options).run()

        return True
