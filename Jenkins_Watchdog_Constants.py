# Jenkins_Watchdog_Constants.py

# Files
CONFIG_FILE = 'Jenkins_Watchdog_Config.json'

# Progamatic constants
DELETE_NOTIF_TYPE = 'delete_notification_type'
ADD_NOTIF_TYPE = 'addition_notification_type'
STATUS_NOTIF_TYPE = 'status_notification_type'

# Info Messages
PAUSING_WATCHDOG_MESSAGE = 'Pausing watchdog until {resume_time}.'
JOB_WAS_DELETED = '{job_name} has been deleted.'
JOB_WAS_ADDED = '{job_name} job has been added.'
JOB_CHANGED_STATUS = '{job_name} changed status from {old_status} to {new_status}.'
MULTIPLE_DELETES = '{count} jobs were deleted.'
MULTIPLE_ADDITIONS = '{count} jobs were added.'
MULTIPLE_STATUS_CHANGES = '{count} jobs changed status.'
EXIT_MESSAGE = 'Exiting.'

# Error Messages
CONFIG_FILE_DNE = 'Config file, %s, does not exist in the working directory.' % CONFIG_FILE
NO_REPOS_CONFIG = 'Config file, %s, does not define any repos to track.' % CONFIG_FILE
INVALID_REPO_URL = 'Repo url, {repo_url}, is not valid. Removing from tracked repos.'
CONNECT_ERROR_MESSAGE = 'Unable to access {repo_url}. Ignoring for now, will try again later.'
VALUE_ERROR_MESSAGE = 'Unable to parse response from {repo_url}. Ignoring for now, will try again later.'
HTTP_ERROR_MESSAGE = 'Http Error: {http_error} from {repo_url}. Ignoring for now, will try again later.'
NO_TRACKABLE_REPOS_ERROR_MESSAGE = 'There are no trackable repos in the config file. Please recheck your repos and try again.'