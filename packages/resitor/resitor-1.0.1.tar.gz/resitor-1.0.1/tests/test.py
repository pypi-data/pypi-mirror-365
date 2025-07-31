import time
import os
from resitor import start_monitor

if __name__ == '__main__':
    pid = os.getpid()

    monitor = start_monitor(
        [pid], # Add more PIDs as needed
        close_save_path = 'tests/test_save.png',
        log_path = 'tests/test_log.txt',
        frequency = 20,
        window_size = 10,
        watch_cpu = True,
        watch_memory = True,
        watch_disk_read = False
    )

    data = []
    i = 0

    while True:
        i += 1
        print(f'PID: {pid}, Iteration: {i}')
        data.append(' ' * 10 ** 6)
        time.sleep(1)
