import logging

LOG_LEVEL_OVERRIDES = {
    "urllib3": logging.INFO,
    "waveshare_epd": logging.INFO,
}

LOG_FORMAT: str = (
    "%(asctime)s|%(levelname)s|%(name)s::%(funcName)s:%(lineno)d|%(message)s"
)

DATE_FORMAT: str | None = None


def setup_logging(debug=False):
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(level=level, format=LOG_FORMAT, datefmt=DATE_FORMAT)
    for module_name, override_level in LOG_LEVEL_OVERRIDES.items():
        module_logger = logging.getLogger(module_name)
        module_logger.setLevel(override_level)
