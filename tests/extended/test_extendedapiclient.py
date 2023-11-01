from typing import Any, Callable
import pytest

import pykoplenti
import pykoplenti.extended

from unittest.mock import ANY, MagicMock, call


class TestVirtualProcessDataValuesDcSum:
    """This class contains tests for virtual process data values for DC sum."""

    @pytest.mark.asyncio
    async def test_virtual_process_data(
        self,
        pykoplenti_extended_client: pykoplenti.extended.ExtendedApiClient,
        client_response_factory: Callable[[int, list[Any] | dict[Any, Any]], MagicMock],
        websession: MagicMock,
    ):
        """Test virtual process data for PV power if depencies are present."""
        client_response_factory(
            200,
            [
                {"moduleid": "devices:local:pv1", "processdataids": ["P"]},
                {"moduleid": "devices:local:pv2", "processdataids": ["P"]},
            ],
        )

        values = await pykoplenti_extended_client.get_process_data()

        websession.request.assert_called_once_with(
            "GET",
            ANY,
            headers=ANY,
        )

        assert values == {
            "_virt_": ["pv_P"],
            "devices:local:pv1": ["P"],
            "devices:local:pv2": ["P"],
        }

    @pytest.mark.asyncio
    async def test_virtual_process_data_value(
        self,
        pykoplenti_extended_client: pykoplenti.extended.ExtendedApiClient,
        client_response_factory: Callable[[int, list[Any] | dict[Any, Any]], MagicMock],
        websession: MagicMock,
    ):
        """Test virtual process data for PV power."""
        client_response_factory(
            200,
            [
                {"moduleid": "devices:local:pv1", "processdataids": ["P"]},
                {"moduleid": "devices:local:pv2", "processdataids": ["P"]},
                {"moduleid": "devices:local:pv3", "processdataids": ["P"]},
            ],
        )
        client_response_factory(
            200,
            [
                {
                    "moduleid": "devices:local:pv1",
                    "processdata": [
                        {"id": "P", "unit": "W", "value": 700.0},
                    ],
                },
                {
                    "moduleid": "devices:local:pv2",
                    "processdata": [
                        {"id": "P", "unit": "W", "value": 300.0},
                    ],
                },
                {
                    "moduleid": "devices:local:pv3",
                    "processdata": [
                        {"id": "P", "unit": "W", "value": 500.0},
                    ],
                },
            ],
        )

        values = await pykoplenti_extended_client.get_process_data_values(
            "_virt_", "pv_P"
        )

        websession.request.assert_has_calls(
            [
                call("GET", ANY, headers=ANY),
                call(
                    "POST",
                    ANY,
                    headers=ANY,
                    json=[
                        {"moduleid": "devices:local:pv1", "processdataids": ["P"]},
                        {"moduleid": "devices:local:pv2", "processdataids": ["P"]},
                        {"moduleid": "devices:local:pv3", "processdataids": ["P"]},
                    ],
                ),
            ],
            any_order=True,
        )

        assert values == {
            "_virt_": pykoplenti.ProcessDataCollection(
                [pykoplenti.ProcessData(id="pv_P", unit="W", value=1500.0)]
            )
        }


class TestVirtualProcessDataValuesEnergyToGrid:
    """This class contains tests for virtual process data values for energy to grid."""

    @pytest.mark.parametrize("scope", ["Total", "Year", "Month", "Day"])
    @pytest.mark.asyncio
    async def test_virtual_process_data(
        self,
        pykoplenti_extended_client: pykoplenti.extended.ExtendedApiClient,
        client_response_factory: Callable[[int, list[Any] | dict[Any, Any]], MagicMock],
        websession: MagicMock,
        scope: str,
    ):
        """Test virtual process data."""
        client_response_factory(
            200,
            [
                {
                    "moduleid": "scb:statistic:EnergyFlow",
                    "processdataids": [
                        f"Statistic:Yield:{scope}",
                        f"Statistic:EnergyHomeBat:{scope}",
                        f"Statistic:EnergyHomePv:{scope}",
                    ],
                },
            ],
        )

        values = await pykoplenti_extended_client.get_process_data()

        websession.request.assert_called_once_with(
            "GET",
            ANY,
            headers=ANY,
        )

        assert values == {
            "_virt_": [f"Statistic:EnergyGrid:{scope}"],
            "scb:statistic:EnergyFlow": [
                f"Statistic:Yield:{scope}",
                f"Statistic:EnergyHomeBat:{scope}",
                f"Statistic:EnergyHomePv:{scope}",
            ],
        }

    @pytest.mark.parametrize("scope", ["Total", "Year", "Month", "Day"])
    @pytest.mark.asyncio
    async def test_virtual_process_data_value(
        self,
        pykoplenti_extended_client: pykoplenti.extended.ExtendedApiClient,
        client_response_factory: Callable[[int, list[Any] | dict[Any, Any]], MagicMock],
        websession: MagicMock,
        scope: str,
    ):
        """Test virtuel process data for energy to grid."""
        client_response_factory(
            200,
            [
                {
                    "moduleid": "scb:statistic:EnergyFlow",
                    "processdataids": [
                        f"Statistic:Yield:{scope}",
                        f"Statistic:EnergyHomeBat:{scope}",
                        f"Statistic:EnergyHomePv:{scope}",
                    ],
                },
            ],
        )
        client_response_factory(
            200,
            [
                {
                    "moduleid": "scb:statistic:EnergyFlow",
                    "processdata": [
                        {
                            "id": f"Statistic:Yield:{scope}",
                            "unit": "Wh",
                            "value": 1000.0,
                        },
                        {
                            "id": f"Statistic:EnergyHomeBat:{scope}",
                            "unit": "Wh",
                            "value": 100.0,
                        },
                        {
                            "id": f"Statistic:EnergyHomePv:{scope}",
                            "unit": "Wh",
                            "value": 200.0,
                        },
                    ],
                },
            ],
        )

        values = await pykoplenti_extended_client.get_process_data_values(
            "_virt_", f"Statistic:EnergyGrid:{scope}"
        )

        websession.request.assert_has_calls(
            [
                call("GET", ANY, headers=ANY),
                call(
                    "POST",
                    ANY,
                    headers=ANY,
                    json=[
                        {
                            "moduleid": "scb:statistic:EnergyFlow",
                            "processdataids": [
                                f"Statistic:Yield:{scope}",
                                f"Statistic:EnergyHomeBat:{scope}",
                                f"Statistic:EnergyHomePv:{scope}",
                            ],
                        },
                    ],
                ),
            ],
            any_order=True,
        )

        assert values == {
            "_virt_": pykoplenti.ProcessDataCollection(
                [
                    pykoplenti.ProcessData(
                        id=f"Statistic:EnergyGrid:{scope}", unit="Wh", value=700.0
                    )
                ]
            )
        }


@pytest.mark.asyncio
async def test_virtual_process_data_no_dc_sum(
    pykoplenti_extended_client: pykoplenti.extended.ExtendedApiClient,
    client_response_factory: Callable[[int, list[Any] | dict[Any, Any]], MagicMock],
    websession: MagicMock,
):
    """Test if no virtual process data is present if dependecies are missing."""
    client_response_factory(
        200,
        [
            {"moduleid": "devices:local", "processdataids": ["EM_State"]},
        ],
    )

    values = await pykoplenti_extended_client.get_process_data()

    websession.request.assert_called_once_with(
        "GET",
        ANY,
        headers=ANY,
    )

    assert values == {
        "_virt_": [],
        "devices:local": ["EM_State"],
    }


@pytest.mark.asyncio
async def test_virtual_process_data_and_normal_process_data(
    pykoplenti_extended_client: pykoplenti.extended.ExtendedApiClient,
    client_response_factory: Callable[[int, list[Any] | dict[Any, Any]], MagicMock],
    websession: MagicMock,
):
    """Test if virtual and non-virtual process values can be requested."""
    client_response_factory(
        200,
        [
            {"moduleid": "devices:local:pv1", "processdataids": ["P"]},
            {"moduleid": "devices:local:pv2", "processdataids": ["P"]},
        ],
    )
    client_response_factory(
        200,
        [
            {
                "moduleid": "devices:local:pv1",
                "processdata": [
                    {"id": "P", "unit": "W", "value": 700.0},
                ],
            },
            {
                "moduleid": "devices:local:pv2",
                "processdata": [
                    {"id": "P", "unit": "W", "value": 300.0},
                ],
            },
        ],
    )

    values = await pykoplenti_extended_client.get_process_data_values(
        {"_virt_": ["pv_P"], "devices:local:pv1": ["P"], "devices:local:pv2": ["P"]}
    )

    websession.request.assert_has_calls(
        [
            call("GET", ANY, headers=ANY),
            call(
                "POST",
                ANY,
                headers=ANY,
                json=[
                    {"moduleid": "devices:local:pv1", "processdataids": ["P"]},
                    {"moduleid": "devices:local:pv2", "processdataids": ["P"]},
                ],
            ),
        ],
        any_order=True,
    )

    assert values == {
        "_virt_": pykoplenti.ProcessDataCollection(
            [pykoplenti.ProcessData(id="pv_P", unit="W", value=1000.0)]
        ),
        "devices:local:pv1": pykoplenti.ProcessDataCollection(
            [pykoplenti.ProcessData(id="P", unit="W", value=700.0)]
        ),
        "devices:local:pv2": pykoplenti.ProcessDataCollection(
            [pykoplenti.ProcessData(id="P", unit="W", value=300.0)]
        ),
    }
