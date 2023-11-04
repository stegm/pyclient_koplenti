"""Smoketest which are executed on a real inverter."""

import os
import re
from typing import AsyncGenerator
import aiohttp
import pytest
import pytest_asyncio

import pykoplenti


@pytest_asyncio.fixture
async def authenticated_client() -> AsyncGenerator[pykoplenti.ApiClient, None]:
    host = os.getenv("SMOKETEST_HOST")
    port = int(os.getenv("SMOKETEST_PORT"))
    password = os.getenv("SMOKETEST_PASS")

    async with aiohttp.ClientSession() as session:
        client = pykoplenti.ApiClient(session, host, port)
        await client.login(password)
        yield client
        await client.logout()


@pytest.mark.skipif(
    os.getenv("SMOKETEST_HOST") is None, reason="Smoketest must be explicitly executed"
)
class TestSmokeTests:
    """Contains smoke tests which are executed on a real inverter.

    This tests are not automatically executed because they need real HW. Please
    note that all checks are highl volatile because of different configuration and
    firmware version of the inverter.
    """

    @pytest.mark.asyncio
    async def test_smoketest_me(self, authenticated_client: pykoplenti.ApiClient):
        """Retrieves the MeData."""

        me = await authenticated_client.get_me()

        assert me == pykoplenti.MeData(
            locked=False,
            active=True,
            authenticated=True,
            permissions=[],
            anonymous=False,
            role="USER",
        )

    @pytest.mark.asyncio
    async def test_smoketest_version(self, authenticated_client: pykoplenti.ApiClient):
        """Retrieves the VersionData."""

        version = await authenticated_client.get_version()

        # version info are highly variable hence only some basic checks are performed
        assert len(version.hostname) > 0
        assert len(version.name) > 0
        assert re.match("\d+.\d+.\d+", version.api_version) is not None
        assert re.match("\d+.\d+.\d+", version.sw_version) is not None

    @pytest.mark.asyncio
    async def test_smoketest_modules(self, authenticated_client: pykoplenti.ApiClient):
        """Retrieves the ModuleData."""

        modules = await authenticated_client.get_modules()

        assert len(modules) >= 17
        assert pykoplenti.ModuleData(id="devices:local", type="device") in modules

    @pytest.mark.asyncio
    async def test_smoketest_settings(self, authenticated_client: pykoplenti.ApiClient):
        """Retrieves the SettingsData."""

        settings = await authenticated_client.get_settings()

        assert "devices:local" in settings
        assert (
            pykoplenti.SettingsData(
                min="0",
                max="32",
                default=None,
                access="readonly",
                unit=None,
                id="Branding:ProductName1",
                type="string",
            )
            in settings["devices:local"]
        )

    @pytest.mark.asyncio
    async def test_smoketest_setting_value1(
        self, authenticated_client: pykoplenti.ApiClient
    ):
        """Retrieves the setting value with variante 1."""

        setting_value = await authenticated_client.get_setting_values(
            "devices:local", "Branding:ProductName1"
        )

        assert setting_value == {
            "devices:local": {"Branding:ProductName1": "PLENTICORE plus"}
        }

    @pytest.mark.asyncio
    async def test_smoketest_setting_value2(
        self, authenticated_client: pykoplenti.ApiClient
    ):
        """Retrieves the setting value with variante 2."""

        setting_value = await authenticated_client.get_setting_values(
            "devices:local", ["Branding:ProductName1"]
        )

        assert setting_value == {
            "devices:local": {"Branding:ProductName1": "PLENTICORE plus"}
        }

    @pytest.mark.asyncio
    @pytest.mark.skip(reason="API endpoint is not working")
    async def test_smoketest_setting_value3(
        self, authenticated_client: pykoplenti.ApiClient
    ):
        """Retrieves the setting value with variante 3."""

        setting_value = await authenticated_client.get_setting_values(
            "devices:local", None
        )

        assert (
            setting_value["devices:local"]["Branding:ProductName1"] == "PLENTICORE plus"
        )

    @pytest.mark.asyncio
    async def test_smoketest_setting_value4(
        self, authenticated_client: pykoplenti.ApiClient
    ):
        """Retrieves the setting value with variante 4."""

        setting_value = await authenticated_client.get_setting_values(
            {"devices:local": ["Branding:ProductName1"]}
        )

        assert setting_value == {
            "devices:local": {"Branding:ProductName1": "PLENTICORE plus"}
        }

    @pytest.mark.asyncio
    async def test_smoketest_process_data_value1(
        self, authenticated_client: pykoplenti.ApiClient
    ):
        """Retrieves process data values by using str, str variant."""
        process_data = await authenticated_client.get_process_data_values(
            "devices:local", "EM_State"
        )

        assert process_data.keys() == {"devices:local"}
        assert len(process_data["devices:local"]) == 1
        assert process_data["devices:local"]["EM_State"] is not None

    @pytest.mark.asyncio
    async def test_smoketest_process_data_value2(
        self, authenticated_client: pykoplenti.ApiClient
    ):
        """Retrieves process data values by using str, Iterable[str] variant."""
        process_data = await authenticated_client.get_process_data_values(
            "devices:local", ["EM_State", "Inverter:State"]
        )

        assert process_data.keys() == {"devices:local"}
        assert len(process_data["devices:local"]) == 2
        assert process_data["devices:local"]["EM_State"] is not None
        assert process_data["devices:local"]["Inverter:State"] is not None

    @pytest.mark.asyncio
    async def test_smoketest_process_data_value3(
        self, authenticated_client: pykoplenti.ApiClient
    ):
        """Retrieves process data values by using Dict[str, Iterable[str]] variant."""
        process_data = await authenticated_client.get_process_data_values(
            {
                "devices:local": ["EM_State", "Inverter:State"],
                "scb:export": ["PortalConActive"],
            }
        )

        assert process_data.keys() == {"devices:local", "scb:export"}
        assert len(process_data["devices:local"]) == 2
        assert process_data["devices:local"]["EM_State"] is not None
        assert process_data["devices:local"]["Inverter:State"] is not None
        assert len(process_data["scb:export"]) == 1
        assert process_data["scb:export"]["PortalConActive"] is not None
