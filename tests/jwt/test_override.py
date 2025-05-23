"""
Copyright (c) 2020, VRAI Labs and/or its affiliates. All rights reserved.

This software is licensed under the Apache License, Version 2.0 (the
"License") as published by the Apache Software Foundation.

You may not use this file except in compliance with the License. You may
obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
License for the specific language governing permissions and limitations
under the License.
"""

from typing import Any, Dict, List, Union

from _pytest.fixtures import fixture
from fastapi import FastAPI
from pytest import mark
from starlette.requests import Request
from starlette.testclient import TestClient
from supertokens_python import InputAppInfo, SupertokensConfig, init
from supertokens_python.framework.fastapi import get_middleware
from supertokens_python.recipe import jwt
from supertokens_python.recipe.jwt.asyncio import create_jwt
from supertokens_python.recipe.jwt.interfaces import (
    APIInterface,
    APIOptions,
    CreateJwtOkResult,
    RecipeInterface,
)

from tests.utils import get_new_core_app_url


@fixture(scope="function")
def driver_config_client():
    app = FastAPI()
    app.add_middleware(get_middleware())

    @app.post("/jwtcreate")
    async def jwt_create(request: Request):  # type: ignore
        payload = (await request.json())["payload"]
        response = await create_jwt(payload, 1000)
        return response

    return TestClient(app)


@mark.asyncio
async def test_that_default_getJWKS_api_does_not_work_when_disabled(
    driver_config_client: TestClient,
):
    created_jwt = None
    jwt_keys: List[Dict[str, Any]] = []

    def custom_functions(param: RecipeInterface):
        temp = param.get_jwks

        async def get_jwks(user_context: Dict[str, Any]):
            response_ = await temp(user_context)

            for key in response_.keys:
                jwt_keys.append(
                    {
                        "kty": key.kty,
                        "kid": key.kid,
                        "n": key.n,
                        "e": key.e,
                        "alg": key.alg,
                        "use": key.use,
                    }
                )

            return response_

        oi_create_jwt = param.create_jwt

        async def create_jwt_(
            payload: Dict[str, Any],
            validity_seconds: Union[int, None],
            use_static_signing_key: Union[bool, None],
            user_context: Dict[str, Any],
        ):
            response_ = await oi_create_jwt(
                payload, validity_seconds, use_static_signing_key, user_context
            )

            if isinstance(response_, CreateJwtOkResult):
                nonlocal created_jwt
                created_jwt = response_.jwt

            return response_

        param.create_jwt = create_jwt_
        param.get_jwks = get_jwks
        return param

    init(
        supertokens_config=SupertokensConfig(get_new_core_app_url()),
        app_info=InputAppInfo(
            app_name="SuperTokens Demo",
            api_domain="http://api.supertokens.io",
            website_domain="supertokens.io",
        ),
        framework="fastapi",
        recipe_list=[jwt.init(override=jwt.OverrideConfig(functions=custom_functions))],
    )

    response = driver_config_client.post(
        url="/jwtcreate", json={"payload": {"someKey": "key"}}
    )

    assert response is not None
    assert response.json()["jwt"] == created_jwt

    response = driver_config_client.get(url="/auth/jwt/jwks.json")

    assert response is not None
    assert response.json()["keys"] == jwt_keys


@mark.asyncio
async def test_overriding_APIs(driver_config_client: TestClient):
    jwt_keys = None

    def custom_api(param: APIInterface):
        temp = param.jwks_get

        async def get_jwks_get(api_options: APIOptions, user_context: Dict[str, Any]):
            response_ = await temp(api_options, user_context)
            nonlocal jwt_keys
            jwt_keys = response_.to_json()["keys"]
            return response_

        param.jwks_get = get_jwks_get

        return param

    init(
        supertokens_config=SupertokensConfig(get_new_core_app_url()),
        app_info=InputAppInfo(
            app_name="SuperTokens Demo",
            api_domain="http://api.supertokens.io",
            website_domain="supertokens.io",
        ),
        framework="fastapi",
        recipe_list=[jwt.init(override=jwt.OverrideConfig(apis=custom_api))],
    )

    response = driver_config_client.get(url="/auth/jwt/jwks.json")

    assert response is not None
    assert response.json()["keys"] == jwt_keys
