import asyncio
from typing import Optional
from ..opsencoder.gcode import GcodeEncoder
from ..models.ops import Ops
from ..models.machine import Machine
from ..transport import TelnetTransport, TransportStatus
from .driver import Driver, DeviceStatus
from .grbl import _parse_state


class SmoothieDriver(Driver):
    """
    Handles Smoothie-based devices via Telnet
    """

    label = "Smoothie"
    subtitle = "Smoothieware via a Telnet connection"

    def __init__(self):
        super().__init__()
        self.encoder = GcodeEncoder()
        self.telnet = None
        self.keep_running = False
        self._connection_task: Optional[asyncio.Task] = None
        self._ok_event = asyncio.Event()

    def setup(self, host: str = "", port: int = 23):
        assert not self.did_setup
        if not host:
            return  # Leave unconfigured
        super().setup()

        # Initialize transports
        self.telnet = TelnetTransport(host, port)
        self.telnet.received.connect(self.on_telnet_data_received)
        self.telnet.status_changed.connect(self.on_telnet_status_changed)

    async def cleanup(self):
        self.keep_running = False
        if self._connection_task:
            self._connection_task.cancel()
        if self.telnet:
            await self.telnet.disconnect()
            self.telnet.received.disconnect(self.on_telnet_data_received)
            self.telnet.status_changed.disconnect(
                self.on_telnet_status_changed
            )
            self.telnet = None
        await super().cleanup()

    async def connect(self):
        self.keep_running = True
        self._connection_task = asyncio.create_task(self._connection_loop())

    async def _connection_loop(self) -> None:
        while self.keep_running:
            if not self.telnet:
                self._on_connection_status_changed(
                    TransportStatus.ERROR, "Driver not configured"
                )
                await asyncio.sleep(5)
                continue

            self._on_connection_status_changed(TransportStatus.CONNECTING)
            try:
                await self.telnet.connect()
                # The transport handles the connection loop.
                # We just need to wait here until cleanup.
                while self.keep_running:
                    await self.telnet.send(b"?")
                    await asyncio.sleep(1)

            except asyncio.CancelledError:
                break  # cleanup is called
            except Exception as e:
                self._on_connection_status_changed(
                    TransportStatus.ERROR, str(e)
                )
            finally:
                if self.telnet:
                    await self.telnet.disconnect()

            if not self.keep_running:
                break

            self._on_connection_status_changed(TransportStatus.SLEEPING)
            await asyncio.sleep(5)

    async def _send_and_wait(self, cmd: bytes):
        if not self.telnet:
            return
        self._ok_event.clear()
        await self.telnet.send(cmd)
        try:
            # Set a 10s timeout to avoid deadlocks
            await asyncio.wait_for(self._ok_event.wait(), 10.0)
        except asyncio.TimeoutError as e:
            raise ConnectionError(
                f"Command '{cmd.decode()}' not confirmed"
            ) from e

    async def run(self, ops: Ops, machine: Machine) -> None:
        gcode = self.encoder.encode(ops, machine)
        try:
            for line in gcode.splitlines():
                await self._send_and_wait(line.encode())
        except Exception as e:
            self._on_connection_status_changed(TransportStatus.ERROR, str(e))
            raise

    async def set_hold(self, hold: bool = True) -> None:
        if hold:
            await self._send_and_wait(b"!")
        else:
            await self._send_and_wait(b"~")

    async def cancel(self) -> None:
        # Send Ctrl+C
        await self._send_and_wait(b"\x03")

    async def home(self) -> None:
        await self._send_and_wait(b"$H")

    async def move_to(self, pos_x, pos_y) -> None:
        cmd = f"G90 G0 X{float(pos_x)} Y{float(pos_y)}"
        await self._send_and_wait(cmd.encode())

    def on_telnet_data_received(self, sender, data: bytes):
        data_str = data.decode("utf-8")
        for line in data_str.splitlines():
            self._log(line)
            if "ok" in line:
                self._ok_event.set()
                self._on_command_status_changed(TransportStatus.IDLE)

            if not line.startswith("<") or not line.endswith(">"):
                continue
            state = _parse_state(line[1:-1], self.state, self._log)
            if state != self.state:
                self.state = state
                self._on_state_changed()

    def on_telnet_status_changed(
        self, sender, status: TransportStatus, message: Optional[str] = None
    ):
        self._on_connection_status_changed(status, message)
        if status in [TransportStatus.DISCONNECTED, TransportStatus.ERROR]:
            if self.state.status != DeviceStatus.UNKNOWN:
                self.state.status = DeviceStatus.UNKNOWN
                self._on_state_changed()
