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
        '-dskr', '--disk-read', '--enable-disk-read',
        dest = 'watch_disk_read',
        action = 'store_true',
        default = False,
        help = 'Enable disk read monitoring.'
    )

    parser.add_argument(
        '-dskw', '--disk-write', '--enable-disk-write',
        dest = 'watch_disk_write',
        action = 'store_true',
        default = False,
        help = 'Enable disk write monitoring.'
    )

    parser.add_argument(
        '-dsk', '--disk', '--enable-disk',
        dest = 'watch_disk',
        action = 'store_true',
        default = False,
        help = 'Enable disk I/O monitoring (override read and write).'
    )

    parser.add_argument(
        '-l', '-log', '--log_path',
        dest = 'log_path',
        type = str,
        default = None,
        help = 'File to save the monitoring log.'
    )

    args = parser.parse_args()

    if args.watch_disk:
        args.watch_disk_read = True
        args.watch_disk_write = True

    monitor = ResourceMonitor(
        args.pids,
        watch_cpu = args.watch_cpu,
        watch_memory = args.watch_memory,
        watch_disk_read = args.watch_disk_read,
        watch_disk_write = args.watch_disk_write
    )

    monitor.start(
        close_save_path = args.close_save_path,
        frequency = args.frequency,
        window_size = args.window_size,
        log_path = args.log_path
    )

if __name__ == '__main__':
    main()
