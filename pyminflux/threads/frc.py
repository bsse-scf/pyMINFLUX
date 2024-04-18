import os

import numpy as np
from PySide6.QtCore import QObject, QRunnable, QThread, QThreadPool, Signal, Slot

from pyminflux.fourier import estimate_resolution_by_frc
from pyminflux.threads.common import CancelFlag


class FRCWorkerSignals(QObject):
    """Encapsulates Signals to be used by the Workers."""

    # Signal progress, completion, and request for stop
    progress = Signal(int)
    result = Signal(int, np.ndarray)


class FRCWorker(QRunnable):
    """AutoUpdateCheckerWorker to run the FRC analysis in parallel over all bins."""

    def __init__(
        self, index, processor, start_time, end_time, sxy, rx, ry, n_reps, cancel_flag
    ):
        """Constructor."""

        super().__init__()
        self.index = index
        self.processor = processor
        self.start_time = start_time
        self.end_time = end_time
        self.sxy = sxy
        self.rx = rx
        self.ry = ry
        self.n_reps = n_reps
        self.signals = FRCWorkerSignals()
        self.cancel_flag = cancel_flag

    def run(self):
        # Check that the processing has not been interrupted
        if self.cancel_flag.is_cancelled():
            # Signal completion
            self.signals.result.emit(self.index, None)
            self.signals.progress.emit(1)
            return

        # Extract the data
        df = self.processor.select_by_1d_range(
            "tim", x_range=(self.start_time, self.end_time)
        )
        df_gr = df.groupby("tid")
        mx = df_gr["x"].mean()
        my = df_gr["y"].mean()

        # Estimate the resolution by FRC
        _, _, _, resolutions, _ = estimate_resolution_by_frc(
            x=mx,
            y=my,
            sx=self.sxy,
            sy=self.sxy,
            rx=self.rx,
            ry=self.ry,
            num_reps=self.n_reps,
            seed=None,
            return_all=True,
        )

        # Convert to nm
        resolutions = 1e9 * np.array(resolutions)

        # Signal completion
        self.signals.result.emit(self.index, resolutions)
        self.signals.progress.emit(1)


class FRCProcessorThread(QThread):
    # Signal progress and completion
    processing_started = Signal()
    processing_progress_updated = Signal(int)
    processing_interrupted = Signal()
    processing_finished = Signal()

    def __init__(self, processor, t_start, t_steps, sxy, rx, ry, n_reps):
        """Constructor."""
        super().__init__()

        # Set arguments
        self.processor = processor
        self.t_start = t_start
        self.t_steps = t_steps
        self.sxy = sxy
        self.rx = rx
        self.ry = ry
        self.n_reps = n_reps

        # Initialize a thread pool
        self.thread_pool = QThreadPool.globalInstance()
        self.thread_pool.setMaxThreadCount(os.cpu_count())

        # Keep track of the progress of the various threads
        self.progress = 0

        # Initialize output
        self.all_resolutions = None

        # Initialize CancelFlag to communicate to AutoUpdateCheckerWorker in a thread-safe manner
        self.cancel_flag = CancelFlag()

    def run(self):
        """Run the computation."""

        # Signal start
        self.processing_started.emit()

        # Allocate space for the results
        self.all_resolutions = np.empty(
            (len(self.t_steps), self.n_reps), dtype=np.float32
        )
        self.all_resolutions.fill(np.nan)

        # Reset the progress counter
        self.progress = 0

        # Create the workers and add them to the thread pool
        for i, t in enumerate(self.t_steps):
            if self.cancel_flag.is_cancelled():
                # This is unlikely: threads are added very fast to the QThreadPool's queue
                self.processing_interrupted.emit()
                break

            # Create the processor_thread
            worker = FRCWorker(
                index=i,
                processor=self.processor,
                start_time=self.t_start,
                end_time=t,
                sxy=self.sxy,
                rx=self.rx,
                ry=self.ry,
                n_reps=self.n_reps,
                cancel_flag=self.cancel_flag,
            )

            # Attach all signals
            worker.signals.result.connect(self.store_result)
            worker.signals.progress.connect(self.broadcast_update_progress)

            # Add the thread to the pool and start it
            self.thread_pool.start(
                worker
            )  # Add the processor_thread to the thread pool

        # Wait for all threads to finish
        self.thread_pool.waitForDone()

        # Signal completion
        self.processing_finished.emit()

    def stop(self):
        # Inform the queued Workers to skip computation
        self.cancel_flag.cancel()

        # Clear the ThreadPool queue
        self.thread_pool.clear()

    @Slot(int, np.ndarray)
    def store_result(self, index, result):
        if result is not None and self.all_resolutions is not None:
            self.all_resolutions[index, :] = result

    def broadcast_update_progress(self, value):
        # Signal progress
        self.progress += value
        self.processing_progress_updated.emit(
            int(np.round(100 * (self.progress + 1) / len(self.t_steps)))
        )
