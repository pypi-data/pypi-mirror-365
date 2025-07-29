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

    async def scan_with_find(self, device_address=None, excluded_watches: list[str] | None = None) -> BLEDevice | None:
            scanner = BleakScanner()

            if excluded_watches is None:
                excluded_watches = []

            if device_address is None:
                while True:
                    device = await scanner.find_device_by_filter(
                        lambda d, ad: (
                            d.name
                            and (parts := d.name.split(" ", 1))
                            and parts[0].lower() == "casio"
                            and (len(parts) > 1 and parts[1] not in excluded_watches)
                        ),
                        timeout=5 * 60.0,
                    )
                    if device is None:
                        continue

                    watch_info.set_name_and_model(device.name)
                    break
            else:
                logger.info("Waiting for device by address...")
                device = await scanner.find_device_by_address(
                    device_address, sys.float_info.max
                )
                if device is None:
                    return None

                if any(device.name.lower().startswith(p.lower()) for p in excluded_watches):
                    logger.info(f"Excluded device found: {device.name}")
                    return None

                watch_info.set_name_and_model(device.name)

            return device

    async def scan(self, device_address: Optional[str] = None, excluded_watches: Optional[list[str]] = None) -> Optional[BLEDevice]:
        if excluded_watches is None:
            excluded_watches = []

        logger.info("🔍 Scanning for CASIO device...")

        try:
            while True:
                try:
                    devices = await BleakScanner.discover(timeout=5.0)
                except Exception as e:
                    logger.warning(f"⚠️ Scan error: {e}")
                    await asyncio.sleep(1)
                    continue

                if not devices:
                    logger.debug("No BLE devices found.")
                    await asyncio.sleep(1)
                    continue

                for device in devices:
                    name = device.name or ""
                    parts = name.split(" ", 1)
                    is_casio = parts[0].lower() == "casio"
                    is_excluded = len(parts) > 1 and parts[1] in excluded_watches
                    if is_excluded:
                        logger.info(f"{name} excluded!")

                    if is_casio and not is_excluded:
                        logger.info(f"✅ Found: {name} ({device.address})")
                        watch_info.set_name_and_model(device.name)
                        return device

                await asyncio.sleep(1)  # ✅ Wait before next loop

        except asyncio.CancelledError:
            logger.info("🔁 Scan loop cancelled.")
            raise

        except Exception as e:
            logger.exception(f"❌ Unexpected scan error: {e}")
            return None
    
scanner = Scanner()
