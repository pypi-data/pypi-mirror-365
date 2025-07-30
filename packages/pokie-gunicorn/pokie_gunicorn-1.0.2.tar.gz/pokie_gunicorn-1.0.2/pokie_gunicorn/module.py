from pokie.core import BaseModule


class Module(BaseModule):
    name = "pokie_gunicorn"
    description = "Gunicorn server integration"

    cmd = {
        "gunicorn:run": "pokie_gunicorn.cli.RunCmd",
    }
