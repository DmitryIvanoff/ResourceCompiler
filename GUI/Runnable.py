from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import traceback
import sys
from ApcLogger import getLogger
from ApcWorkObj import ApcCompiler


class WorkerSignals(QObject):
    """Defines the signals available from a running worker thread.

    Supported signals are:

    finished
        No data

    error
        `tuple` (exctype, value, traceback.format_exc() )

    result
        `object` data returned from processing, anything

    progress
        `int` indicating % progress
    """
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)
    progress = pyqtSignal(int)

    def disconnect_all(self):
        self.finished.disconnect()
        self.error.disconnect()
        self.result.disconnect()
        self.progress.disconnect()


class Worker(QRunnable):
    """Worker thread.

    Inherits from QRunnable to handler worker thread setup, signals and wrap-up.

    :param callback: The function callback to run on this worker thread. Supplied args and
                     kwargs will be passed through to the runner.
    :type callback: function
    :param args: Arguments to pass to the callback function
    :param kwargs: Keywords to pass to the callback function
    """
    logger = getLogger("Worker")

    def __init__(self, compiler: ApcCompiler, fn: str, *args, **kwargs):
        super(Worker, self).__init__()

        # Store constructor arguments (re-used for processing)
        self.compiler = compiler
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

        # Add the callback to our kwargs
        self.kwargs["progress_callback"] = self.signals.progress

    def run(self):
        """Initialise the runner function with passed args, kwargs."""

        # Retrieve args/kwargs here; and fire processing using them
        try:
            self.logger.debug("running Worker")
            if self.fn == "update":
                result = self.compiler.update_json(*self.args, **self.kwargs)
            elif self.fn == "save":
                result = self.compiler.save(*self.args, **self.kwargs)
            elif self.fn == "compile":
                result = self.compiler.compile(*self.args, **self.kwargs)
            else:
                return 0

        except Exception as e:
            exctype, value, tb = sys.exc_info()
            self.logger.exception(e)
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)  # Return the result of the processing
        finally:
            self.signals.finished.emit()  # Done
