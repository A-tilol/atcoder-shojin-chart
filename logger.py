import logging
import sys

FORMAT = (
    "%(levelname)-8s %(asctime)s [%(filename)s %(funcName)s:%(lineno)s] %(message)s"
)


def get_logger(module_name: str, level=20, out_file: str = "") -> logging.Logger:
    """モジュールごとに設定可能なロガーを返す

    使用してるライブラリのログに興味がないため、ルートロガーの設定は行っていない

    level:
        10: DEBUG
        20: INFO
        30: WARNING
        40: ERROR
        50: CRITICAL

    Args:
        module_name (str): モジュール名
        level (int, optional): ログレベル. Defaults to 10.
        out_file (str, optional): ログ出力ファイル. Defaults to "".

    Returns:
        logging.Logger: ロガー
    """

    logger = logging.getLogger(module_name)
    logger.setLevel(level)
    logger.propagate = False

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(logging.Formatter(FORMAT))
    logger.addHandler(handler)

    if out_file:
        fl_handler = logging.FileHandler(filename=out_file, encoding="utf-8")
        fl_handler.setLevel(logging.DEBUG)
        fl_handler.setFormatter(logging.Formatter(FORMAT))
        logger.addHandler(fl_handler)

    return logger
