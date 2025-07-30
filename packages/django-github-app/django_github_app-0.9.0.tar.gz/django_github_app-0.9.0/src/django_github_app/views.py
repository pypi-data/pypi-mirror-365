from __future__ import annotations

import time
from abc import ABC
from abc import abstractmethod
from collections.abc import Coroutine
from typing import Any
from typing import Generic
from typing import TypeVar

import gidgethub
from django.core.exceptions import BadRequest
from django.http import HttpRequest
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
from gidgethub.sansio import Event

from ._typing import override
from .conf import app_settings
from .github import AsyncGitHubAPI
from .github import SyncGitHubAPI
from .models import EventLog
from .models import Installation
from .routing import GitHubRouter

GitHubAPIType = TypeVar("GitHubAPIType", AsyncGitHubAPI, SyncGitHubAPI)

_router = GitHubRouter(*GitHubRouter.routers)


class BaseWebhookView(View, ABC, Generic[GitHubAPIType]):
    github_api_class: type[GitHubAPIType]

    def get_event(self, request: HttpRequest) -> Event:
        try:
            event = Event.from_http(
                request.headers,
                request.body,
                secret=app_settings.WEBHOOK_SECRET,
            )
        except KeyError as err:
            raise BadRequest(f"Missing required header: {err}") from err
        except gidgethub.ValidationFailure as err:
            raise BadRequest(f"Invalid webhook: {err}") from err
        return event

    def get_github_api(self, installation: Installation | None) -> GitHubAPIType:
        requester = app_settings.SLUG
        installation_id = getattr(installation, "installation_id", None)
        return self.github_api_class(requester, installation_id=installation_id)

    def get_response(self, event_log: EventLog | None) -> JsonResponse:
        response_data: dict[str, int | str] = {"message": "ok"}
        if event_log:
            response_data["event_id"] = event_log.id
        return JsonResponse(response_data)

    @property
    def router(self) -> GitHubRouter:
        return _router

    @abstractmethod
    def post(
        self, request: HttpRequest
    ) -> JsonResponse | Coroutine[Any, Any, JsonResponse]: ...


@method_decorator(csrf_exempt, name="dispatch")
class AsyncWebhookView(BaseWebhookView[AsyncGitHubAPI]):
    github_api_class = AsyncGitHubAPI

    @override
    async def post(self, request: HttpRequest) -> JsonResponse:
        event = self.get_event(request)

        if app_settings.AUTO_CLEANUP_EVENTS:
            await EventLog.objects.acleanup_events()

        found_callbacks = self.router.fetch(event)

        event_log = None
        if app_settings.LOG_ALL_EVENTS or found_callbacks:
            event_log = await EventLog.objects.acreate_from_event(event)

        if found_callbacks:
            installation = await Installation.objects.aget_from_event(event)
            async with self.get_github_api(installation) as gh:
                await gh.sleep(1)
                await self.router.adispatch(event, gh)

        return self.get_response(event_log)


@method_decorator(csrf_exempt, name="dispatch")
class SyncWebhookView(BaseWebhookView[SyncGitHubAPI]):
    github_api_class = SyncGitHubAPI

    def post(self, request: HttpRequest) -> JsonResponse:  # pragma: no cover
        event = self.get_event(request)

        if app_settings.AUTO_CLEANUP_EVENTS:
            EventLog.objects.cleanup_events()

        found_callbacks = self.router.fetch(event)

        event_log = None
        if app_settings.LOG_ALL_EVENTS or found_callbacks:
            event_log = EventLog.objects.create_from_event(event)

        if found_callbacks:
            installation = Installation.objects.get_from_event(event)
            with self.get_github_api(installation) as gh:
                time.sleep(1)
                self.router.dispatch(event, gh)

        return self.get_response(event_log)
