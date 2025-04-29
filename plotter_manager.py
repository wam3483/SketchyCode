import logging
import threading
from plotter.xy_plotter import XYPlotter


class PlotterManager:
    def __init__(self, plotter : XYPlotter):
        self._plotter = plotter
        self._job = None
        self._job_thread = None
        self._is_job_active = False
        self._lock = threading.Lock()

    @property
    def is_job_active(self):
        return self._is_job_active

    def stop_job(self) -> bool:
        """
        Flags job as needing to stop, and attempts to joins with thread running job for 5 seconds.
        :return: whether job thread was successfully stopped
        """
        with self._lock:
            self._is_job_active = False
            self._job_thread.join(5) # wait 5 seconds at most for thread to stop.
            return self._job_thread.is_alive()

    def start_job(self, job) -> bool:
        with self._lock:
            if self._is_job_active:
                return False

            logging.info(f"starting job : {job}")
            self._job = job
            self._is_job_active = True

            # Start job in a background thread
            self._job_thread = threading.Thread(target=self._run_job_wrapper, daemon=True)
            self._job_thread.start()

            return True

    def _run_job_wrapper(self):
        try:
            logging.info(f"running job : {self._job}")
            self._job.run()
        finally:
            self._is_job_active = False