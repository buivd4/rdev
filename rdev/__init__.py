import os
import sys
import time
import logging
import subprocess

import click

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from watchdog.observers.api import DEFAULT_OBSERVER_TIMEOUT
from getpass import getpass

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')


class COLORS(object):
    PURPLE = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


def _get_what(event):
    return 'directory' if event.is_directory else 'file'


class RSyncEventHandler(FileSystemEventHandler):
    """RSync when the events captured."""

    def __init__(self, local_path, remote_path, rsync_options=''):
        self.local_path = local_path
        self.remote_path = remote_path
        self.rsync_options = rsync_options.split()
        self.sshpass()
        self.rsync()

    @staticmethod
    def log(log, color):
        logging.info('{}{}{}'.format(color, log, COLORS.END))
    
    def on_moved(self, event):
        super(RSyncEventHandler, self).on_moved(event)

        what = _get_what(event)
        self.log(
            'Info: Moved {}: from {} to {}'.format(
                what,
                event.src_path,
                event.dest_path
            ),
            COLORS.BLUE
        )

        self.rsync()

    def on_created(self, event):
        super(RSyncEventHandler, self).on_created(event)

        what = _get_what(event)
        self.log(
            'Info: Created {}: {}'.format(what, event.src_path),
            COLORS.GREEN
        )

        self.rsync()

    def on_deleted(self, event):
        super(RSyncEventHandler, self).on_deleted(event)

        what = _get_what(event)
        self.log(
            'Info: Deleted {}: {}'.format(what, event.src_path),
            COLORS.RED
        )

        self.rsync()

    def on_modified(self, event):
        super(RSyncEventHandler, self).on_modified(event)

        what = _get_what(event)
        self.log(
            'Info: Modified {}: {}'.format(what, event.src_path),
            COLORS.YELLOW
        )

        self.rsync()
    def sshpass(self):
        password=getpass()
        remote_host,remote_dir=self.remote_path.split(":")
        if subprocess.call('sshpass -p "{password}" ssh-copy-id -o StrictHostKeyChecking=no {remote_host}'.format(password=password,remote_host=remote_host),shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE):
            self.log('Error: Can\'t copy key to remote host.', COLORS.RED)
            sys.exit(1)
        else:
            self.log('Info: Copy ssh-key to {}'.format(remote_host),COLORS.PURPLE)
 
    def rsync(self, relative_path=None):
        self.log('Info: Start rsync', COLORS.PURPLE)

        local_path = self.local_path
        remote_path = self.remote_path
        if relative_path is not None:
            local_path = os.path.join(local_path, relative_path)
            remote_path = os.path.join(remote_path, relative_path)

        cmd = 'rsync -avzP {} {} {}'.format(
            ' '.join(self.rsync_options), local_path, remote_path
        )
        self.log(cmd, COLORS.BOLD)
        with open(os.devnull, 'w') as DEVNULL:
            subprocess.call(
                cmd.split(' '),
                stdout=DEVNULL,
                stderr=subprocess.STDOUT
            )


@click.command()
@click.argument('local-path')
@click.argument('remote-path')
@click.option(
    '--observer-timeout',
    default=DEFAULT_OBSERVER_TIMEOUT,
    help='The observer timeout, default {}'.format(
        DEFAULT_OBSERVER_TIMEOUT
    )
)
@click.option('--rsync-options', default='-a --delete', help='rsync command options')
@click.option('--rsync-file-opts', default=None, help='file with rsync options')
def main(
    local_path, remote_path,
    observer_timeout, rsync_options, rsync_file_opts
):
    if subprocess.call(['which', 'rsync'],stdout=subprocess.PIPE, stderr=subprocess.PIPE) != 0:
        print(
            COLORS.RED +
            'Error: You must install `rsync` before use rdev.' +
            COLORS.END
        )
        sys.exit(1)
    if subprocess.call(['which', 'sshpass'],stdout=subprocess.PIPE, stderr=subprocess.PIPE) != 0:
        print(
            COLORS.RED +
            'Error: You must install sshpass before use rdev.' +
            COLORS.END
        )
        sys.exit(1)
    if rsync_file_opts:
        with open(rsync_file_opts) as opts_file:
            opts = map(str.strip, opts_file)
            rsync_options += u' '.join(opts)
    event_handler = RSyncEventHandler(local_path, remote_path, rsync_options)
    observer = Observer(timeout=observer_timeout)
    observer.schedule(event_handler, local_path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == '__main__':
    main()
