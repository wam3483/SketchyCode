import logging
import threading
from queue import Queue, Empty
from typing import Callable

class PlotterManager:
    def __init__(self):
        self._job_queue: Queue = Queue()
        self._current_job_thread: threading.Thread | None = None
        self._is_job_active: bool = False
        self._lock = threading.Lock()
        self._worker_thread = threading.Thread(target=self._job_worker, daemon=True)
        self._stop_signal = threading.Event()
        self._worker_thread.start()

    @property
    def is_job_active(self) -> bool:
        with self._lock:
            return self._is_job_active

    def stop_job(self) -> bool:
        """
        Attempt to stop current job execution.
        :return: True if job thread was stopped (or not alive anymore), False if still alive.
        """
        with self._lock:
            self._is_job_active = False
        if self._current_job_thread and self._current_job_thread.is_alive():
            self._current_job_thread.join(timeout=5)
            return not self._current_job_thread.is_alive()
        return True

    def queue_job(self, job) -> bool:
        """
        Add a job to the queue. Job must have a .run() method.
        :param job: Object with a .run() method
        :return: True if job was queued successfully
        """
        if not hasattr(job, "run") or not callable(job.run):
            logging.error("Invalid job: must have a callable 'run' method.")
            return False

        logging.info(f"Job queued: {job}")
        self._job_queue.put(job)
        return True

    def _job_worker(self):
        while not self._stop_signal.is_set():
            try:
                job = self._job_queue.get(timeout=1)
            except Empty:
                continue

            with self._lock:
                self._is_job_active = True
                self._current_job_thread = threading.Thread(
                    target=self._run_job_wrapper, args=(job,), daemon=True
                )
                self._current_job_thread.start()

            self._current_job_thread.join()
            with self._lock:
                self._is_job_active = False
                self._current_job_thread = None

    def _run_job_wrapper(self, job):
        try:
            logging.info(f"Running job: {job}")
            job.run()
        except Exception as e:
            logging.exception(f"Job failed: {e}")
        finally:
            logging.info(f"Job completed: {job}")

    def shutdown(self):
        """Gracefully stop the worker thread (optional use)."""
        self._stop_signal.set()
        self._worker_thread.join(timeout=5)