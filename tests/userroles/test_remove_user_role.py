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

from pytest import mark, skip
from supertokens_python import InputAppInfo, SupertokensConfig, init
from supertokens_python.querier import Querier
from supertokens_python.recipe import session, userroles
from supertokens_python.recipe.userroles import asyncio, interfaces
from supertokens_python.utils import is_version_gte

from tests.utils import get_new_core_app_url


@mark.asyncio
async def test_remove_role_from_a_user():
    init(
        supertokens_config=SupertokensConfig(get_new_core_app_url()),
        app_info=InputAppInfo(
            app_name="SuperTokens Demo",
            api_domain="https://api.supertokens.io",
            website_domain="supertokens.io",
        ),
        framework="fastapi",
        recipe_list=[
            userroles.init(),
            session.init(get_token_transfer_method=lambda _, __, ___: "cookie"),
        ],
    )

    version = await Querier.get_instance().get_api_version()
    if not is_version_gte(version, "2.14"):
        # If the version less than 2.14, user roles recipe doesn't exist. So skip the test
        skip()

    user_id = "user_id"
    role = "role"

    # Create new role:
    result = await asyncio.create_new_role_or_add_permissions(role, [])
    assert isinstance(result, interfaces.CreateNewRoleOrAddPermissionsOkResult)
    assert result.created_new_role

    # Add role to the user:
    result = await asyncio.add_role_to_user("public", user_id, role)
    assert isinstance(result, interfaces.AddRoleToUserOkResult)
    assert not result.did_user_already_have_role

    # Check that user has a role:
    result = await asyncio.get_roles_for_user("public", user_id)
    assert isinstance(result, interfaces.GetRolesForUserOkResult)
    assert result.roles == [role]

    # Remove role from the user:
    result = await asyncio.remove_user_role("public", user_id, role)
    assert isinstance(result, interfaces.RemoveUserRoleOkResult)
    assert result.did_user_have_role

    # Check that the permission has been removed from the role:
    result = await asyncio.get_roles_for_user("public", user_id)
    assert isinstance(result, interfaces.GetRolesForUserOkResult)
    assert result.roles == []


@mark.asyncio
async def test_remove_unassigned_role_from_user():
    init(
        supertokens_config=SupertokensConfig(get_new_core_app_url()),
        app_info=InputAppInfo(
            app_name="SuperTokens Demo",
            api_domain="https://api.supertokens.io",
            website_domain="supertokens.io",
        ),
        framework="fastapi",
        recipe_list=[
            userroles.init(),
            session.init(get_token_transfer_method=lambda _, __, ___: "cookie"),
        ],
    )

    version = await Querier.get_instance().get_api_version()
    if not is_version_gte(version, "2.14"):
        # If the version less than 2.14, user roles recipe doesn't exist. So skip the test
        skip()

    user_id = "user_id"
    role = "role"

    # Create new role:
    result = await asyncio.create_new_role_or_add_permissions(role, [])
    assert isinstance(result, interfaces.CreateNewRoleOrAddPermissionsOkResult)
    assert result.created_new_role

    # Remove (unassigned) role from the user:
    result = await asyncio.remove_user_role("public", user_id, role)
    assert isinstance(result, interfaces.RemoveUserRoleOkResult)
    assert not result.did_user_have_role


@mark.asyncio
async def test_remove_non_existent_role_from_user():
    init(
        supertokens_config=SupertokensConfig(get_new_core_app_url()),
        app_info=InputAppInfo(
            app_name="SuperTokens Demo",
            api_domain="https://api.supertokens.io",
            website_domain="supertokens.io",
        ),
        framework="fastapi",
        recipe_list=[
            userroles.init(),
            session.init(get_token_transfer_method=lambda _, __, ___: "cookie"),
        ],
    )

    version = await Querier.get_instance().get_api_version()
    if not is_version_gte(version, "2.14"):
        # If the version less than 2.14, user roles recipe doesn't exist. So skip the test
        skip()

    user_id = "user_id"
    role = "role"

    # Remove (non-existent) role from the user:
    result = await asyncio.remove_user_role("public", user_id, role)
    assert isinstance(result, interfaces.UnknownRoleError)
