# Copyright 2024 AtlasAI PBC. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from contextlib import contextmanager
from functools import wraps
import logging
import os
import time

from . import constants
from .environ import environment

MAX_ATTEMPTS_KEY = 'DISCOVERY_CLIENT_MAX_RETRY_ATTEMPTS'
MAX_ATTEMPTS = 5
if MAX_ATTEMPTS_KEY in os.environ:
    MAX_ATTEMPTS = os.environ[MAX_ATTEMPTS_KEY]

__all__ = [
    'retry',
    'enable_retry',
    'enable_write_retry',
]

logger = logging.getLogger(__name__)

class RetryOperation:
    def __init__(self, *error_types, attempts=None, backoff_factor=0.2):
        self.error_types = tuple(error_types or [Exception])
        self.attempts = attempts
        self.backoff_factor = backoff_factor

    @property
    def attempts(self):
        return self._attempts

    @attempts.setter
    def attempts(self, value):
        if value is None:
            value = MAX_ATTEMPTS

        assert isinstance(value, int), '`attempts` must be an integer'
        self._attempts = value

    def __call__(self, fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            num_attempts = 1
            if os.getenv(constants.ENABLE_DISCOVERY_READ_RETRIES):
                num_attempts = self.attempts

            attempt = 0
            while True:
                try:
                    result = fn(*args, **kwargs)
                except self.error_types as e:
                    attempt = self.prepare_for_next_attempt(
                        attempt,
                        num_attempts,
                        fn,
                        e
                    )
                else:
                    errors = result.get('errors') or []
                    if not errors:
                        return result

                    from . import endpoint
                    should_retry = any([
                        endpoint.can_retry(error)
                        for error in errors
                    ])
                    if not should_retry:
                        return result

                    try:
                        attempt = self.prepare_for_next_attempt(
                            attempt,
                            num_attempts,
                            fn,
                            errors
                        )
                    except StopIteration:
                        return result

        return wrapper

    def prepare_for_next_attempt(self, attempt, num_attempts, fn, error=None):
        attempt += 1
        if attempt >= num_attempts:
            if isinstance(error, Exception):
                raise error
            else:
                raise StopIteration()

        sleep_for = self.backoff_factor * pow(2, attempt)
        logger.info(f'Failed attempt #{attempt}. Retrying after sleeping for {sleep_for} seconds')
        if attempt / num_attempts >= 0.5:
            logger.info(f'Error from failed attempt #{attempt}: {fn} {error}')

        time.sleep(sleep_for)

        return attempt

retry = RetryOperation

@contextmanager
def enable_retry():
    with environment(**({
        constants.ENABLE_DISCOVERY_READ_RETRIES: '1'
    })):
        yield

@contextmanager
def enable_write_retry():
    with environment(**({
        constants.ENABLE_DISCOVERY_WRITE_RETRIES: '1'
    })):
        yield
