import filecmp
import logging.config
import os
import pathlib
import random
import shutil
import string
import subprocess
import sys
import threading
import time
from datetime import datetime
from typing import Tuple
from backup_settings import BACKUP_DESTINATION, BACKUP_SOURCE
from os import path

import psutil

from backup_settings import EMAIL_ALERT_CONFIG
from backup_settings import LOG_CONF, LOG_FOLDER_PATH
from email_alert_dispatcher import EmailAlertDispatcher

_rsync_idle = False

logging.basicConfig()
logger = logging.getLogger('backup_service')
logging.config.dictConfig(LOG_CONF)
logger.setLevel(logging.DEBUG)
logger.handlers[0].doRollover()


def is_destination_valid(destination: str) -> bool:
    """
    Returns evaluation if folder path is valid destination, if false executes panic_abort method
    """
    if not os.path.exists(destination):
        message = f"Destination {destination} not found ! Aborting...execution"
        panic_abort(message)
        return False

    elif os.path.isfile(destination):
        message = f"Destination {destination} is not a folder ! Aborting...execution"
        panic_abort(message)
        return False

    else:
        logger.info(f"Destination {destination} is valid ... proceeding")
        return True


def is_enough_free_space(destination_path: str, backup_threshold_gb: int) -> bool:
    """ Returns evaluation if drive has sufficient space for backup,
    if false executes panic_abort method
    """
    free_space = shutil.disk_usage(destination_path).free
    free_space_gb = free_space / 1024 / 1024 / 1024
    if free_space_gb < backup_threshold_gb:
        message = f"Only {int(free_space_gb)} GB are available ,{backup_threshold_gb} GB are required !\n" \
                  f"Insufficient free space to execute a backup ! Aborting... "
        panic_abort(message)
        sys.exit(1)
    else:
        logger.info(f"Free space validated , drive has {int(free_space_gb)} GB of free space... proceeding")
        return True


def is_user_permitted(destination: str) -> bool:
    """
    Returns evaluation if current user has enough permission to read , write , execute in provided folder,
    if false executes panic_abort method
    """

    if os.access(destination, os.R_OK) \
            and os.access(destination, os.W_OK) \
            and os.access(destination, os.X_OK):
        logger.info("User permissions validated ... proceeding")
        return True
    else:
        message = "Insufficient privileges! Aborting..."
        panic_abort(message)
        return False


def is_rsync_present() -> bool:
    """
    Returns evaluation if rsync utility is present in PATH,
    if false executes panic_abort method
    """
    if not shutil.which('rsync'):
        message = "rsync executable not found ! Aborting..."
        panic_abort(message)
        return False
    logger.info("rsync executable found... proceeding")
    return True


def is_rsync_not_running() -> bool:
    """
    Returns evaluation if another instance of rsync is running (presumably previous backup ?),
    if false executes panic_abort method
    """
    for proc in psutil.process_iter():
        if proc.name() == "rsync":
            message = f"{proc.name} rsync is already running ! aborting..."
            panic_abort(message)
            return False
        else:
            logger.info("No other instances of rsync detected... proceeding")
            return True


def panic_abort(error_message: str) -> None:
    """
    Aborts execution whenever an error that blocks a successful backup occurs
    executes dispatch_failure_alert_by_email method with details
    :param error_message: message with reason to abort
    :return: None
    """
    logger.debug(error_message)
    dispatch_failure_alert_by_email(error_message)
    sys.exit(1)


def dispatch_failure_alert_by_email(message: str) -> None:
    """
    Sends an email with provided message and log attachment
    """
    # TODO replace ead class instantiation to be more flexible
    # TODO replace with SMTP log handler if alerting is done my email
    # TODO before interview ! Eblan ne zabud !
    #  ADD ConnectionRefusedError: [Errno 111] Connection refused try /  catch

    logger.info(f"Sending email to {EMAIL_ALERT_CONFIG['_email']}")
    ead = EmailAlertDispatcher(EMAIL_ALERT_CONFIG["_email"],
                               EMAIL_ALERT_CONFIG["_password"],
                               EMAIL_ALERT_CONFIG["_send_to"],
                               "Critical Failure during backup !",
                               message,
                               EMAIL_ALERT_CONFIG["_file_attachment_path"])
    ead.compose_msg()
    ead.smtp_send()


def get_process_io_count(process_name: str) -> Tuple[int, int]:
    """
    Utility that extracts io data from psutil.io_counters ,
    :return: [read io , write io] only
    """
    io_count = (0, 0)
    time.sleep(1)
    for proc in psutil.process_iter():
        if proc.name() == process_name:
            try:
                io_count = (proc.io_counters()[0], proc.io_counters()[1])
            except Exception as e:
                logger.error("Psutil crashed retrieving io")
                logger.exception(e)
    return io_count


def if_backup_exists(backup_path : str) -> bool:
    """
    Validates is today's back is already present
    :param backup_path:
    :return:
    """
    if path.exists(backup_path):
        logger.warning("folder already exists , rsync will update delta only")
        return True
    logger.info("Today's backup not found")
    return False


def run_rsync() -> None:
    """
    Executed rsync command with provided arguments
    :return: None
    """
    logger.info("rsync started")
    rsync_cmd = [
        "rsync",
        "-avhW", "--no-compress", "--progress",
        "--no-perms",
        # BACKUP_SOURCE,
        "/home/iidwuurliik/",
        # BACKUP_DESTINATION,
        "/tmp/" + "backup_" + str(datetime.now().strftime("%d-%m-%Y")),
    ]

    subprocess.Popen(rsync_cmd, shell=False)


def kill_rsync() -> None:
    """
    send kill -9 to rsync process
    :return:
    """
    for proc in psutil.process_iter():
        if proc.name() == "rsync":
            logger.info(f"killing  rsync  {proc.pid}")
            os.kill(proc.pid, 9)


def run_watchdog(seconds) -> None:
    """
    Watchdog will sleep determined interval and check rsync IO ,
    if no IO detected for the provided interval , watchdog will execute os.kill of rsync processes (3)
    if io_delta (current - previous) is 0 , will result on os.kill()
    """

    while not _rsync_idle:
        logger.info("watchdog started .....")
        old_io_count = get_process_io_count("rsync")
        logger.info(f"Watchdog awake -> rsync write io {old_io_count[0]} rsync read io {old_io_count[1]}")
        time.sleep(seconds)  # watchdog interval
        new_io_count = get_process_io_count("rsync")
        logger.info(f"Watchdog awake -> rsync write io {new_io_count[0]} rsync read io {new_io_count[1]}")
        delta = tuple(new - old for old, new in zip(old_io_count, new_io_count))
        logger.info(f"watchdog io delta calculation {delta}")
        if delta[0] == 0 or delta[1] == 0:
            logger.error(f"rsync IDLE for {seconds} seconds -> sending kill signal ")
            kill_rsync()
            dispatch_failure_alert_by_email("rsync killed , check log for details")
            break


if __name__ == '__main__':
    logger.info("Pre backup checks ....started")
    is_destination_valid(LOG_FOLDER_PATH)
    is_enough_free_space(LOG_FOLDER_PATH, 4)
    is_user_permitted(LOG_FOLDER_PATH)
    is_rsync_present()
    is_rsync_not_running()
    if_backup_exists("backup_" + str(datetime.now().strftime("%d-%m-%Y")))
    logger.info("Pre backup checks ....completed")

    # asynchronous execution in separate thread
    rsync_thread = threading.Thread(target=run_rsync)
    rsync_thread.start()

    # watchdog execution in separate thread
    watchdog_thread = threading.Thread(target=run_watchdog(3))
    watchdog_thread.start()

    logger.info("rsync completed... ")

    filecmp.dircmp('/home/iidwuurliik/Desktop/py_dev',
                   "/tmp/" + "backup_" + str(datetime.now().strftime("%d-%m-%Y"))).report_full_closure()

    # TODO ask question in case we have large files md5 hash calculation might be appropriate ,
    # for large number of small files inefficient

    logger.info("BACKUP_completed")
