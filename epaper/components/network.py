from epaper.components.core import (
    TextComponent,
)
from epaper.components.fonts import font
from epaper.data.network import get_ip_address, get_ssid


class NetworkComponent(TextComponent):
    def __init__(self, pos, font_size=22):
        self.font = font(size=font_size)
        ssid = get_ssid() or "<ssid>"
        ip_address = get_ip_address() or "<ip>"
        text = f"{ssid} | {ip_address}"
        super().__init__(text, self.font, pos)
