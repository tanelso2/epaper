import pytest

from epaper.display.wrapper import AsyncEPDWrapper, get_display_wrapper


@pytest.fixture
def real_display_wrapper() -> AsyncEPDWrapper:
    try:
        e = get_display_wrapper(use_mock=False)
        return e
    except Exception:
        pytest.skip("Could not load real display")


@pytest.fixture
def mock_display_wrapper() -> AsyncEPDWrapper:
    return get_display_wrapper(use_mock=True)


@pytest.fixture(params=[True, False])
def parameterized_display_wrapper(request) -> AsyncEPDWrapper:
    use_mock = request.param
    try:
        e = get_display_wrapper(use_mock=use_mock)
        return e
    except Exception:
        if use_mock:
            # Should never fail, propagate failure
            raise
        else:
            pytest.skip("Could not load real display")


async def test_display_wrapper(parameterized_display_wrapper: AsyncEPDWrapper):
    e = parameterized_display_wrapper
    await e.init()
    await e.blank_screen()
    await e.sleep()
    await e.clear()
    await e.blank_screen()
