#!/usr/bin/env python3
# Standard Library
import contextlib, threading, time

# Local Library
from app import api, gui

# Third-Party Library
import uvicorn

class Server(uvicorn.Server):
    def install_signal_handlers(self):
        pass

    @contextlib.contextmanager
    def run_in_thread(self):
        thread = threading.Thread(target=self.run)
        thread.start()

        try:
            while not self.started:
                time.sleep(1e-3)
            yield
        finally:
            self.should_exit = True
            thread.join()

if __name__ == "__main__":
    Config = uvicorn.Config(app=api.app, host="127.0.0.1", port=8000, loop="asyncio")

    with Server(config=Config).run_in_thread():
        gui.open("http://127.0.0.1:8000")