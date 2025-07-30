import argparse
from .ResourceMonitor import ResourceMonitor

def main():
    parser = argparse.ArgumentParser(
        description = 'Monitor resource usage of processes.'
    )

    parser.add_argument(
        'pids',
        metavar = 'PID',
        type = int,
        nargs = '+',
        help = 'Process IDs to monitor.'
    )

    parser.add_argument(
        '-s', '-csp', '--close-save-path',
        dest = 'close_save_path',
        type = str,
        default = None,
        help = 'File to save the final frame when the window is closed.'
    )

    parser.add_argument(
        '-f', '-freq', '--frequency',
        dest = 'frequency',
        type = str,
        default = 20,
        help = 'Frequency of monitoring updates.'
    )

    parser.add_argument(
        '-w', '-win', '--window', '--window-size',
        dest = 'window_size',
        type = int,
        default = 10,
        help = 'Size of the monitoring window (in seconds).'
    )

    parser.add_argument(
        '-noc', '--no-cpu', '--disable-cpu',
        dest = 'watch_cpu',
        action = 'store_false',
        default = True,
        help = 'Disable CPU usage monitoring.'
    )

    parser.add_argument(
        '-nom', '--no-memory', '--disable-memory',
        dest = 'watch_memory',
        action = 'store_false',
        default = True,
        help = 'Disable memory usage monitoring.'
    )

    parser.add_argument(
        '-dsk', '--disk', '--enable-disk',
        dest = 'watch_disk',
        action = 'store_true',
        default = False,
        help = 'Enable disk I/O monitoring.'
    )

    args = parser.parse_args()

    monitor = ResourceMonitor(
        args.pids,
        watch_cpu = args.watch_cpu,
        watch_memory = args.watch_memory,
        watch_disk = args.watch_disk
    )

    monitor.start(
        close_save_path = args.close_save_path,
        frequency = args.frequency,
        window_size = args.window_size
    )

if __name__ == '__main__':
    main()
