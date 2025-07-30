from __future__ import annotations
import asyncio, sys, time
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch, AsyncMock
import threading

import pytest

# --------------------------------------------------------------------------- #
# package under test                                                          #
# --------------------------------------------------------------------------- #
from petal_app_manager.proxies.external import (
    MavLinkExternalProxy,
    MavLinkFTPProxy,
    _match_ls_to_entries,
    ULogInfo,
)

# --------------------------------------------------------------------------- #
#  Helper message classes for tests                                           #
# --------------------------------------------------------------------------- #

class MsgWithTimeUtc:     
    time_utc = 1612345678          
    def get_type(self): return "AUTOPILOT_VERSION"
    def get_msgId(self): return 0
    
class MsgWithTimeBootMs:  
    time_boot_ms = 60000           
    def get_type(self): return "AUTOPILOT_VERSION"
    def get_msgId(self): return 0
    
class MsgWithTimeUsec:    
    time_usec = 60000000           
    def get_type(self): return "AUTOPILOT_VERSION"
    def get_msgId(self): return 0
    
class MsgWithTimestamp:  
    _timestamp = 1612345678        
    def get_type(self): return "AUTOPILOT_VERSION"
    def get_msgId(self): return 0
    
class MsgWithNoTime:                                      
    def get_type(self): return "AUTOPILOT_VERSION"
    def get_msgId(self): return 0

# --------------------------------------------------------------------------- #
#  Mocks for pymavlink                                                        #
# --------------------------------------------------------------------------- #

class MockMavlink:
    """
    Minimal stand-in for mavutil.mavlink_connection return object.
    """
    def __init__(self, log_entry=False, px4_time_msg=None):
        self.target_system     = 1
        self.target_component  = 1
        self._log_entry_sent   = not log_entry
        self._px4_time_msg     = px4_time_msg
        self.mav               = MagicMock()
        self._log_counter      = 0

    def wait_heartbeat(self, timeout=5):
        return True

    def recv_match(self, blocking=False, type=None, timeout=None):
        if type == "LOG_ENTRY":
            if self._log_counter < 2:
                self._log_counter += 1
                idx     = self._log_counter
                mock_msg = MagicMock()
                mock_msg.id        = idx
                mock_msg.size      = 1024 if idx == 1 else 2048
                mock_msg.time_utc  = 1612345678 + (idx - 1)
                mock_msg.num_logs  = 2
                return mock_msg
        elif type == "AUTOPILOT_VERSION":
            if self._px4_time_msg is not None:
                return self._px4_time_msg
            return None
        return None
    
    def close(self):
        return None


class MockFTPAck:
    def __init__(self, rc=0, op=""): 
        self.return_code = rc
        self.operation_name = op
        
class MockFTPEntry:
    def __init__(self, name, size_b, is_dir=False): 
        self.name = name
        self.size_b = size_b
        self.is_dir = is_dir

class MockFTP:
    """
    Stand-in for pymavlink.mavftp.MAVFTP that feeds predictable directory
    listings and fakes downloads.
    """
    def __init__(self, master, target_system=None, target_component=None, debug=0):
        self.master = master
        self.ftp_settings = SimpleNamespace(
            debug=debug, 
            retry_time=0.2,
            burst_read_size=239
        )
        self.burst_size = 239
        self.list_result = []
        self.temp_filename = "/tmp/temp_mavftp_file"

    def cmd_list(self, args):
        path = args[0]
        if path == "fs/microsd/log":
            self.list_result = [
                MockFTPEntry("2023-01-01", 0, True),
                MockFTPEntry("2023-01-02", 0, True),
            ]
        elif path == "fs/microsd/log/2023-01-01":
            self.list_result = [
                MockFTPEntry("log1.ulg", 1024, False),
                MockFTPEntry("log2.ulg", 2048, False),
            ]
        elif path == "fs/microsd/log/2023-01-02":
            self.list_result = []
        return MockFTPAck()

    def cmd_get(self, args, progress_callback=None):
        if progress_callback:
            for i in range(11):
                progress_callback(i / 10)
        Path(args[1]).write_text("mock data")
        return MockFTPAck()

    def process_ftp_reply(self, op, timeout=0):
        return MockFTPAck()

# --------------------------------------------------------------------------- #
#  Mock for _BlockingParser                                                   #
# --------------------------------------------------------------------------- #

class MockBlockingParser:
    def __init__(self, logger, master, mavlink_proxy, debug=0):
        self._log = logger.getChild("MockBlockingParser")
        self.master = master
        self.proxy = mavlink_proxy
        self.ftp = MockFTP(master, master.target_system, master.target_component)
        
    def list_ulogs(self, entries=None, base = "fs/microsd/log"):
        return [
            {"index": 0, "remote_path": f"{base}/2023-01-01/log1.ulg", "size_bytes": 1024, "utc": 1612345678},
            {"index": 1, "remote_path": f"{base}/2023-01-01/log2.ulg", "size_bytes": 2048, "utc": 1612345679}
        ]
        
    def download_ulog(self, remote_path, local_path, on_progress=None, cancel_event=None):
        # Simulate download with progress
        if on_progress:
            for i in range(11):
                asyncio.run_coroutine_threadsafe(
                    on_progress(i / 10.0),
                    self.proxy._loop
                )
                time.sleep(0.01)
        
        # Create the output file
        local_path.write_text("mock data")
        return str(local_path)
        
    def _ls(self, path):
        if path == "fs/microsd/log":
            return [
                ("2023-01-01", 0, True),
                ("2023-01-02", 0, True),
            ]
        elif path == "fs/microsd/log/2023-01-01":
            return [
                ("log1.ulg", 1024, False),
                ("log2.ulg", 2048, False),
            ]
        return []

# --------------------------------------------------------------------------- #
#  Helper: build & start a proxy under the patches                            #
# --------------------------------------------------------------------------- #

from petal_app_manager.proxies import external as _px

def _patch_pymavlink(px4_time_msg=None):
    """Return context-manager patches for testing."""
    dummy_mavutil = SimpleNamespace(
        mavlink_connection = lambda *a, **kw: MockMavlink(
            log_entry=True, px4_time_msg=px4_time_msg
        ),
        mavlink = SimpleNamespace(
            MAV_CMD_REQUEST_MESSAGE = 0,
            MAVLINK_MSG_ID_LOG_ENTRY = 118
        ),
    )
    dummy_mavftp = SimpleNamespace(MAVFTP = MockFTP)

    # Patches
    p_pkg = patch.multiple(
        "pymavlink",
        mavutil = dummy_mavutil,
        mavftp = dummy_mavftp,
        create = True,
    )
    p_mod1 = patch.object(_px, "mavutil", dummy_mavutil, create=True)
    p_mod2 = patch.object(_px, "mavftp", dummy_mavftp, create=True)
    
    # New patch for _BlockingParser
    p_mod3 = patch.object(_px, "_BlockingParser", MockBlockingParser)
    
    return p_pkg, p_mod1, p_mod2, p_mod3


async def build_proxy(px4_time_msg=None) -> MavLinkExternalProxy:
    p_pkg, p_mod1, p_mod2, p_mod3 = _patch_pymavlink(px4_time_msg)
    with p_pkg, p_mod1, p_mod2, p_mod3:
        proxy = MavLinkExternalProxy(endpoint="udp:dummy:14550", baud=57600, maxlen=200)
        await proxy.start()
        
        # Force connection establishment for testing
        # Since the new logic uses _schedule_reconnect(), we need to wait for it
        # and ensure the connection gets established with our mocks
        await asyncio.sleep(0.1)  # Allow background tasks to run
        
        # Manually set connected status and initialize parser if needed
        if not proxy.connected:
            proxy.connected = True
            
        # Even if connected, the parser might still be None due to timing issues
        # with the async _schedule_reconnect() task, so ensure it's initialized
        if not hasattr(proxy, '_parser') or proxy._parser is None:
            await proxy._init_parser()
        
        return proxy

async def build_ftp_proxy(px4_time_msg=None) -> MavLinkFTPProxy:
    p_pkg, p_mod1, p_mod2, p_mod3 = _patch_pymavlink(px4_time_msg)
    with p_pkg, p_mod1, p_mod2, p_mod3:
        proxy = MavLinkExternalProxy(endpoint="udp:dummy:14550", baud=57600, maxlen=200)

        ftp_proxy = MavLinkFTPProxy(mavlink_proxy=proxy)
        await proxy.start()
        await ftp_proxy.start()
        
        # Force connection establishment for testing
        # Since the new logic uses _schedule_reconnect(), we need to wait for it
        # and ensure the connection gets established with our mocks
        await asyncio.sleep(0.1)  # Allow background tasks to run
        
        # Manually set connected status and initialize parser if needed
        if not proxy.connected:
            proxy.connected = True
            
        # Even if connected, the parser might still be None due to timing issues
        # with the async _schedule_reconnect() task, so ensure it's initialized
        if not hasattr(ftp_proxy, '_parser') or ftp_proxy._parser is None:
            await ftp_proxy._init_parser()
        
        return ftp_proxy

# --------------------------------------------------------------------------- #
#  Pytest fixtures                                                            #
# --------------------------------------------------------------------------- #

@pytest.fixture(scope="session")
def event_loop():
    """Provide a session-wide asyncio loop (pytest-asyncio)."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def hardware_cleanup():
    """Fixture to ensure hardware resources are released if test is interrupted."""
    cancel_events = []
    
    def register_event(event):
        cancel_events.append(event)
        
    yield register_event
    
    # This runs even if test is aborted or fails
    for event in cancel_events:
        if not event.is_set():
            print("Cleaning up hardware resources...")
            event.set()

# --------------------------------------------------------------------------- #
#  Tests – pure helper function                                               #
# --------------------------------------------------------------------------- #

def test_match_ls_to_entries_success():
    ls_list = [
        ("file1.ulg", 1024),
        ("file2.ulg", 2048)
    ]
    entry_dict = {
        1: {'size': 1024, 'utc': 1612345678},
        2: {'size': 2048, 'utc': 1612345679}
    }
    result = _match_ls_to_entries(ls_list, entry_dict, threshold_size=1)
    assert len(result) == 2
    assert result[1][0] == "file1.ulg"
    assert result[2][0] == "file2.ulg"


def test_match_ls_to_entries_count_mismatch():
    with pytest.raises(ValueError):
        _match_ls_to_entries([("file1.ulg", 1024)], {1: {"size": 1024, "utc": 0}, 2: {"size": 2048, "utc": 1}})


def test_match_ls_to_entries_size_tolerance():
    ls_list = [("file1.ulg", 1024), ("file2.ulg", 2050)]
    entry_dict = {
        1: {"size": 1024, "utc": 111},
        2: {"size": 2048, "utc": 222},
    }
    res = _match_ls_to_entries(ls_list, entry_dict, threshold_size=100)
    assert len(res) == 2
    assert res[2][0] == "file2.ulg"

# --------------------------------------------------------------------------- #
#  Tests – proxy init / list / ls / walk                                      #
# --------------------------------------------------------------------------- #

@pytest.mark.asyncio
async def test_init():
    """Ensure proxy starts and has an FTP handle."""
    proxy = await build_ftp_proxy()
    # The parser is now initialized in start()
    assert proxy._parser is not None
    assert proxy._parser.ftp is not None
    await proxy.stop()

@pytest.mark.asyncio
async def test_list_ulogs():
    # Use build_proxy to set up a properly connected proxy
    proxy = await build_ftp_proxy()
    
    # Patch the get_log_entries method to return mock data directly
    async def mock_get_log_entries(**kwargs):
        return {
            1: {"size": 1024, "utc": 1612345678},
            2: {"size": 2048, "utc": 1612345679}
        }
    
    # Apply the patch
    with patch.object(proxy.mavlink_proxy, 'get_log_entries', mock_get_log_entries):
        ulogs = await proxy.list_ulogs()
        
        # Check results
        assert isinstance(ulogs[0], ULogInfo)
        assert len(ulogs) == 2
        paths = {u.remote_path for u in ulogs}
        assert "fs/microsd/log/2023-01-01/log1.ulg" in paths

@pytest.mark.asyncio
async def test_ls():
    """Test directory listing through mock."""
    proxy = await build_ftp_proxy()
    
    # Access through mock BlockingParser's _ls method
    dir_list = proxy._parser._ls("fs/microsd/log")
    assert len(dir_list) == 2
    
    names = {d[0] for d in dir_list}
    assert names == {"2023-01-01", "2023-01-02"}
    
    # Verify directory flags
    assert all(item[2] is True for item in dir_list)
    await proxy.stop()

# --------------------------------------------------------------------------- #
#  Tests – proxy download                                                     #
# --------------------------------------------------------------------------- #

@pytest.mark.asyncio
async def test_download(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    # Ensure worker-thread can find an event-loop
    main_loop = asyncio.get_event_loop()
    monkeypatch.setattr(asyncio, "get_event_loop", lambda: main_loop)

    proxy = await build_ftp_proxy()
    remote = "fs/microsd/log/2023-01-01/log1.ulg"
    local = tmp_path / "log1.ulg"

    progress = []
    async def on_prog(frac):
        progress.append(frac)

    await proxy.download_ulog(remote, local, on_prog)

    assert local.exists() and local.read_text() == "mock data"
    assert progress[-1] == 1.0
    await proxy.stop()

# --------------------------------------------------------------------------- #
#  (Optional) hardware-integration test                                       #
# --------------------------------------------------------------------------- #
@pytest.mark.hardware
@pytest.mark.asyncio
async def test_download_logs_hardware_integration(hardware_cleanup):
    """
    Real-hardware integration test - skipped in CI.
    Connects to actual PX4, lists logs, downloads the smallest one.
    """
    cancel_event = threading.Event()
    hardware_cleanup(cancel_event) # Register cleanup event
    
    proxy = None
    print("=== HARDWARE INTEGRATION TEST START ===")
    
    try:
        print("Creating MavLinkExternalProxy...")
        proxy = MavLinkExternalProxy(endpoint="udp:127.0.0.1:14551", baud=57600, maxlen=200)
        ftp_proxy = MavLinkFTPProxy(mavlink_proxy=proxy)
        print("Starting proxy...")
        await proxy.start()
        await ftp_proxy.start()
        print("Proxy started successfully")
        
        # Wait a bit for connection to stabilize
        print("Waiting for connection to stabilize...")
        await asyncio.sleep(3.0)  # Increased wait time for test suite
        
        # Check if connection is established
        print(f"Connection status after initial wait: {proxy.connected}")
        if not proxy.connected:
            print("Connection not established initially, waiting longer...")
            # Give it more time in case we're in a test suite
            for i in range(5):
                await asyncio.sleep(1.0)
                print(f"Retry {i+1}/5 - Connection status: {proxy.connected}")
                if proxy.connected:
                    print(f"Connection established after retry {i+1}")
                    break
            
            if not proxy.connected:
                print("Connection still not established after retries")
                print("This may be expected if hardware is not available")
                print("Proceeding with test anyway to check if operations work...")
        else:
            print("Connection established successfully!")
            
    except Exception as e:
        print(f"Exception during proxy start: {type(e).__name__}: {e}")
        import traceback
        print("Full traceback:")
        traceback.print_exc()
        if proxy:
            try:
                await proxy.stop()
            except Exception as stop_e:
                print(f"Error during cleanup: {stop_e}")
        pytest.skip(f"Hardware connection not available: {e}")

    try:
        # Check connection before attempting to list logs (but don't skip)
        print(f"Connection status before listing: {proxy.connected}")
        if not proxy.connected:
            print("Connection not established, but attempting to list logs anyway...")
            print("This will test if the error handling works correctly...")
            
        print("Listing ULogs on vehicle...")
        try:
            ulogs = await ftp_proxy.list_ulogs("/fs/microsd/log")
            print(f"Found {len(ulogs)} ULog files")
        except Exception as e:
            print(f"Error listing ULogs: {type(e).__name__}: {e}")
            print("This is expected if hardware is not connected")
            raise
        
        if not ulogs or len(ulogs) == 0:
            print("No ULogs found - this may be normal if SD card is empty")
            pytest.skip("No ULogs found on vehicle")

        # find the smallest file to download
        smallest = min(ulogs, key=lambda u: u.size_bytes)
        remote = smallest.remote_path
        print(f"Downloading {remote} ({smallest.size_bytes} bytes)...")

        local = Path("ulog_downloads") / Path(remote).name
        local.parent.mkdir(exist_ok=True)

        async def on_progress(frac):
            if int(frac * 100) % 20 == 0:  # Print every 20% to reduce noise
                print(f"Download progress: {frac * 100:.1f}%")

        # Check connection before download (but don't skip)
        print(f"Connection status before download: {proxy.connected}")
        if not proxy.connected:
            print("Connection not established, but attempting download anyway...")
            
        print("Starting download...")
        try:
            await ftp_proxy.download_ulog(remote, local, on_progress=on_progress, cancel_event=cancel_event)
            print("Download completed!")
        except Exception as e:
            print(f"Error during download: {type(e).__name__}: {e}")
            print("This is expected if hardware is not connected")
            raise

        if not local.exists():
            pytest.fail(f"Download failed: {remote} -> {local}")
        
        file_size = local.stat().st_size
        print(f"Downloaded file size: {file_size} bytes")
        assert local.exists() and file_size > 0
        print("=== TEST PASSED! ===")
        
    except RuntimeError as e:
        print(f"RuntimeError during test: {e}")
        # Only skip for very specific connection errors
        if "MAVLink connection not established" in str(e):
            print("Skipping due to connection issue (expected when hardware not available)")
            pytest.skip(f"Connection issue during test: {e}")
        else:
            print("Re-raising RuntimeError...")
            raise
    except OSError as e:
        print(f"OSError during test: {e} (errno: {e.errno})")
        if e.errno == 9:  # Bad file descriptor
            print("Skipping due to bad file descriptor (connection lost)")
            pytest.skip(f"Connection lost during operation: {e}")
        else:
            print("Re-raising OSError...")
            raise
    except Exception as e:
        print(f"Unexpected exception during test: {type(e).__name__}: {e}")
        import traceback
        print("Full traceback:")
        traceback.print_exc()
        raise
    finally:
        print("Running cleanup...")
        # Local cleanup - happens even if test fails
        if not cancel_event.is_set():
            cancel_event.set()
        if proxy:
            try:
                await proxy.stop()
                print("Proxy stopped successfully")
            except Exception as e:
                print(f"Error stopping proxy: {e}")
        if ftp_proxy:
            try:
                await ftp_proxy.stop()
                print("FTP Proxy stopped successfully")
            except Exception as e:
                print(f"Error stopping FTP proxy: {e}")
        print("Cleanup completed.")
        
        # Add a small delay to ensure resources are fully released
        await asyncio.sleep(0.5)
        print("=== HARDWARE INTEGRATION TEST END ===")
