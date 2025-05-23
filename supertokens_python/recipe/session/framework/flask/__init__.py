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
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, TypeVar, Union, cast

from supertokens_python import Supertokens
from supertokens_python.async_to_sync_wrapper import sync
from supertokens_python.exceptions import SuperTokensError
from supertokens_python.framework.flask.flask_request import FlaskRequest
from supertokens_python.framework.flask.flask_response import FlaskResponse
from supertokens_python.recipe.session import SessionContainer, SessionRecipe
from supertokens_python.recipe.session.interfaces import SessionClaimValidator
from supertokens_python.types import MaybeAwaitable
from supertokens_python.utils import set_request_in_user_context_if_not_defined

_T = TypeVar("_T", bound=Callable[..., Any])


def verify_session(
    anti_csrf_check: Union[bool, None] = None,
    session_required: bool = True,
    check_database: bool = False,
    override_global_claim_validators: Optional[
        Callable[
            [List[SessionClaimValidator], SessionContainer, Dict[str, Any]],
            MaybeAwaitable[List[SessionClaimValidator]],
        ]
    ] = None,
    user_context: Union[None, Dict[str, Any]] = None,
) -> Callable[[_T], _T]:
    _ = user_context

    def session_verify(f: _T) -> _T:
        @wraps(f)
        def wrapped_function(*args: Any, **kwargs: Any):
            nonlocal user_context
            from flask import make_response, request

            base_req = FlaskRequest(request)
            user_context = set_request_in_user_context_if_not_defined(
                user_context, base_req
            )

            recipe = SessionRecipe.get_instance()

            try:
                session = sync(
                    recipe.verify_session(
                        base_req,
                        anti_csrf_check,
                        session_required,
                        check_database,
                        override_global_claim_validators,
                        user_context,
                    )
                )
                if session is None:
                    if session_required:
                        raise Exception("Should never come here")
                    base_req.set_session_as_none()
                else:
                    base_req.set_session(session)

                response = f(*args, **kwargs)
                return make_response(response) if response is not None else None
            except SuperTokensError as e:
                response = FlaskResponse(make_response())
                result = sync(
                    Supertokens.get_instance().handle_supertokens_error(
                        base_req, e, response, user_context
                    )
                )
                if isinstance(result, FlaskResponse):
                    return result.response
                raise Exception("Should never come here")

        return cast(_T, wrapped_function)

    return session_verify
