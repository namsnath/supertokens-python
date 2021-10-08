"""
Copyright (c) 2021, VRAI Labs and/or its affiliates. All rights reserved.

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
from __future__ import annotations
from httpx import AsyncClient
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from supertokens_python.supertokens import AppInfo
    from .types import User
    from .interfaces import RecipeInterface, APIInterface
    from typing import Callable, Union
from os import environ


def default_get_email_verification_url(app_info: AppInfo):
    async def func(_: User):
        return app_info.website_domain.get_as_string_dangerous(
        ) + app_info.website_base_path.get_as_string_dangerous() + '/verify-email'
    return func


def default_create_and_send_custom_email(app_info: AppInfo):
    async def func(user: User, email_verification_url: str):
        if ('SUPERTOKENS_ENV' not in environ) or (
                environ['SUPERTOKENS_ENV'] != 'testing'):
            return
        try:
            await AsyncClient().post('https://api.supertokens.io/0/st/auth/email/verify', json={'email': user.email, 'appName': app_info.app_name, 'emailVerifyURL': email_verification_url}, headers={'api-version': '0'})
        except Exception:
            pass
    return func


class OverrideConfig:
    def __init__(self, functions: Union[Callable[[RecipeInterface], RecipeInterface],
                 None], apis: Union[Callable[[APIInterface], APIInterface], None]):
        self.functions = functions
        self.apis = apis


class EmailVerificationConfig:
    def __init__(self,
                 get_email_for_user_id,
                 get_email_verification_url,
                 create_and_send_custom_email,
                 override: OverrideConfig
                 ):
        self.get_email_for_user_id = get_email_for_user_id
        self.get_email_verification_url = get_email_verification_url
        self.create_and_send_custom_email = create_and_send_custom_email
        self.override = override


def validate_and_normalise_user_input(app_info: AppInfo, config):
    get_email_verification_url = config[
        'get_email_verification_url'] if 'get_email_verification_url' in config and config['get_email_verification_url'] is not None else default_get_email_verification_url(
        app_info)
    create_and_send_custom_email = config[
        'create_and_send_custom_email'] if 'create_and_send_custom_email' in config and config[
        'create_and_send_custom_email'] is not None else default_create_and_send_custom_email(
        app_info)
    get_email_for_user_id = config['get_email_for_user_id']
    override_functions = config['override']['functions'] if 'override' in config and 'functions' in config[
        'override'] else None
    override_apis = config['override']['apis'] if 'override' in config and 'apis' in config[
        'override'] else None
    override = OverrideConfig(override_functions, override_apis)

    return EmailVerificationConfig(
        get_email_for_user_id,
        get_email_verification_url,
        create_and_send_custom_email,
        override
    )