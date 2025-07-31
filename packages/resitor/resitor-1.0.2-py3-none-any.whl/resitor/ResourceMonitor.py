import sys
import psutil
import matplotlib.pyplot as plot
import matplotlib.animation as animation
import time
from threading import Thread, Event, Lock
import subprocess

def start_monitor(pids, *, frequency = 20, window_size = 10, close_save_path = None,
                  log_path = None,
                  watch_cpu = True, watch_memory = True,
                  watch_disk_read = False, watch_disk_write = False):

    '''
    Launch a subprocess to monitor system resources for given PIDs using the CLI tool.

    Parameters:
        pids (int or list of int): Process ID(s) to monitor.
        frequency (int): Update frequency in Hz (default is 20).
        window_size (int): Duration of the sliding window in seconds (default is 10).
        close_save_path (str): Optional path to save the plot when the window closes.
        log_path (str): Optional path to write a CSV log of measurements.
        watch_cpu (bool): Whether to monitor CPU usage.
        watch_memory (bool): Whether to monitor memory usage.
        watch_disk_read (bool): Whether to monitor disk read I/O.
        watch_disk_write (bool): Whether to monitor disk write I/O.
    '''

    if type(pids) is not list:
        pids = [pids]

    cmd = [sys.executable, '-m', 'resitor', *map(str, pids)]

    if close_save_path is not None:
        cmd += ['-s', close_save_path]

    if log_path is not None:
        cmd += ['-l', log_path]

    if frequency is not None:
        cmd += ['-f', str(frequency)]

    if window_size is not None:
        cmd += ['-w', str(window_size)]

    if not watch_cpu:
        cmd += ['-noc']

    if not watch_memory:
        cmd += ['-nom']

    if watch_disk_read:
        cmd += ['-dskr']

    if watch_disk_write:
        cmd += ['-dskw']

    subprocess.Popen(cmd)

class ResourceMonitor:
    def __init__(self, pids, watch_cpu = True, watch_memory = True,
                 watch_disk_read = False, watch_disk_write = False):

        '''
        Initialize the ResourceMonitor for tracking CPU, memory, and disk usage of processes.
        Generally, users should use the `start_monitor` function instead of this constructor.

        Parameters:
            pids (list of int): List of PIDs to monitor.
            watch_cpu (bool): Enable CPU usage tracking.
            watch_memory (bool): Enable memory usage tracking.
            watch_disk_read (bool): Enable disk read I/O tracking.
            watch_disk_write (bool): Enable disk write I/O tracking.
        '''

        if not any([watch_cpu, watch_memory, watch_disk_read, watch_disk_write]):
            raise ValueError('At least one metric must be enabled.')

        self.watch_cpu = watch_cpu
        self.watch_memory = watch_memory
        self.watch_disk_read = watch_disk_read
        self.watch_disk_write = watch_disk_write

        self.start_time = time.time()
        self._stop_event = Event()
        self._data_lock = Lock()

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

        num_axes = sum([
            self.watch_cpu,
            self.watch_memory,
            self.watch_disk_read or self.watch_disk_write
        ])

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

        if self.watch_disk_read or self.watch_disk_write:
            self.ax_disk = self.axes[idx]
            self.ax_disk.set_title('Disk I/O (MB/s)')
            idx += 1

        else:
            self.ax_disk = None

        self.fig.tight_layout()

    def _monitor_loop(self):
        prev_disk = {}

        log = False
        if hasattr(self, '_log_file') and self._log_file:
            log = True

        while not self._stop_event.is_set() and self.data:
            elapsed = time.time() - self.start_time
            terminated_pids = []

            with self._data_lock:
                for pid, d in self.data.items():
                    try:
                        proc = d['proc']
                        d['x'].append(elapsed)

                        if self.watch_cpu:
                            cpu = proc.cpu_percent(interval = None)
                            if cpu is None or cpu < 0:
                                cpu = 0

                            d['cpu'].append(cpu)

                            if log:
                                self._log_file.write(f'{elapsed:.2f},{pid},cpu,{cpu:.2f}\n')

                        if self.watch_memory:
                            mem = proc.memory_info().rss / (1024 ** 2)
                            if mem is None or mem < 0:
                                mem = 0

                            d['memory'].append(mem)

                            if log:
                                self._log_file.write(f'{elapsed:.2f},{pid},memory,{mem:.2f}\n')

                        if self.watch_disk_read or self.watch_disk_write:
                            try:
                                io = proc.io_counters()
                                prev = prev_disk.get(pid)

                            except:
                                print('Disk I/O monitoring failed. psutil disk I/O is only available on Linux and Windows.')
                                plot.close()
                                sys.exit(1)

                            if self.watch_disk_read:
                                value = ((io.read_bytes - prev.read_bytes) / (1024 ** 2)) / self.update_period if prev else 0
                                if value is None or value < 0:
                                    value = 0

                                d['disk_read'].append(value)

                                if log:
                                    self._log_file.write(f'{elapsed:.2f},{pid},disk_read,{value:.4f}\n')

                            if self.watch_disk_write:
                                value = -((io.write_bytes - prev.write_bytes) / (1024 ** 2)) / self.update_period if prev else 0
                                if value is None or value > 0:
                                    value = 0

                                d['disk_write'].append(value)

                                if log:
                                    self._log_file.write(f'{elapsed:.2f},{pid},disk_write,{value:.4f}\n')

                            prev_disk[pid] = io

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
            name = f'PID {pid} - ' + d['proc'].name()

            if self.watch_cpu:
                self.ax_cpu.set_xlim(0, self.window_size)
                (cpu_line,) = self.ax_cpu.plot([], [], label = name)
                d['cpu_line'] = cpu_line
                lines.append(cpu_line)

            if self.watch_memory:
                self.ax_memory.set_xlim(0, self.window_size)
                (memory_line,) = self.ax_memory.plot([], [], label = name)
                d['memory_line'] = memory_line
                lines.append(memory_line)

            if self.watch_disk_read:
                self.ax_disk.set_xlim(0, self.window_size)
                (read_line,) = self.ax_disk.plot([], [], label = f'{name} Read')
                d['disk_read_line'] = read_line
                lines.append(read_line)

            if self.watch_disk_write:
                self.ax_disk.set_xlim(0, self.window_size)
                (write_line,) = self.ax_disk.plot([], [], label = f'{name} Write')
                d['disk_write_line'] = write_line
                lines.append(write_line)

        if self.watch_cpu:
            self.ax_cpu.legend(loc = 'upper left')

        if self.watch_memory:
            self.ax_memory.legend(loc = 'upper left')

        if self.watch_disk_read or self.watch_disk_write:
            self.ax_disk.legend(loc = 'upper left')

        return lines

    def _update_plot(self, frame):
        all_lines = []

        with self._data_lock:
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

                    if self.watch_disk_read:
                        d['disk_read'] = d['disk_read'][min_i:]

                    if self.watch_disk_write:
                        d['disk_write'] = d['disk_write'][min_i:]

                if self.watch_cpu:
                    d['cpu_line'].set_data(d['x'], d['cpu'])
                    all_lines.append(d['cpu_line'])

                if self.watch_memory:
                    d['memory_line'].set_data(d['x'], d['memory'])
                    all_lines.append(d['memory_line'])

                if self.watch_disk_read:
                    d['disk_read_line'].set_data(d['x'], d['disk_read'])
                    all_lines.append(d['disk_read_line'])

                if self.watch_disk_write:
                    d['disk_write_line'].set_data(d['x'], d['disk_write'])
                    all_lines.append(d['disk_write_line'])

            if valid_data_found:
                if self.watch_cpu:
                    self.ax_cpu.set_xlim(xmin, xmax)
                    self.ax_cpu.relim()
                    self.ax_cpu.autoscale_view()

                if self.watch_memory:
                    self.ax_memory.set_xlim(xmin, xmax)
                    self.ax_memory.relim()
                    self.ax_memory.autoscale_view()

                if self.watch_disk_read or self.watch_disk_write:
                    self.ax_disk.set_xlim(xmin, xmax)
                    self.ax_disk.relim()
                    self.ax_disk.autoscale_view()

        return all_lines

    def start(self, close_save_path = None, frequency = 20, window_size = 10, log_path = None):

        '''
        Start the monitoring thread and live plot display.

        Parameters:
            close_save_path (str): Optional path to save the final plot when the window closes.
            frequency (int): Update frequency in Hz (default is 20).
            window_size (float): Length of sliding time window in seconds (default is 10).
            log_path (str): Optional CSV file path to log data.
        '''

        self.update_period = 1 / float(frequency)
        self.window_size = float(window_size)

        if self.window_size <= 0:
            self.window_size = None

        if log_path is not None:
            self._log_file = open(log_path, 'w', buffering = 1)
            self._log_file.write('timestamp,pid,metric,value\n')

        else:
            self._log_file = None

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

        '''
        Stop the monitoring thread and optionally save the last plot and log.

        Parameters:
            save_path (str): Optional path to save the current plot as an image.
        '''
        
        self._stop_event.set()

        try:
            self.monitor_thread.join()

        except:
            print('Warning: Monitor thread could not be joined.')

        if save_path is not None:
            self.fig.savefig(save_path)
            print(f'Last frame saved to {save_path}')

        if hasattr(self, '_log_file') and self._log_file:
            self._log_file.close()
            print(f'Log saved to {self._log_file.name}')
