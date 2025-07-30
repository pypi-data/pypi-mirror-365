import logging
import colorlog
from colorlog import default_log_colors, ColoredFormatter


class PackagePathFormatter(ColoredFormatter):
    def format(self, record):
        if hasattr(record, 'module'):
            package_path = record.module.replace('.', '/')
        else:
            package_path = ""

        record.package_filepath = f"{package_path}.py" if package_path else record.filename

        return super().format(record)


def setup_logging(level=logging.INFO):
    # 创建一个日志记录器
    logging.basicConfig(style='%')
    logger = logging.getLogger()
    logger.setLevel(level)
    logger.handlers = []

    # 创建一个控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)  # 设置处理器的日志级别
    console_handler.setFormatter(PackagePathFormatter(
        '%(log_color)s %(asctime)s - %(name)s:%(lineno)d - %(levelname)s - %(message)s',
        log_colors=default_log_colors
    ))
    logger.addHandler(console_handler)
