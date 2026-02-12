# Copyright (c) 2026, Ive Herreman
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

"""The CREG-tarief thuis laden integration."""

from __future__ import annotations

from datetime import timedelta, datetime
import logging
import csv

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from .const import DOMAIN, CONF_URL

PLATFORMS: list[Platform] = [Platform.SENSOR]

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up CREG-tarief thuis laden from a config entry."""
    coordinator = CregDataUpdateCoordinator(hass)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


class CregDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching CREG data."""

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize."""
        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=timedelta(hours=24))

    async def _async_update_data(self) -> dict[str, float]:
        """Fetch data from CREG CSV."""
        session = async_get_clientsession(self.hass)
        try:
            async with session.get(CONF_URL) as response:
                response.raise_for_status()
                text = await response.text()
        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err

        return self._parse_csv(text)

    def _parse_csv(self, text: str) -> dict:
        """Parse the CSV data and return the current applicable prices."""
        # Use semi-colon delimiter
        lines = text.splitlines()
        reader = csv.reader(lines, delimiter=";")

        # Skip header
        rows = list(reader)
        if len(rows) < 2:
            raise UpdateFailed("CSV has no data rows")

        rows = rows[1:]

        # Determine target year/month based on current date
        now = dt_util.now()
        current_month = now.month
        current_year = now.year

        # Logic:
        # Q1 (Jan-Mar) -> Look for Prev Year, Month 10
        # Q2 (Apr-Jun) -> Look for Curr Year, Month 1
        # Q3 (Jul-Sep) -> Look for Curr Year, Month 4
        # Q4 (Oct-Dec) -> Look for Curr Year, Month 7

        if 1 <= current_month <= 3:
            target_year = current_year - 1
            target_month = 10
        elif 4 <= current_month <= 6:
            target_year = current_year
            target_month = 1
        elif 7 <= current_month <= 9:
            target_year = current_year
            target_month = 4
        else: # 10-12
            target_year = current_year
            target_month = 7

        _LOGGER.debug(
            "Looking for Year=%s, Month=%s (Current Date=%s)",
            target_year,
            target_month,
            now,
        )

        # Indices (0-based) based on User Input:
        # Year: 0
        # Month: 1
        # Flanders: 3
        # Brussels: 5
        # Wallonia: 7

        for row in rows:
            if len(row) < 8:
                continue

            try:
                row_year = int(row[0])
                row_month = int(row[1])
            except ValueError:
                continue # Skip invalid rows

            if row_year == target_year and row_month == target_month:
                # Found it!
                try:
                    return {
                        "flanders": self._parse_float(row[3]),
                        "brussels": self._parse_float(row[5]),
                        "wallonia": self._parse_float(row[7]),
                        "source_year": row_year,
                        "source_month": row_month,
                    }
                except ValueError as err:
                    raise UpdateFailed(f"Error parsing values in row {row}: {err}") from err

        raise UpdateFailed(f"No matching data found for target Year={target_year}, Month={target_month}")

    def _parse_float(self, value: str) -> float:
        """Parse float from string with comma decimal."""
        if not value:
            return 0.0
        return float(value.replace(",", "."))
