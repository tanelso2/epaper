import pytest

from epaper.display.wrapper import get_display_wrapper


@pytest.mark.asyncio
async def test_mock_display_wrapper():
    e = get_display_wrapper(use_mock=True)
    await e.init()
    await e.blank_screen()
    await e.clear()
