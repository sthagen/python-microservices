import json
import functools
from contextlib import contextmanager
from typing import Any, Dict, Optional, List
from starlette.requests import Request
from fastapi.security import SecurityScopes
from authlib.oauth2 import ResourceProtector as _ResourceProtector
from authlib.oauth2.rfc6749 import MissingAuthorizationError
from .models import OAuth2AuthorizationCodeBearer
from .logging import OAuth2Audit


class ResourceProtector(_ResourceProtector, OAuth2AuthorizationCodeBearer):
    """A protecting method for resource servers. Creating a ``require_oauth``
    decorator easily with ResourceProtector
    """
    def __init__(
        self,
        authorization_url: str,
        token_url: str,
        refresh_url: str = None,
        scopes: dict = {},
        auto_error: bool = True
    ):
        _ResourceProtector.__init__(self)
        OAuth2AuthorizationCodeBearer.__init__(
            self, authorization_url, token_url, refresh_url, scopes, auto_error
        )

    @OAuth2Audit()
    async def acquire_token(
        self, request: Request, scope: SecurityScopes = None, operator: str = 'AND'
    ):
        """A method to acquire current valid token with the given scope.

        :param request: FastAPI HTTP request instance
        :param scope: string of space delimted scope values
        :param operator: value of "AND" or "OR"
        :return: token object
        """
        if not callable(operator):
            operator = operator.upper()
        token = self.validate_request(scope.scope_str, request, operator)
        return token

    async def __call__(
        self,
        request: Request,
        scope: SecurityScopes = None,
        operator: str = 'AND',
        optional: bool = False
    ):
        return await self.acquire_token(request, scope, operator)
