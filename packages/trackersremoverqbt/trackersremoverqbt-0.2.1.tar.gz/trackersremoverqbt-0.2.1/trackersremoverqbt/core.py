import argparse
import os
import platform
import shutil
import subprocess
import sys
import threading
import time
import importlib.metadata

from qbittorrentapi import Client, NotFound404Error
from rich import print
from rich.table import Table

DEFAULT_IGNORED_TRACKERS = {"** [DHT] **", "** [PeX] **", "** [LSD] **"}


class Spinner:
    busy = False
    delay = 0.1
    message = "\033[93mWaiting for connection to qBittorrent Web UI... \033[0m"

    @staticmethod
    def spinning_cursor():
        while 1:
            for cursor in '|/-\\':
                yield cursor

    def __init__(self, message=None, delay=None):
        self.spinner_generator = self.spinning_cursor()
        if delay and float(delay):
            self.delay = delay
        if message:
            self.message = f"\033[93m{message}\033[0m"

    def spinner_task(self):
        while self.busy:
            sys.stdout.write(f"\r{self.message}{next(self.spinner_generator)}")
            sys.stdout.flush()
            time.sleep(self.delay)

    def __enter__(self):
        self.busy = True
        threading.Thread(target=self.spinner_task).start()

    def __exit__(self, exception, value, tb):
        self.busy = False
        time.sleep(self.delay)
        print()
        if exception is not None:
            return False


def launch_qbittorrent():
    system = platform.system()

    if system == "Darwin":  # macOS
        app_path = "/Applications/qbittorrent.app"
        if os.path.exists(app_path):
            print("[yellow]Launching qBittorrent on macOS...[/yellow]")
            subprocess.Popen(["open", app_path])
        else:
            print("[red]qBittorrent.app not found in /Applications[/red]")

    elif system == "Windows":
        print("[yellow]Attempting to launch qBittorrent on Windows...[/yellow]")

        # Try PATH
        qbittorrent_path = shutil.which("qbittorrent")
        if qbittorrent_path:
            subprocess.Popen([qbittorrent_path], shell=True)
            print("[green]qBittorrent launched from PATH[/green]")
            return

        # Try common install locations
        common_paths = [
            r"C:\Program Files\qBittorrent\qbittorrent.exe",
            r"C:\Program Files (x86)\qBittorrent\qbittorrent.exe"
        ]
        for path in common_paths:
            if os.path.exists(path):
                subprocess.Popen([path], shell=True)
                print(f"[green]qBittorrent launched from {path}[/green]")
                return

        print("[red]qBittorrent not found in PATH or standard locations[/red]")

    else:
        print("[yellow]Autolaunch not supported on this platform[/yellow]")


def parse_args():
    parser = argparse.ArgumentParser(description="Remove non-ignored trackers from active qBittorrent downloads.")
    parser.add_argument("-H", "--host", default="localhost", help="qBittorrent Web UI host")
    parser.add_argument("-P", "--port", type=int, default=8080, help="qBittorrent Web UI port")
    parser.add_argument("-U", "--username", default="admin", help="qBittorrent Web UI username")
    parser.add_argument("-PSW", "--password", default="123456", help="qBittorrent Web UI password")
    parser.add_argument("--no-verify", default=True, help="Disable SSL certificate verification")
    parser.add_argument("-MDL", "--min-dl-speed", type=int, default=10, help="Minimum download speed in KB/s to remove trackers")
    parser.add_argument("--ignored-trackers", nargs="*", default=[], help="Additional trackers to ignore (added to defaults)")
    parser.add_argument("-QBT", "--launch-qbt", default=True, help="Launch qBittorrent if not running")

    try:
        version = importlib.metadata.version("trqbt")
    except importlib.metadata.PackageNotFoundError:
        version = "unknown"

    parser.add_argument("-V", "--version", action="version", version=f"TrackersRemover-qBittorrent {version}",
                        help="Show program version and exit")
    return parser.parse_args()


def main():
    args = parse_args()

    # if args.launch_qbt:
    #     print("[blue]Attempting to launch qBittorrent...[/blue]")
    #     launch_qbittorrent()
    #     time.sleep(3)

    client = Client(
        host=args.host,
        port=args.port,
        username=args.username,
        password=args.password,
        VERIFY_WEBUI_CERTIFICATE=not args.no_verify
    )

    print(args.host)

    with Spinner():
        while True:
            try:
                client.auth_log_in()
                print("[green]Connected to web qBittorrent[/green]")
                break
            except Exception as e:
                msg = str(e) if str(e) else "Error authenticating with qBittorrent Web UI"
                print(f"\n[red]Connection failed: {msg}[/red]")
                if not str(e):
                    print("[yellow]Please verify your host, port, username and password[/yellow]")
                print("[yellow]Please start qBittorrent Web UI[/yellow]")
                time.sleep(5)

    IGNORED_TRACKERS = DEFAULT_IGNORED_TRACKERS.union(args.ignored_trackers)
    MIN_DL_SPEED = args.min_dl_speed

    previous_snapshot = {}

    while True:
        try:
            all_torrents = client.torrents_info()
            current_snapshot = {}

            table = Table(title="Torrents with Non-Ignored Trackers")
            table.add_column("Name", style="cyan", no_wrap=True)
            table.add_column("Hash", style="dim", overflow="fold")
            table.add_column("State", style="green")
            table.add_column("DL Speed", justify="right")
            table.add_column("Trackers", style="magenta", overflow="fold")

            for t in all_torrents:
                try:
                    current_trackers = client.torrents_trackers(t.hash)
                    filtered_trackers = [tr.url for tr in current_trackers if tr.url not in IGNORED_TRACKERS]

                    if filtered_trackers:
                        key = t.hash
                        snapshot_data = {
                            "name": t.name,
                            "state": t.state,
                            "dlspeed": t.dlspeed,
                            "trackers": tuple(sorted(filtered_trackers)),
                        }

                        current_snapshot[key] = snapshot_data

                        if previous_snapshot.get(key) != snapshot_data:
                            trackers_str = ", ".join(filtered_trackers)
                            table.add_row(
                                t.name,
                                t.hash,
                                t.state,
                                f"{t.dlspeed / 1024:.1f} KB/s",
                                trackers_str
                            )

                            if current_snapshot != previous_snapshot:
                                print()
                                print(table)

                except Exception as e:
                    print(f"[red]Error retrieving trackers for {t.name}: {e}[/red]")

            previous_snapshot = current_snapshot

            torrents_to_clean = [t for t in all_torrents if t.state == 'downloading' and t.dlspeed > MIN_DL_SPEED * 1024]

            for torrent in torrents_to_clean:
                try:
                    current_trackers = client.torrents_trackers(torrent.hash)

                    for tr in current_trackers:
                        if tr.url in IGNORED_TRACKERS:
                            continue

                        try:
                            print(f"[cyan]Tracker cleaning for: [bold]{torrent.name}[/bold] ({torrent.hash}), DL speed {torrent.dlspeed / 1024:.1f} KB/s[/cyan]")

                            client.torrents_remove_trackers(
                                torrent_hash=torrent.hash,
                                urls=[tr.url]
                            )
                            print(f"[green]Tracker deleted for [bold]{torrent.name}[/bold] ({torrent.hash}): [bold]{tr.url}[/bold][/green]")
                        except Exception as remove_err:
                            print(f"[red]Error deleting tracker {tr.url} for {torrent.name}: {remove_err}[/red]")

                except NotFound404Error:
                    print("[red]Torrent not found[/red]")
                except Exception as err:
                    print(f"[red]Processing error: {err}[/red]")

        except Exception as e:
            print(f"[red]Overall error: {e}[/red]")

        time.sleep(1)


if __name__ == "__main__":
    main()
