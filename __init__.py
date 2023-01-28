import quart.flask_patch  # flake8: noqa
from psycopg2cffi import compat

compat.register()
