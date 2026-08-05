import threading
import time

import numpy as np
import sounddevice as sd


class DoubleClapControl:
    def __init__(
        self,
        clap_threshold=0.35,
        release_threshold=0.12,
        min_clap_gap=0.15,
        max_clap_gap=0.70,
        toggle_cooldown=1.0,
    ):
        self.clap_threshold = clap_threshold
        self.release_threshold = release_threshold
        self.min_clap_gap = min_clap_gap
        self.max_clap_gap = max_clap_gap
        self.toggle_cooldown = toggle_cooldown

        self._controls_enabled = threading.Event()
        self._first_clap_time = None
        self._last_toggle_time = 0.0
        self._ready_for_clap = True
        self._stream = None

    def start(self):
        if self._stream is not None:
            return

        self._stream = sd.InputStream(
            samplerate=16_000,
            channels=1,
            dtype="float32",
            blocksize=512,
            callback=self._audio_callback,
        )

        try:
            self._stream.start()
        except Exception:
            self._stream.close()
            self._stream = None
            raise

    def stop(self):
        if self._stream is None:
            return

        self._stream.stop()
        self._stream.close()
        self._stream = None

    def is_enabled(self):
        return self._controls_enabled.is_set()

    def set_enabled(self, enabled):
        if enabled:
            self._controls_enabled.set()
        else:
            self._controls_enabled.clear()

    def toggle(self):
        self.set_enabled(not self.is_enabled())
        state = "ON" if self.is_enabled() else "OFF"
        print(f"Hand controls: {state}")

    def _audio_callback(self, audio_data, frames, time_info, status):
        del frames, time_info

        if status:
            print(f"Microphone status: {status}")

        volume = float(np.max(np.abs(audio_data)))

        if volume <= self.release_threshold:
            self._ready_for_clap = True
            return

        if volume < self.clap_threshold or not self._ready_for_clap:
            return

        self._ready_for_clap = False
        self._register_clap(time.monotonic())

    def _register_clap(self, clap_time):
        if clap_time - self._last_toggle_time < self.toggle_cooldown:
            return

        if (
            self._first_clap_time is None
            or clap_time - self._first_clap_time > self.max_clap_gap
        ):
            self._first_clap_time = clap_time
            return

        clap_gap = clap_time - self._first_clap_time

        if clap_gap < self.min_clap_gap:
            return

        self.toggle()
        self._last_toggle_time = clap_time
        self._first_clap_time = None
