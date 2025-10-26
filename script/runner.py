import subprocess
import threading

class CloudflareRunner:
    def __init__(self, log_callback):
        self.log_callback = log_callback
        self.process = None

    def run_command(self, command):
        def target():
            self.log_callback(f"[INFO] 启动命令: {' '.join(command)}")
            try:
                self.process = subprocess.Popen(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1
                )
                for line in self.process.stdout:
                    self.log_callback(line.rstrip())
                rc = self.process.wait()
                if rc == 0:
                    self.log_callback("[INFO] 进程结束: 退出码 0")
                else:
                    self.log_callback(f"[ERROR] 进程结束: 退出码 {rc}")
            except FileNotFoundError:
                self.log_callback("[ERROR] 未找到 cloudflared 可执行文件，请检查安装与 PATH")
            except Exception as e:
                self.log_callback(f"[ERROR] 子进程异常: {e}")
        threading.Thread(target=target, daemon=True).start()

    def stop(self):
        if self.process and self.process.poll() is None:
            self.process.terminate()
            self.log_callback("[WARN] 已请求终止进程")
