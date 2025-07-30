import re
import asyncio


class VmMapMemory:
    def __init__(self):
        self.last_nonzero_memory = None

    async def get_process_memory(self, pid):
        cmd = ["top", "-l", "1", "-stats", "mem", "-pid", str(pid)]
        try:
            # 创建子进程并设置超时
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.DEVNULL
            )

            try:
                stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=1)
            except asyncio.TimeoutError:
                # 超时后确保子进程被终止
                proc.kill()
                await proc.wait()
                raise

            if proc.returncode == 0:
                # 解析 top 输出中的内存信息
                lines = stdout.decode().strip().split('\n')
                if lines:
                    last_line = lines[-1].strip()  # 获取最后一行
                    match = re.match(r'^([\d.]+)([GMK]?)$', last_line)

                    if match:
                        val, unit = float(match.group(1)), match.group(2)
                        memory_value = val * {
                            'G': 1024, 'M': 1, 'K': 1 / 1024, '': 1 / (1024 * 1024)
                        }.get(unit, 1)

                        if memory_value > 0:
                            self.last_nonzero_memory = memory_value
                        # 返回当前值或上一次非零值
                        return memory_value if memory_value != 0 else self.last_nonzero_memory
        except Exception as e:
            print(e)
        finally:
            if proc and proc.returncode is None:
                proc.kill()
                await proc.wait()
        # 如果未能获取到有效值，返回上一次非零值或默认值 0.0
        return self.last_nonzero_memory if self.last_nonzero_memory is not None else 0.0
