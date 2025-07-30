import multiprocessing


# pokie_gunicorn configuration
class GunicornConfigTemplate:
    GUNICORN_WORKERS = (multiprocessing.cpu_count() * 2) + 1
    GUNICORN_BIND = "localhost:5000"
    GUNICORN_THREADS = multiprocessing.cpu_count() * 4
    GUNICORN_KEEPALIVE = 2

    # other gunicorn options can be added by prefixing the option with GUNICORN_ and uppercasing the option name
    # alternatively, one can use env vars directly - see cli/run.py for more details
    #
    # Note: if any configuration option is found on the pokie config container (typically class-based), any further
    # detection of environment vars is skipped
    #
