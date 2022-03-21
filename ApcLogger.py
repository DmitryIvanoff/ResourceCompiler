import locale
import logging
import os
import sys
import time
from pathlib import Path

start_date = time.strftime("%Y_%m_%d")
start_time = time.strftime("%H_%M_%S")
# main file handler
if not Path("./Logs").exists():
    os.makedirs(str(Path("./Logs")))
main_fh = logging.FileHandler(f"./Logs/{start_date}_main_{start_time}.log", mode="w", encoding="utf8")
main_fh.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(levelname)s: [%(name)-10s] *%(threadName)s* %(message)s', datefmt="%Y-%m-%d %H:%M:%S")
main_fh.setFormatter(formatter)


def get_encoding():
    return locale.getpreferredencoding()


def getLogger(name, filename: str = None, loglevel: str = "INFO", afDT: bool = True, **params) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(loglevel)
    formatter = logging.Formatter('%(asctime)s: [%(levelname)s] %(message)s')
    should_add_file_handler = not any((isinstance(h, logging.FileHandler)
                                       and filename == h.baseFilename
                                       for h in logger.handlers))
    should_add_stdout_handler = not any((isinstance(h, logging.StreamHandler)
                                         and h.stream == sys.stdout
                                         for h in logger.handlers))
    should_add_stderr_handler = not any((isinstance(h, logging.StreamHandler)
                                         and h.stream == sys.stdout
                                         for h in logger.handlers))
    if filename and should_add_file_handler:
        file = Path(filename)
        if afDT:
            datestr = time.strftime("%Y_%m_%d")  # time.strftime("%Y_%m_%d_%H_%M_%S")
            timestr = time.strftime("%H_%M_%S")
            if file.suffix:
                file = file.parent.joinpath(f"{datestr}_{file.name.split('.')[0]}_{timestr}.{file.name.split('.')[1]}")
            else:
                file = file.parent.joinpath(f"{datestr}_{file.name}_{timestr}.log")
        if not file.parent.exists():
            os.makedirs(file.parent)
        fh = logging.FileHandler(file, mode="w", encoding="utf-8")
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)
        logger.addHandler(fh)
    if should_add_stdout_handler:
        # добавляем консольный обработчик (всегда добаляется stdout)
        ch1 = logging.StreamHandler(params.get("stream", sys.stdout))
        ch1.setLevel(logging.DEBUG)
        ch1.setFormatter(formatter)
        ch1.addFilter(
            lambda x: 1 if x.levelname != "ERROR" and x.levelname != "CRITICAL" else 0)  # все кроме ERROR в stdout
        logger.addHandler(ch1)
    if should_add_stderr_handler:
        ch2 = logging.StreamHandler(sys.stderr)
        ch2.setLevel(logging.ERROR)
        ch2.addFilter(lambda x: 1 if x.levelname == "ERROR" or x.levelname == "CRITICAL" else 0)  # все ERROR в stderr
        ch2.setFormatter(formatter)
        logger.addHandler(ch2)
    if params.get("to_main_log", True):
        logger.addHandler(main_fh)
    return logger


class ApcLogger:
    def __init__(self, name, filename: str = None, loglevel="INFO", afDT: bool = True, **params):
        self._logger = logging.getLogger(name)
        self.removeHandlers()
        self._logger.setLevel(loglevel)
        self._formatter = logging.Formatter('%(asctime)s: [%(levelname)s] %(message)s')
        self.addStreamHandler(stream=sys.stdout, loglevel=loglevel)
        self.addStreamHandler(
            stream=sys.stderr,
            loglevel="ERROR",
            filt_func=lambda x: 1 if x.levelname == "ERROR" or x.levelname == "CRITICAL" else 0)  # все ERROR в stderr
        self.addFileHandler(filename, loglevel=loglevel, afDT=afDT, **params)

    def removeHandlers(self):
        if self._logger.hasHandlers():
            for h in self._logger.handlers:
                self._logger.removeHandler(h)

    def addFileHandler(self,
                       filename: str = None,
                       loglevel="DEBUG",
                       afDT: bool = True,
                       formatter: logging.Formatter = None,
                       encoding="utf-8",
                       mode="w",
                       **params):
        should_add_file_handler = not any((isinstance(h, logging.FileHandler)
                                           and filename == h.baseFilename
                                           for h in self._logger.handlers))
        if filename and should_add_file_handler:
            file = Path(filename)
            if afDT:
                datestr = time.strftime("%Y_%m_%d")  # time.strftime("%Y_%m_%d_%H_%M_%S")
                timestr = time.strftime("%H_%M_%S")
                if file.suffix:
                    file = file.parent.joinpath(f"{datestr}_{file.name.split('.')[0]}_{timestr}.{file.name.split('.')[1]}")
                else:
                    file = file.parent.joinpath(f"{datestr}_{file.name}_{timestr}.log")
            if not file.parent.exists():
                os.makedirs(file.parent)
            fh = logging.FileHandler(file, mode=mode, encoding=encoding)
            fh.setLevel(loglevel)
            if formatter:
                fh.setFormatter(formatter)
            else:
                fh.setFormatter(self._formatter)
            self._logger.addHandler(fh)

    def addStreamHandler(self,
                         stream=sys.stdout,
                         loglevel="INFO",
                         filt_func=None,
                         formatter: logging.Formatter = None,
                         **params):
        should_add_stream_handler = not any((isinstance(h, logging.StreamHandler)
                                             and h.stream == stream
                                             for h in self._logger.handlers))
        if should_add_stream_handler:
            # добавляем консольный обработчик (всегда добавляется stdout)
            ch1 = logging.StreamHandler(stream)
            ch1.setLevel(loglevel)
            if formatter:
                ch1.setFormatter(formatter)
            else:
                ch1.setFormatter(self._formatter)

            if filt_func:
                ch1.addFilter(filt_func)
            else:
                ch1.addFilter(
                    lambda x: 1 if x.levelname != "ERROR" and x.levelname != "CRITICAL" else 0)  # все кроме ERROR в stdout
            self._logger.addHandler(ch1)

    def setFormatter(self, formatter: logging.Formatter):
        for h in self._logger.handlers:
            h.setFormatter(formatter)

    def debug(self, msg, *args, **kwargs):
        self._logger.debug(msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        self._logger.info(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        self._logger.warning(msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        self._logger.critical(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        self._logger.error(msg, *args, **kwargs)

    def exception(self, msg, *args, **kwargs):
        self._logger.exception(msg, *args, **kwargs)

    def getLogger(self):
        return self._logger


if __name__ == "__main__":
    logger = getLogger("__main__")
    logger.info("sdfg")
