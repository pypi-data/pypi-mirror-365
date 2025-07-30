from __future__ import annotations

import datetime
from unittest.mock import MagicMock

import pytest
from asgiref.sync import sync_to_async
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from django.utils import timezone
from model_bakery import baker

from django_github_app.github import AsyncGitHubAPI
from django_github_app.models import EventLog
from django_github_app.models import Installation
from django_github_app.models import InstallationStatus
from django_github_app.models import Repository

from .utils import seq

pytestmark = pytest.mark.django_db


@pytest.fixture
def private_key():
    private_key = rsa.generate_private_key(
        public_exponent=65537, key_size=2048, backend=default_backend()
    )

    pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )

    return pem.decode("utf-8")


class TestEventLogManager:
    @pytest.mark.asyncio
    async def test_acreate_from_event(self, create_event):
        data = {"foo": "bar"}
        event = "baz"

        event_log = await EventLog.objects.acreate_from_event(
            create_event(event, **data)
        )

        assert event_log.event == event
        assert event_log.payload == data

    def test_create_from_event(self, create_event):
        data = {"foo": "bar"}
        event = "baz"

        event_log = EventLog.objects.create_from_event(create_event(event, **data))

        assert event_log.event == event
        assert event_log.payload == data

    @pytest.mark.asyncio
    async def test_acleanup_events(self):
        days_to_cleanup = 7
        now = timezone.now()
        quantity = 5

        await sync_to_async(baker.make)(
            "django_github_app.EventLog",
            received_at=now - datetime.timedelta(days_to_cleanup + 1),
            _quantity=quantity,
        )

        deleted, _ = await EventLog.objects.acleanup_events(days_to_cleanup)

        assert deleted == quantity

    def test_cleanup_events(self):
        days_to_keep = 7
        now = timezone.now()
        quantity = 5

        baker.make(
            "django_github_app.EventLog",
            received_at=now - datetime.timedelta(days_to_keep + 1),
            _quantity=quantity,
        )

        deleted, _ = EventLog.objects.cleanup_events(days_to_keep)

        assert deleted == quantity


class TestEventLog:
    @pytest.mark.parametrize(
        "event,action,expected",
        [
            (None, None, "unknown"),
            ("foo", None, "foo"),
            ("foo", "bar", "foo bar"),
            (None, "bar", "unknown bar"),
        ],
    )
    def test_str(self, event, action, expected):
        event = baker.make(
            "django_github_app.EventLog", event=event, payload={"action": action}
        )

        assert str(event) == f"{event.pk} {expected}"

    @pytest.mark.parametrize(
        "payload,expected",
        [(None, None), ({"action": "foo"}, "foo")],
    )
    def test_action_property(self, payload, expected):
        event = baker.make("django_github_app.EventLog", payload=payload)

        assert event.action == expected


class TestInstallationManager:
    @pytest.mark.asyncio
    @pytest.mark.parametrize("app_settings_app_id_type", [int, str])
    async def test_acreate_from_event(
        self, app_settings_app_id_type, create_event, override_app_settings
    ):
        repositories = [
            {"id": seq.next(), "node_id": "node1", "full_name": "owner/repo1"},
            {"id": seq.next(), "node_id": "node2", "full_name": "owner/repo2"},
        ]
        installation_data = {
            "id": seq.next(),
            "app_id": seq.next(),
        }
        event = create_event(
            "installation",
            installation=installation_data,
            repositories=repositories,
        )

        with override_app_settings(
            APP_ID=installation_data["app_id"]
            if isinstance(app_settings_app_id_type, int)
            else str(installation_data["app_id"])
        ):
            installation = await Installation.objects.acreate_from_event(event)

        assert installation.installation_id == installation_data["id"]
        assert installation.data == installation_data
        assert await Repository.objects.filter(
            installation=installation
        ).acount() == len(repositories)

    @pytest.mark.parametrize("app_settings_app_id_type", [int, str])
    def test_create_from_event(
        self, app_settings_app_id_type, create_event, override_app_settings
    ):
        repositories = [
            {"id": seq.next(), "node_id": "node1", "full_name": "owner/repo1"},
            {"id": seq.next(), "node_id": "node2", "full_name": "owner/repo2"},
        ]
        installation_data = {
            "id": seq.next(),
            "app_id": seq.next(),
        }
        event = create_event(
            "installation",
            installation=installation_data,
            repositories=repositories,
        )

        with override_app_settings(
            APP_ID=installation_data["app_id"]
            if isinstance(app_settings_app_id_type, int)
            else str(installation_data["app_id"])
        ):
            installation = Installation.objects.create_from_event(event)

        assert installation.installation_id == installation_data["id"]
        assert installation.data == installation_data
        assert Repository.objects.filter(installation=installation).count() == len(
            repositories
        )

    @pytest.mark.asyncio
    async def test_acreate_from_gh_data(self):
        installation_data = {
            "id": seq.next(),
            "app_id": seq.next(),
        }

        installation = await Installation.objects.acreate_from_gh_data(
            installation_data
        )

        assert installation.installation_id == installation_data["id"]
        assert installation.data == installation_data

    def test_create_from_gh_data(self):
        installation_data = {
            "id": seq.next(),
            "app_id": seq.next(),
        }

        installation = Installation.objects.create_from_gh_data(installation_data)

        assert installation.installation_id == installation_data["id"]
        assert installation.data == installation_data

    @pytest.mark.asyncio
    async def test_aget_from_event(self, ainstallation, create_event):
        event = create_event(
            "installation", installation={"id": ainstallation.installation_id}
        )

        result = await Installation.objects.aget_from_event(event)

        assert result == ainstallation

    @pytest.mark.asyncio
    async def test_aget_from_event_doesnotexist(self, installation_id, create_event):
        event = create_event("installation", installation={"id": installation_id})

        installation = await Installation.objects.aget_from_event(event)

        assert installation is None

    def test_get_from_event(self, installation, create_event):
        event = create_event(
            "installation", installation={"id": installation.installation_id}
        )

        result = Installation.objects.get_from_event(event)

        assert result == installation

    @pytest.mark.asyncio
    async def test_aget_or_create_from_event_existing(
        self, ainstallation, create_event
    ):
        event = create_event(
            "installation_repositories",
            installation={"id": ainstallation.installation_id, "app_id": seq.next()},
        )

        result = await Installation.objects.aget_or_create_from_event(event)

        assert result == ainstallation

    @pytest.mark.asyncio
    async def test_aget_or_create_from_event_new(
        self, create_event, override_app_settings
    ):
        installation_id = seq.next()
        app_id = seq.next()
        installation_data = {
            "id": installation_id,
            "app_id": app_id,
            "account": {"login": "testorg", "type": "Organization"},
        }
        event = create_event(
            "installation_repositories",
            installation=installation_data,
            repositories_added=[],
            repositories_removed=[],
        )

        assert not await Installation.objects.filter(
            installation_id=installation_id
        ).aexists()

        with override_app_settings(APP_ID=str(app_id)):
            result = await Installation.objects.aget_or_create_from_event(event)

        assert result is not None
        assert result.installation_id == installation_id
        assert result.data == installation_data

    @pytest.mark.asyncio
    async def test_aget_or_create_from_event_wrong_app_id(
        self, create_event, override_app_settings
    ):
        installation_data = {
            "id": seq.next(),
            "app_id": seq.next(),
        }
        event = create_event(
            "installation_repositories",
            installation=installation_data,
        )

        with override_app_settings(APP_ID="999999"):
            result = await Installation.objects.aget_or_create_from_event(event)

        assert result is None

    def test_get_or_create_from_event_existing(self, installation, create_event):
        event = create_event(
            "installation_repositories",
            installation={"id": installation.installation_id, "app_id": seq.next()},
        )

        result = Installation.objects.get_or_create_from_event(event)

        assert result == installation

    def test_get_or_create_from_event_new(self, create_event, override_app_settings):
        installation_id = seq.next()
        app_id = seq.next()
        installation_data = {
            "id": installation_id,
            "app_id": app_id,
            "account": {"login": "testorg", "type": "Organization"},
        }
        event = create_event(
            "installation_repositories",
            installation=installation_data,
            repositories_added=[],
            repositories_removed=[],
        )

        assert not Installation.objects.filter(installation_id=installation_id).exists()

        with override_app_settings(APP_ID=str(app_id)):
            result = Installation.objects.get_or_create_from_event(event)

        assert result is not None
        assert result.installation_id == installation_id
        assert result.data == installation_data

    def test_get_or_create_from_event_wrong_app_id(
        self, create_event, override_app_settings
    ):
        installation_data = {
            "id": seq.next(),
            "app_id": seq.next(),
        }
        event = create_event(
            "installation_repositories",
            installation=installation_data,
        )

        with override_app_settings(APP_ID="999999"):
            result = Installation.objects.get_or_create_from_event(event)

        assert result is None


class TestInstallationStatus:
    @pytest.mark.parametrize(
        "action,expected",
        [
            ("deleted", InstallationStatus.INACTIVE),
            ("suspend", InstallationStatus.INACTIVE),
            ("created", InstallationStatus.ACTIVE),
            ("new_permissions_accepted", InstallationStatus.ACTIVE),
            ("unsuspend", InstallationStatus.ACTIVE),
        ],
    )
    def test_from_event(self, action, expected, create_event):
        event = create_event("installation", action=action)

        assert InstallationStatus.from_event(event) == expected

    def test_from_event_invalid_action(self, create_event):
        event = create_event("installation", action="invalid")

        with pytest.raises(ValueError):
            InstallationStatus.from_event(event)


class TestInstallation:
    def test_get_gh_client(self, installation):
        client = installation.get_gh_client()

        assert isinstance(client, AsyncGitHubAPI)
        assert client.installation_id == installation.installation_id

    @pytest.mark.parametrize("account_type", ["org", "user"])
    @pytest.mark.asyncio
    async def test_arefresh_from_gh(
        self,
        account_type,
        private_key,
        ainstallation,
        aget_mock_github_api,
        override_app_settings,
    ):
        mock_github_api = aget_mock_github_api({"foo": "bar"})
        ainstallation.get_gh_client = MagicMock(return_value=mock_github_api)

        with override_app_settings(PRIVATE_KEY=private_key):
            await ainstallation.arefresh_from_gh(account_type, "test")

        assert ainstallation.data == {"foo": "bar"}

    @pytest.mark.parametrize("account_type", ["org", "user"])
    def test_refresh_from_gh(
        self,
        account_type,
        private_key,
        installation,
        get_mock_github_api,
        override_app_settings,
    ):
        mock_github_api = get_mock_github_api({"foo": "bar"})
        installation.get_gh_client = MagicMock(return_value=mock_github_api)

        with override_app_settings(PRIVATE_KEY=private_key):
            installation.refresh_from_gh(account_type, "test")

        assert installation.data == {"foo": "bar"}

    def test_refresh_from_gh_invalid_account_type(self, installation):
        with pytest.raises(ValueError):
            installation.refresh_from_gh("invalid", "test")

    @pytest.mark.asyncio
    async def test_aget_repos(self, ainstallation):
        repos = await ainstallation.aget_repos()

        assert len(repos) == 2
        assert repos[0]["node_id"] == "node1"
        assert repos[0]["full_name"] == "owner/repo1"
        assert repos[1]["node_id"] == "node2"
        assert repos[1]["full_name"] == "owner/repo2"

    def test_get_repos(self, installation):
        repos = installation.get_repos()

        assert len(repos) == 2
        assert repos[0]["node_id"] == "node1"
        assert repos[0]["full_name"] == "owner/repo1"
        assert repos[1]["node_id"] == "node2"
        assert repos[1]["full_name"] == "owner/repo2"

    def test_app_slug(self):
        app_slug = "foo"
        installation = baker.make(
            "django_github_app.Installation",
            installation_id=seq.next(),
            data={"app_slug": app_slug},
        )

        assert installation.app_slug == app_slug


class TestRepositoryManager:
    @pytest.mark.asyncio
    async def test_acreate_from_gh_data_list(self, ainstallation):
        data = [
            {"id": seq.next(), "node_id": "node1", "full_name": "owner/repo1"},
            {"id": seq.next(), "node_id": "node2", "full_name": "owner/repo2"},
        ]

        repositories = await Repository.objects.acreate_from_gh_data(
            data, ainstallation
        )

        assert len(repositories) == len(data)
        for i, repo in enumerate(repositories):
            assert repo.repository_id == data[i]["id"]
            assert repo.repository_node_id == data[i]["node_id"]
            assert repo.full_name == data[i]["full_name"]
            assert repo.installation_id == ainstallation.id

    def test_create_from_gh_data_list(self, installation):
        data = [
            {"id": seq.next(), "node_id": "node1", "full_name": "owner/repo1"},
            {"id": seq.next(), "node_id": "node2", "full_name": "owner/repo2"},
        ]

        repositories = Repository.objects.create_from_gh_data(data, installation)

        assert len(repositories) == len(data)
        for i, repo in enumerate(repositories):
            assert repo.repository_id == data[i]["id"]
            assert repo.repository_node_id == data[i]["node_id"]
            assert repo.full_name == data[i]["full_name"]
            assert repo.installation_id == installation.id

    @pytest.mark.asyncio
    async def test_acreate_from_gh_data_single(self, ainstallation):
        data = {"id": seq.next(), "node_id": "node1", "full_name": "owner/repo1"}

        repository = await Repository.objects.acreate_from_gh_data(data, ainstallation)

        assert repository.repository_id == data["id"]
        assert repository.repository_node_id == data["node_id"]
        assert repository.full_name == data["full_name"]
        assert repository.installation_id == ainstallation.id

    def test_create_from_gh_data_single(self, installation):
        data = {"id": seq.next(), "node_id": "node1", "full_name": "owner/repo1"}

        repository = Repository.objects.create_from_gh_data(data, installation)

        assert repository.repository_id == data["id"]
        assert repository.repository_node_id == data["node_id"]
        assert repository.full_name == data["full_name"]
        assert repository.installation_id == installation.id

    @pytest.mark.asyncio
    async def test_aget_from_event(self, arepository, create_event):
        data = {
            "repository": {
                "id": arepository.repository_id,
                "node_id": arepository.repository_node_id,
                "full_name": arepository.full_name,
            }
        }

        repo = await Repository.objects.aget_from_event(
            create_event("repository", **data)
        )

        assert repo.repository_id == data["repository"]["id"]
        assert repo.repository_node_id == data["repository"]["node_id"]
        assert repo.full_name == data["repository"]["full_name"]
        assert repo.installation_id == arepository.installation.id

    @pytest.mark.asyncio
    async def test_aget_from_event_doesnotexist(self, repository_id, create_event):
        data = {
            "repository": {
                "id": repository_id,
            }
        }

        repo = await Repository.objects.aget_from_event(
            create_event("repository", **data)
        )

        assert repo is None

    def test_get_from_event(self, repository, create_event):
        data = {
            "repository": {
                "id": repository.repository_id,
                "node_id": repository.repository_node_id,
                "full_name": repository.full_name,
            }
        }

        repo = Repository.objects.get_from_event(create_event("repository", **data))

        assert repo.repository_id == data["repository"]["id"]
        assert repo.repository_node_id == data["repository"]["node_id"]
        assert repo.full_name == data["repository"]["full_name"]
        assert repo.installation_id == repository.installation.id

    def test_sync_repositories_from_event(self, installation, create_event):
        existing_repo = baker.make(
            "django_github_app.Repository",
            installation=installation,
            repository_id=seq.next(),
            repository_node_id="existing_node",
            full_name="owner/existing",
        )
        repo_to_remove = baker.make(
            "django_github_app.Repository",
            installation=installation,
            repository_id=seq.next(),
            repository_node_id="remove_node",
            full_name="owner/to_remove",
        )

        event = create_event(
            "installation_repositories",
            installation={"id": installation.installation_id},
            repositories_added=[
                {
                    "id": existing_repo.repository_id,
                    "node_id": "existing_node",
                    "full_name": "owner/existing",
                },
                {
                    "id": seq.next(),
                    "node_id": "new_node",
                    "full_name": "owner/new",
                },
            ],
            repositories_removed=[
                {"id": repo_to_remove.repository_id},
            ],
        )

        Repository.objects.sync_repositories_from_event(event)

        assert Repository.objects.filter(
            repository_id=existing_repo.repository_id
        ).exists()
        assert not Repository.objects.filter(
            repository_id=repo_to_remove.repository_id
        ).exists()
        assert Repository.objects.filter(full_name="owner/new").exists()
        assert Repository.objects.filter(installation=installation).count() == 2

    @pytest.mark.asyncio
    async def test_async_repositories_from_event(self, ainstallation, create_event):
        existing_repo = await sync_to_async(baker.make)(
            "django_github_app.Repository",
            installation=ainstallation,
            repository_id=seq.next(),
            repository_node_id="existing_node",
            full_name="owner/existing",
        )
        repo_to_remove = await sync_to_async(baker.make)(
            "django_github_app.Repository",
            installation=ainstallation,
            repository_id=seq.next(),
            repository_node_id="remove_node",
            full_name="owner/to_remove",
        )

        event = create_event(
            "installation_repositories",
            installation={"id": ainstallation.installation_id},
            repositories_added=[
                {
                    "id": existing_repo.repository_id,
                    "node_id": "existing_node",
                    "full_name": "owner/existing",
                },
                {
                    "id": seq.next(),
                    "node_id": "new_node",
                    "full_name": "owner/new",
                },
            ],
            repositories_removed=[
                {"id": repo_to_remove.repository_id},
            ],
        )

        await Repository.objects.async_repositories_from_event(event)

        assert await Repository.objects.filter(
            repository_id=existing_repo.repository_id
        ).aexists()
        assert not await Repository.objects.filter(
            repository_id=repo_to_remove.repository_id
        ).aexists()
        assert await Repository.objects.filter(full_name="owner/new").aexists()
        assert await Repository.objects.filter(installation=ainstallation).acount() == 2

    def test_sync_repositories_from_event_wrong_event_type(self, create_event):
        event = create_event("push")

        with pytest.raises(
            ValueError, match="Expected 'installation_repositories' event"
        ):
            Repository.objects.sync_repositories_from_event(event)

    @pytest.mark.asyncio
    async def test_async_repositories_from_event_wrong_event_type(self, create_event):
        event = create_event("push")

        with pytest.raises(
            ValueError, match="Expected 'installation_repositories' event"
        ):
            await Repository.objects.async_repositories_from_event(event)


class TestRepository:
    def test_get_gh_client(self, repository):
        client = repository.get_gh_client()

        assert isinstance(client, AsyncGitHubAPI)
        assert client.installation_id == repository.installation.installation_id

    @pytest.mark.asyncio
    async def test_aget_issues(self, arepository):
        issues = await arepository.aget_issues()

        assert len(issues) == 2
        assert issues[0]["number"] == 1
        assert issues[0]["title"] == "Test Issue 1"
        assert issues[1]["number"] == 2
        assert issues[1]["title"] == "Test Issue 2"

    def test_get_issues(self, repository):
        issues = repository.get_issues()

        assert len(issues) == 2
        assert issues[0]["number"] == 1
        assert issues[0]["title"] == "Test Issue 1"
        assert issues[1]["number"] == 2
        assert issues[1]["title"] == "Test Issue 2"
