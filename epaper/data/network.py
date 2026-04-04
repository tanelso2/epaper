import fcntl
import socket
import struct
import subprocess
from typing import Optional


def get_ip_address(interface="wlan0") -> Optional[str]:
    """Get the IP address of a network interface."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # SIOCGIFADDR is a request to get the interface address
        ip_address = socket.inet_ntoa(
            fcntl.ioctl(
                sock.fileno(),
                0x8915,  # SIOCGIFADDR
                struct.pack("256s", interface.encode("utf-8")[:15]),
            )[20:24]
        )
        return ip_address
    except IOError as e:
        return None


def get_ssid() -> Optional[str]:
    """Get the current WiFi SSID."""
    try:
        return subprocess.check_output(["iwgetid", "-r"], text=True).strip()
    except subprocess.CalledProcessError:
        return None
