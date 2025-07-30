from __future__ import annotations

import pytest
from asgiref.sync import sync_to_async
from model_bakery import baker

from django_github_app.events.arepository import arename_repository
from django_github_app.models import Repository
from tests.utils import seq

pytestmark = [pytest.mark.asyncio, pytest.mark.django_db]


async def test_arename_repository(ainstallation, repository_id, create_event):
    repository = await sync_to_async(baker.make)(
        "django_github_app.Repository",
        installation=ainstallation,
        repository_id=repository_id,
        full_name=f"owner/old_name_{seq.next()}",
    )

    data = {
        "repository": {
            "id": repository.repository_id,
            "full_name": f"owner/new_name_{seq.next()}",
        },
    }
    event = create_event("repository", delivery_id="1234", **data)

    assert not await Repository.objects.filter(
        full_name=data["repository"]["full_name"]
    ).aexists()

    await arename_repository(event, None)

    assert await Repository.objects.filter(
        full_name=data["repository"]["full_name"]
    ).aexists()
