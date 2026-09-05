from decouple import config

env = config("DJANGO_ENV", default="local")

if env == "production":
    from .prod import *
elif env == "local":
    from .local import *
elif env == "staging":
    from .staging import *
else:
    raise ValueError("Unknown environment")
