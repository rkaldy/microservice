from typing import Any

import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.starlette import StarletteIntegration
from sentry_sdk.types import Event, Hint

from src.settings.base import base_settings
from src.utils.exceptions import RetryableQueryError


def filter_exceptions(event: Event, hint: Hint) -> Event | None:
    if "exc_info" in hint:
        exception = hint["exc_info"][1]
        if isinstance(exception, RetryableQueryError):
            return None
    return event


def init_sentry(server_name: str, component: str) -> None:
    if not base_settings.SENTRY_DSN:
        return

    status_codes_to_sentry = [range(400, 403), range(404, 599)]
    sentry_sdk.init(
        dsn=base_settings.SENTRY_DSN,
        environment=base_settings.APP_ENV,
        server_name=server_name,
        integrations=[
            StarletteIntegration(
                transaction_style="endpoint",
                failed_request_status_codes=status_codes_to_sentry,
            ),
            FastApiIntegration(
                transaction_style="endpoint",
                failed_request_status_codes=status_codes_to_sentry,
            ),
        ],
        before_send=filter_exceptions,
    )
    sentry_sdk.set_tag("component", component)


def set_sentry_context(key: str, value: Any) -> None:
    if base_settings.SENTRY_DSN:
        sentry_sdk.set_context(key, value)
