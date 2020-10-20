#!/usr/bin/python3
import time
import subprocess
import os
import shutil
import threading
import sys
import psutil
from datetime import datetime
import filecmp

rsync_idle = False


# def is_destination_valid(destination: str) -> bool:
#     if not os.path.exists(destination):
#         message = f"{destination} not found ! Aborting..."
#         print(message)
#
#         # create def handle_panic(message)
#         # panic abort!
#         # logger.error("OMG!")
#         # dispatch alert
#
#         sys.exit()
#     elif os.path.isfile(destination):
#
#         message = f"{destination} is not a folder !"
#         # handle panic
#         print(message)
#         sys.exit(1)
#
#     else:
#         print("detination valid!")
#         return True


# def is_enough_free_space(destination: str, backup_threshold: int) -> bool:
#     free_space = shutil.disk_usage(destination).free
#     free_space_gb = free_space / 1024 / 1024 / 1024
#     if free_space_gb < backup_threshold:
#         message = f"Only {free_space_gb} GB are available ,{backup_threshold} GB are required !\n" \
#                   f"Not enough free space to execute a backup ! Aborting... "
#
#         print(message)
#         # handle panic
#         # logger.error("OMG!")
#         sys.exit(1)
#     else:
#         print("Free space OK!")
#         return True


# def is_user_permitted(destination: str) -> bool:
#     if os.access(destination, os.R_OK) \
#             and os.access(destination, os.W_OK) \
#             and os.access(destination, os.X_OK):
#         print("User permistted")
#         return True
#     else:
#         # handle panic
#         print("handling permission panic")
#         return False


# def is_previous_backup_running(pid: str) -> bool:
#     print(f"no backup is currently executed !{pid}")
#     return True

    # check process_id
    # check checkpoint file for status
    # check checkpoit file for timestamp
    # check checkpoint file for strted and done


# def is_rsync_present():
#     if not shutil.which('rsync'):
#         sys.stderr.write("rsync executable not found in PATH\n")
#         sys.exit(1)


# def get_rsync_io_count():
#     io_count = (0, 0)
#     time.sleep(1)
#     for proc in psutil.process_iter():
#         if proc.name() == "rsync":
#             try:
#                 io_count = (proc.io_counters()[0], proc.io_counters()[1])
#             except Exception as e:
#                 print("psutil crashed retrieving io")
#                 print(e)
#                 # log error here
#     return io_count

    # def is_rsync_io_idle():
    #     global rsync_idle
    #     # get_rsync_io_count()
    #     # for proc in psutil.process_iter():
    #     #     if proc.name() == "rsync":
    #     #         print(f"process name {proc.name()} -> IO COUNT {proc.io_counters()}")
    #     #         print(f"READ COUNT-> {proc.io_counters()[0]}, WRITE COUNT-> {proc.io_counters()[1]}")

    #     rsync_idle = True



# def run_watchdog(seconds) -> None:
#     # watchdog will sleep determined interval and check IO ,
#     # in no IO for the interval , watchdog will kill rsync proccesses
#     # old_io = (old_read_count, old_write_count)  = get_rsync_io_count()
#
#     while not rsync_idle:
#         old_io_count = get_rsync_io_count()
#         print("BOOM **************************")
#         print(old_io_count, type(old_io_count))
#
#         time.sleep(seconds)
#
#         new_io_count = get_rsync_io_count()
#         print("BOOM ******************************")
#         print(new_io_count, type(new_io_count))
#         print("run here method _check_rsync_io")
#
#         delta = tuple(new - old for old, new in zip(old_io_count, new_io_count))
#         print(f"DELTA DELTA !!! ******************************{delta}")
#
#         if delta[0] == 0 or delta[1] == 0:
#             # if is_rsync_io_idle():
#             print(f"RSYNC IDLE FOR {seconds} seconds -> sending kill ")
#             kill_rsync()
#             #         handle_panic()
#             break


# def run_rsync():
#     rsync_cmd = [
#         "rsync",
#         # "-avzvvhrtplHP",
#         "-avhW", "--no-compress", "--progress",
#         "--no-perms",
#         # "/home/iidwuurliik/"
#         "/home/iidwuurliik/",  # Desktop/py_dev/",
#         "/tmp/" + "9backup_" + str(datetime.now().strftime("%d-%m-%Y")),
#     ]
#
#     subprocess.Popen(rsync_cmd, shell=False)


def kill_rsync():
    for proc in psutil.process_iter():
        # print(proc.name())

        if proc.name() == "rsync":
            print(f"Lets kill {proc.pid}")
            os.kill(proc.pid, 9)


if __name__ == '__main__':
    # kill_rsync()
    # is_destination_valid("/home/iidwuurliik/")
    # is_enough_free_space("/home/", 5)
    # is_user_permitted("/home/iidwuurliik/")
    # is_previous_backup_running("3456")
    # is_rsync_present()
    #
    # rsync_thread = threading.Thread(target=run_rsync)
    # rsync_thread.start()
    # time.sleep(1)
    # watchdog_thread = threading.Thread(target=run_watchdog(3))
    # watchdog_thread.start()

    print("RSYNC DONE!")

    rsync_thread._stop
    dest = "/tmp/9backup_" + str(datetime.now().strftime("%d-%m-%Y"))
    print(dest)
    filecmp.dircmp('/home/iidwuurliik/Desktop/py_dev', dest).report_full_closure()
    # print(get_rsync_io_count())



# have an updated section on various limitations
