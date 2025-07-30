import sys
import psutil
import matplotlib.pyplot as plot
import matplotlib.animation as animation
import time
from threading import Thread, Event
import subprocess

# TODO: Add documentation
# TODO: Add tests

def start_monitor(pids, *, frequency = 20, window_size = 10, close_save_path = None,
                  watch_cpu = True, watch_memory = True,
                  watch_disk = True):

    if type(pids) is not list:
        pids = [pids]

    cmd = [sys.executable, '-m', 'resitor', *map(str, pids)]

    if close_save_path is not None:
        cmd += ['-s', close_save_path]

    if frequency is not None:
        cmd += ['-f', str(frequency)]

    if window_size is not None:
        cmd += ['-w', str(window_size)]

    if not watch_cpu:
        cmd += ['-noc']

    if not watch_memory:
        cmd += ['-nom']

    if watch_disk:
        cmd += ['-dsk']

    subprocess.Popen(cmd)

class ResourceMonitor:
    def __init__(self, pids, watch_cpu = True, watch_memory = True,
                 watch_disk = False):
        if not any([watch_cpu, watch_memory, watch_disk]):
            raise ValueError('At least one metric must be enabled.')

        self.watch_cpu = watch_cpu
        self.watch_memory = watch_memory
        self.watch_disk = watch_disk

        self.start_time = time.time()
        self._stop_event = Event()

        self.data = {}

        for pid in pids:
            try:
                proc = psutil.Process(pid)
                self.data[pid] = {
                    'proc': proc,
                    'x': [],
                    'cpu': [],
                    'memory': [],
                    'disk_read': [],
                    'disk_write': [],
                    'cpu_line': None,
                    'memory_line': None,
                    'disk_read_line': None,
                    'disk_write_line': None,
                }
            except psutil.NoSuchProcess:
                print(f'Warning: PID {pid} does not exist.')

        if not self.data:
            print('No valid PIDs provided for monitoring.')
            sys.exit(1)

        plot.style.use('seaborn-v0_8')
        num_axes = sum([self.watch_cpu, self.watch_memory, self.watch_disk])
        self.fig, self.axes = plot.subplots(num_axes, 1, sharex = True)

        if num_axes == 1:
            self.axes = [self.axes]

        idx = 0
        if self.watch_cpu:
            self.ax_cpu = self.axes[idx]
            self.ax_cpu.set_title('CPU Usage (%)')
            idx += 1
        else:
            self.ax_cpu = None

        if self.watch_memory:
            self.ax_memory = self.axes[idx]
            self.ax_memory.set_title('Memory Usage (MB)')
            idx += 1
        else:
            self.ax_memory = None

        if self.watch_disk:
            self.ax_disk = self.axes[idx]
            self.ax_disk.set_title('Disk Read/Write (MB/s)')
            idx += 1
        else:
            self.ax_disk = None

        self.fig.tight_layout()

    def _monitor_loop(self):
        prev_disk = {}
        while not self._stop_event.is_set() and self.data:
            elapsed = time.time() - self.start_time
            terminated_pids = []

            for pid, d in self.data.items():
                try:
                    proc = d['proc']
                    if self.watch_cpu:
                        d['cpu'].append(proc.cpu_percent(interval = None))

                    if self.watch_memory:
                        d['memory'].append(proc.memory_info().rss / (1024 ** 2))

                    if self.watch_disk:
                        try:
                            io = proc.io_counters()
                            prev = prev_disk.get(pid)
                            if prev:
                                d['disk_read'].append(((io.read_bytes - prev.read_bytes) / (1024 ** 2)) / self.update_period)
                                d['disk_write'].append(-((io.write_bytes - prev.write_bytes) / (1024 ** 2)) / self.update_period)
                            else:
                                d['disk_read'].append(0)
                                d['disk_write'].append(0)

                            prev_disk[pid] = io

                        except:
                            d['disk_read'].append(0)
                            d['disk_write'].append(0)

                            plot.close()
                            print('Disk I/O monitoring failed. Currently, it is only available on Windows, Linux, BSD, and AIX. Please disable disk monitoring.')
                            sys.exit(1)

                    d['x'].append(elapsed)

                except psutil.NoSuchProcess:
                    print(f'PID {pid} has terminated.')
                    terminated_pids.append(pid)

            for pid in terminated_pids:
                del self.data[pid]

            if not self.data:
                print('All monitored processes have terminated.')
                self._stop_event.set()

            time.sleep(self.update_period)

    def _init_plot(self):
        lines = []
        for pid, d in self.data.items():
            if self.watch_cpu:
                self.ax_cpu.set_xlim(0, self.window_size)
                (cpu_line,) = self.ax_cpu.plot([], [], label = f'PID {pid}')
                d['cpu_line'] = cpu_line
                lines.append(cpu_line)

            if self.watch_memory:
                self.ax_memory.set_xlim(0, self.window_size)
                (memory_line,) = self.ax_memory.plot([], [], label = f'PID {pid}')
                d['memory_line'] = memory_line
                lines.append(memory_line)

            if self.watch_disk:
                self.ax_disk.set_xlim(0, self.window_size)
                (read_line,) = self.ax_disk.plot([], [], label = f'PID {pid} Read')
                (write_line,) = self.ax_disk.plot([], [], label = f'PID {pid} Write')
                d['disk_read_line'] = read_line
                d['disk_write_line'] = write_line
                lines += [read_line, write_line]

        if self.watch_cpu:
            self.ax_cpu.legend(loc = 'upper left')

        if self.watch_memory:
            self.ax_memory.legend(loc = 'upper left')

        if self.watch_disk:
            self.ax_disk.legend(loc = 'upper left')

        return lines

    def _update_plot(self, frame):
        all_lines = []
        if not self.data:
            print('No data left.')
            sys.exit(1)

        xmax = 0
        xmin = float('inf')
        valid_data_found = False

        for d in self.data.values():
            if not d['x']:
                continue

            valid_data_found = True
            xmax = max(xmax, d['x'][-1])
            xmin = xmax - self.window_size if self.window_size is not None else min(xmin, d['x'][0])

            if self.window_size is not None:
                min_i = next((i for i, val in enumerate(d['x']) if val >= xmin - self.update_period), 0)
                d['x'] = d['x'][min_i:]

                if self.watch_cpu:
                    d['cpu'] = d['cpu'][min_i:]
                if self.watch_memory:
                    d['memory'] = d['memory'][min_i:]
                if self.watch_disk:
                    d['disk_read'] = d['disk_read'][min_i:]
                    d['disk_write'] = d['disk_write'][min_i:]

            if self.watch_cpu:
                d['cpu_line'].set_data(d['x'], d['cpu'])
                all_lines.append(d['cpu_line'])
            if self.watch_memory:
                d['memory_line'].set_data(d['x'], d['memory'])
                all_lines.append(d['memory_line'])
            if self.watch_disk:
                d['disk_read_line'].set_data(d['x'], d['disk_read'])
                d['disk_write_line'].set_data(d['x'], d['disk_write'])
                all_lines.extend([d['disk_read_line'], d['disk_write_line']])

        # Only update axis limits if valid data was found
        if valid_data_found:
            if self.watch_cpu:
                self.ax_cpu.set_xlim(xmin, xmax)
                self.ax_cpu.relim()
                self.ax_cpu.autoscale_view()
            if self.watch_memory:
                self.ax_memory.set_xlim(xmin, xmax)
                self.ax_memory.relim()
                self.ax_memory.autoscale_view()
            if self.watch_disk:
                self.ax_disk.set_xlim(xmin, xmax)
                self.ax_disk.relim()
                self.ax_disk.autoscale_view()

        return all_lines


    def start(self, close_save_path = None, frequency = 20, window_size = 10):
        self.update_period = 1 / float(frequency)
        self.window_size = float(window_size)

        if self.window_size <= 0:
            self.window_size = None

        self.monitor_thread = Thread(target = self._monitor_loop, daemon = True)
        self.monitor_thread.start()

        self._animation = animation.FuncAnimation(
            self.fig,
            self._update_plot,
            init_func = self._init_plot,
            interval = self.update_period * 1000,
            blit = False,
            cache_frame_data = False
        )

        def _on_close(event):
            self.stop(save_path = close_save_path)

        self.fig.canvas.mpl_connect('close_event', _on_close)

        plot.show()

    def stop(self, save_path = None):
        self._stop_event.set()
        self.monitor_thread.join()

        if save_path is not None:
            self.fig.savefig(save_path)
            print(f'Last frame saved to {save_path}')