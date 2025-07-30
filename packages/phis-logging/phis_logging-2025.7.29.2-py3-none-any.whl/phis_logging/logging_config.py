import logging
import os
from datetime import datetime
import sys


def 配置日志(level=logging.INFO, old_dir_compat=True):
    """
    设置日志同时输出到控制台和文件
    """
    log_folder = '执行日志'
    if old_dir_compat:
        from phis_logging.dir_switch import setup_dir

        setup_dir()
    os.makedirs(log_folder, exist_ok=True)

    log_filename = os.path.join(
        log_folder, f'{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.log'
    )

    # Get the root logger
    logger = logging.getLogger()
    logger.setLevel(level)

    # Prevent adding duplicate handlers
    if logger.hasHandlers():
        logger.handlers.clear()

    # Create a file handler
    file_handler = logging.FileHandler(log_filename, encoding='utf-8')
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # Create a console handler
    try:
        import coloredlogs

        # Use coloredlogs for prettier console output
        coloredlogs.install(
            level=level,
            logger=logger,
            stream=sys.stdout,
            fmt='%(asctime)s %(name)s [%(filename)s:%(lineno)d] %(levelname)s %(message)s',
        )
    except ImportError:
        # Fallback to standard StreamHandler if coloredlogs is not available
        console_handler = logging.StreamHandler(sys.stdout)
        console_formatter = logging.Formatter('%(levelname)s: %(message)s')
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

    logging.info(
        '日志已配置同时输出到控制台和文件 %s 中', str(log_filename).replace('\\', '/')
    )
