from datetime import datetime

"""
TODO add comments
why .py file ? 

"""
# LOG_FOLDER_PATH = "/home/iidwuurliik/Desktop/py_dev/oanda/logs/"
LOG_FOLDER_PATH = "C:/Users/Art3m15/IdeaProjects/oanda_interview/logs/"

BACKUP_DESTINATION = "/tmp/backup_" + str(datetime.now().strftime("%d-%m-%Y"))

BACKUP_SOURCE = {
    "/home/iidwuurliik/",
}

EXCLUDED_DIRECTORY_LIST = {
    "/home/iidwuurliik/.cache",
    "/home/iidwuurliik/.config"
}

EMAIL_ALERT_CONFIG = {
    "_email": "alert.dispatcher.6883674@gmail.com",
    # TODO replace with API key in REAL production env!
    "_password": "SecurePasswordsAsPlainText!1",  # BEST SECURITY PRACTICE EVER!
    "_send_to": "alert.dispatcher.6883674@gmail.com",
    "_subject": "Exception during backup execution !",
    "_message": "most recent log attached ",
    "_file_attachment_path": LOG_FOLDER_PATH + "backup_service.log"

}

LOG_CONF = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': "[%(levelname)4.8s %(asctime)s %(module)s:%(lineno)d] "
                      "%(message)s",
            'datefmt': "%Y-%m-%d+%H:%M:%S",
        },
    },
    'handlers': {

        # 'default': {
        #     'level': 'DEBUG',
        #     'class': 'logging.StreamHandler',
        #     'formatter': 'standard',
        #     'stream': 'sys.stderr',
        #
        # },
        # 'error': {
        #     'level': 'ERROR',
        #     'class': 'logging.',
        #     'formatter': 'standard',
        #     'stream': 'sys.stderr',
        #
        # },
        'rotating_to_file': {
            'level': 'DEBUG',
            'class': "logging.handlers.RotatingFileHandler",
            'formatter': 'standard',
            'filename': LOG_FOLDER_PATH + 'backup_service.log',
            'mode': 'a',
            "maxBytes": 0,
            "backupCount": 0,
        },
    },
    'loggers': {
        'backup_service': {
            # 'handlers': ['default', 'rotating_to_file'],
            'handlers': ['rotating_to_file'],
            'level': 'DEBUG',
            'propagate': True
        }
    }
}

# CHECKPOINT_FILE_FLAG = ""
# CHECKPOINT_FILE_LOCATION = ""
