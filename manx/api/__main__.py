# Local imports
from .api import settings, run


if __name__ == "__main__":
    run(host=settings.API_HOST, port=settings.API_PORT)
