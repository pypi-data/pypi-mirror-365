import os
import sys
import inspect
from copy import deepcopy

from datetime import datetime

import torch
import torch.nn as nn
import thop


def summery_model(model: nn.Module, imgsz: int = 224) -> None:
    """
        Args:
            model: The model to be summarized.
            imgsz: The image of input size.
    """
    n_parameters = sum(p.numel() for p in model.parameters() if p.requires_grad)
    param_content = "{:<18}={:>8.3f}M".format("Overall parameters", n_parameters / 1e6)
    print(param_content)

    p = next(model.parameters())
    im = torch.empty((1, 3, imgsz, imgsz), device=p.device)  # input image in BCHW format
    flops = thop.profile(deepcopy(model), inputs=(im, ), verbose=False)[0] / 1E9 * 2
    flops_content = "{:<20}={:>8.1f}GFLOPs".format("Overall FLOPs (Thop)**", flops)  # 640x640 GFLOPs
    print(flops_content)

    save_dir = os.environ.get("LOG_PATH", "./output/log")
    os.makedirs(save_dir, exist_ok=True)
    with open(os.path.join(save_dir, "model_summery.log"), 'w') as f:
        f.write(param_content + '\n')
        f.write(flops_content + '\n')
    f.close()



class ModelLogger:
    def __init__(
            self,
            filename: str = None,
            use_time: bool = True,
            show_caller: bool = False,
    ) -> None:
        """Get parameters for training along with the learning rate.

                Args:
                    filename: The log file name. If None, a timestamped file will be created.
                    use_time: If True, each log entry will be prefixed with a timestamp.
                    show_caller: If True, each log entry will be prefixed with a caller.
                Returns:
                     None
                Note:
                    filename default is None, which will create a log file with the current timestamp.
                    use_time default is True, which will add a timestamp to each log entry.
                """
        self.log_dir = os.environ.get("LOG_PATH", "./output/log")
        os.makedirs(self.log_dir, exist_ok=True)
        if filename is None:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = f"{timestamp}.log"

        self.use_time = use_time
        self.log_file = os.path.join(self.log_dir, filename)
        self.terminal = sys.stdout
        self.show_caller = show_caller
        sys.stdout = self
        self.buffer = ""

    @staticmethod
    def _get_caller_info():
        """Finds the stack frame of the original print() call."""
        # The stack frame we want is the first one *outside* of this logger file.
        # This is a robust way to find where the print() was actually called from.
        f = inspect.currentframe()
        # Move up the stack until we're out of this file
        while hasattr(f, "f_code") and f.f_code.co_filename == __file__:
            f = f.f_back

        if f:
            # Format the caller info
            filename = os.path.basename(f.f_code.co_filename)
            return f"Code file name: ({filename}) function name: ({f.f_code.co_name}) line: ({f.f_lineno})"
        return "unknown:0"

    def write(self, message):
        """Rewrite the write method of stdout to buffer messages until they are complete."""
        self.terminal.write(message)
        self.buffer += message

        if "\n" in message:
            parts = []
            if self.use_time:
                parts.append(f"[{self.get_timestamp()}]")
            if self.show_caller:
                parts.append(f"[{self._get_caller_info()}]")

            content = " ".join(parts) + f" {self.buffer}" if parts else self.buffer

            try:
                with open(self.log_file, "a", encoding="utf-8") as f:
                    f.write(content)
            except Exception as e:
                self.terminal.write(f"Error writing to log file: {e}\n")
            self.buffer = ""

    def flush(self):
        """Rewriting the flush method of stdout"""
        self.terminal.flush()

        if self.buffer:
            parts = []
            if self.use_time:
                parts.append(f"[{self.get_timestamp()}]")
            if self.show_caller:
                parts.append(f"[{self._get_caller_info()}]")

            content = " ".join(parts) + f" {self.buffer}" if parts else self.buffer
            try:
                with open(self.log_file, "a", encoding="utf-8") as f:
                    f.write(content)
            except Exception as e:
                self.terminal.write(f"Error writing to log file: {e}\n")
            self.buffer = ""

    @staticmethod
    def get_timestamp():
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# 示例用法
if __name__ == "__main__":
    os.environ["LOG_PATH"] = "./logs"

    logger1 = ModelLogger("custom.log")
    print("This is a log with a custom named file.")

    logger2 = ModelLogger()
    print("This is a log with a time named file.")