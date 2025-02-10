# Copyright (c) 2021, VRAI Labs and/or its affiliates. All rights reserved.
#
# This software is licensed under the Apache License, Version 2.0 (the
# "License") as published by the Apache Software Foundation.
#
# You may not use this file except in compliance with the License. You may
# obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
from typing import Any, Dict, Optional, Union

from supertokens_python.async_to_sync_wrapper import sync
from supertokens_python.recipe.openid import asyncio
from supertokens_python.recipe.openid.interfaces import (
    GetOpenIdDiscoveryConfigurationResult,
)

from ...jwt.interfaces import (
    CreateJwtOkResult,
    CreateJwtResultUnsupportedAlgorithm,
    GetJWKSResult,
)


def create_jwt(
    payload: Optional[Dict[str, Any]] = None,
    validity_seconds: Optional[int] = None,
    use_static_signing_key: Optional[bool] = None,
    user_context: Optional[Dict[str, Any]] = None,
) -> Union[CreateJwtOkResult, CreateJwtResultUnsupportedAlgorithm]:
    return sync(
        asyncio.create_jwt(
            payload, validity_seconds, use_static_signing_key, user_context
        )
    )


def get_jwks(user_context: Optional[Dict[str, Any]] = None) -> GetJWKSResult:
    return sync(asyncio.get_jwks(user_context))


def get_open_id_discovery_configuration(
    user_context: Optional[Dict[str, Any]] = None,
) -> GetOpenIdDiscoveryConfigurationResult:
    return sync(asyncio.get_open_id_discovery_configuration(user_context))
