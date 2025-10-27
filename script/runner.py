import subprocess
import threading

class CloudflareRunner:
    def __init__(self, log_callback=None):
        self.log_callback = log_callback
        self.process = None

    def run_command(self, cmd, return_process=False):
        """
        如果 return_process=True，则返回 Popen 对象
        否则异步读取输出并写入 GUI 日志
        """
        if return_process:
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            threading.Thread(target=self._read_output, args=(self.process,), daemon=True).start()
            return self.process

        def target():
            try:
                proc = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                self._read_output(proc)
            except Exception as e:
                if self.log_callback:
                    self.log_callback(f"[ERROR] {e}")

        threading.Thread(target=target, daemon=True).start()

    def _read_output(self, proc):
        for line in proc.stdout:
            if self.log_callback:
                self.log_callback(line.rstrip())
        proc.wait()

    def stop(self):
        if self.process and self.process.poll() is None:
            self.process.terminate()
            if self.log_callback:
                self.log_callback("[INFO] 隧道进程已终止")
            self.process = None
        else:
            if self.log_callback:
                self.log_callback("[WARN] 没有正在运行的隧道进程")
