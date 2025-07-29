import sys

import asyncio
from bleak import BleakScanner
from gshock_api.watch_info import watch_info
from gshock_api.logger import logger
from bleak.backends.device import BLEDevice

import asyncio
import sys
from bleak import BleakScanner, BLEDevice, AdvertisementData
from typing import Optional

from bleak import BleakScanner, BLEDevice, AdvertisementData
import asyncio
from typing import Optional

class Scanner:
    def __init__(self):
        self._found_device: Optional[BLEDevice] = None
        self._event = asyncio.Event()

    def _make_callback(self, excluded_watches: list[str], device_address: Optional[str]):
        def callback(device: BLEDevice, adv: AdvertisementData):
            name = device.name or adv.local_name or ""
            parts = name.split(" ", 1)
            has_casio_in_name = parts[0].lower() == 'casio'
            is_excluded = not (len(parts) > 1 and parts[1] not in excluded_watches)
            if device_address and device.address.lower() != device_address.lower():
                return
            if not has_casio_in_name:
                return
            if is_excluded:
                logger.info(f"Excluded: {name}")
                return

            logger.info(f"✅ Found: {name} ({device.address})")
            self._found_device = device
            self._event.set()
        return callback

    async def scan(self, device_address: Optional[str] = None, excluded_watches: Optional[list[str]] = None) -> Optional[BLEDevice]:
        if excluded_watches is None:
            excluded_watches = []

        callback = self._make_callback(excluded_watches, device_address)
        scanner = BleakScanner(detection_callback=callback)

        logger.info("🔍 Scanning for CASIO device...")
        await scanner.start()

        try:
            await self._event.wait()
        finally:
            await scanner.stop()
            self._event.clear()

        return self._found_device

scanner = Scanner()
