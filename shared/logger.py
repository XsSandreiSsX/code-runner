import logging


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.DEBUG,
        format="[%(levelname).1s] | %(asctime)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
