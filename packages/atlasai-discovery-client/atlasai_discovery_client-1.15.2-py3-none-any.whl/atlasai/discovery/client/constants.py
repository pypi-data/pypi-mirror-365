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

import os

DEFAULT_PAGE_SIZE = int(os.getenv('DISCOVERY_DEFAULT_PAGE_SIZE') or 100)
DEFAULT_OFFSET = 0

DESC = 'desc'
ASC = 'asc'

DISCOVERY_GRAPHQL_URL = 'DISCOVERY_GRAPHQL_URL'

DISCOVERY_ACCESS_KEY = 'DISCOVERY_ACCESS_KEY'
DISCOVERY_SECRET_KEY = 'DISCOVERY_SECRET_KEY'
DISCOVERY_BEARER_TOKEN = 'DISCOVERY_BEARER_TOKEN'

ATLASAI_ACCESS_KEY = 'ATLASAI_ACCESS_KEY'
ATLASAI_SECRET_KEY = 'ATLASAI_SECRET_KEY'
ATLASAI_BEARER_TOKEN = 'ATLASAI_BEARER_TOKEN'

ENABLE_DISCOVERY_READ_RETRIES = 'ENABLE_DISCOVERY_READ_RETRIES'
ENABLE_DISCOVERY_WRITE_RETRIES = 'ENABLE_DISCOVERY_WRITE_RETRIES'
DISABLE_SSL_VERIFICATION = 'DISABLE_SSL_VERIFICATION'
