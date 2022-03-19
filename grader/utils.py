from functools import wraps
import logging
from pathlib import Path


logger = logging.getLogger(__name__)

BASE_DIR = Path(Path(__file__).parents[1])


def retry(n_retries=5, handle_exc=Exception):
    """For API wrappers that may cause API errors, recursively retry `N` times."""

    def outer(method):
        @wraps(method)
        def wrapper(self, *args, **kwargs):
            for _ in range(n_retries):
                try:
                    result = method(self, *args, **kwargs)
                    return result
                except handle_exc as e:
                    logger.exception(
                        "method %s failed from exception %s. retrying %d more times",
                        method,
                        e,
                        n_retries,
                    )
            raise Exception(
                f"method {method} did not succeed after {n_retries} retries"
            )

        return wrapper

    return outer
