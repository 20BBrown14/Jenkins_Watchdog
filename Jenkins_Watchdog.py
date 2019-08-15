# Jenkins Watchdog
# python 3.6

import sys
from platform import python_version

#Check Python version. Must be atleast 3.6
if sys.version_info < (3,6,0):
  raise Exception("Trying to use Python %s. Must be using at least Python 3.6" % python_version())


# Library imports
import datetime
import json
import logging
import os
import pause
import re
import time
from requests import get, ConnectionError, HTTPError
from platform import system
from dateutil import parser
from copy import deepcopy
from plyer import notification

# Local imports
import Jenkins_Watchdog_Constants as constants

# Global vars
global REPOS_TO_TRACK # Repos to track from the config file
global TRACKED_INFORMATION # Currently tracked information from jenkins calls
global LOGGER # The logger being used
global START_WATCH # Time to start watchdog
global END_WATCH # Time to stop watchdog
global SHOULD_PAUSE # Should the watching be paused?

# Returns a string with formatted time 'dd/mm/yyyy HH:MM:SS'
def get_formatted_time():
  formattedTime = time.strftime("%d/%m/%Y %H:%M:%S")
  return formattedTime

def log_information(message):
  LOGGER.info("%s - %s" % (get_formatted_time(), message))

# Prints the given message and current time to the console with a level
# Logs the given message and current time to the log file with the given level
def print_and_log(message, loggerLevel):
  print("%s:%s - %s" % (loggerLevel.upper(), get_formatted_time(), message))
  if(loggerLevel.lower() == 'info'):
    LOGGER.info("%s - %s" % (get_formatted_time(), message))
  elif(loggerLevel.lower() == 'error'):
    LOGGER.error("%s - %s" % (get_formatted_time(), message))

# Checks that the config file exists and reads the config if it does
def setup_config():
  # todo: check for update
  global LOGGER
  global REPOS_TO_TRACK
  global START_WATCH
  global END_WATCH
  global SHOULD_PAUSE
  if(os.path.isfile(constants.CONFIG_FILE)):
    with open(constants.CONFIG_FILE) as config_file:
      data = json.load(config_file)
      try:
        logging.basicConfig(filename=data['logFileName'], level=logging.INFO)
        LOGGER = logging.getLogger('Jenkins_Watchdog')
        REPOS_TO_TRACK = data['trackedRepos']
        START_WATCH = data['watchConfig']['startWatch']
        START_WATCH = parser.parse(START_WATCH).time()
        SHOULD_PAUSE = data['watchConfig']['useWatchShift'] 
        if(SHOULD_PAUSE):
          END_WATCH = data['watchConfig']['endWatch']
          END_WATCH = parser.parse(END_WATCH).time()
      except ValueError as e:
        print("%s - %s: %s" % (get_formatted_time, 'ERROR', e))
        print_and_log(constants.EXIT_MESSAGE, 'INFO')
        exit(1)
  else:
    print("%s - %s: %s" % (get_formatted_time, 'ERROR', constants.CONFIG_FILE_DNE))
    print_and_log(constants.EXIT_MESSAGE, 'INFO')
    exit(1)

def setup_jobs():
  global REPOS_TO_TRACK
  global TRACKED_INFORMATION
  if(len(REPOS_TO_TRACK) > 0):
    TRACKED_INFORMATION = json.loads('{}')
    for repo_dict in REPOS_TO_TRACK:
      if(repo_dict['tracked']):
        repo_name = repo_dict['name']
        repo_url = repo_dict['url']
        if(not re.match("^(?:http(s)?:\/\/)?[\w.-]+(?:\.[\w\.-]+)+[\w\-\._~:/?#[\]@!\$&'\(\)\*\+\%,;=.]+$", repo_url)):
          REPOS_TO_TRACK.remove(repo_dict)
          print_and_log(constants.INVALID_REPO_URL.format(repo_url=repo_url), 'ERROR')
        if(not re.match("(\/{1,}api\/{1,}json\/{0,})$", repo_url)):
          repo_url = repo_url + '/api/json/'
        try:
          get_response = get(repo_url)
          jenkins_info = json.loads(get_response.text.encode('utf-8').strip())
        except HTTPError as e:
          print_and_log(constants.HTTP_ERROR_MESSAGE.format(http_error=e.response.status_code, repo_url=repo_url), 'ERROR')
          print_and_log(e, 'ERROR')
          continue
        except ConnectionError as e:
          print_and_log(constants.CONNECT_ERROR_MESSAGE.format(repo_url=repo_url), 'ERROR')
          print_and_log(e, 'ERROR')
          continue
        except ValueError as e:
          print_and_log(constants.VALUE_ERROR_MESSAGE.format(repo_url=repo_url), 'ERROR')
          print_and_log(e, 'ERROR')
          continue
        TRACKED_INFORMATION[repo_name] = json.loads('{}')
        TRACKED_INFORMATION[repo_name]['watched_jobs'] = json.loads('{}')
        for job in jenkins_info['jobs']:
          job_name = job['name']
          TRACKED_INFORMATION[repo_name]['watched_jobs'][job_name] = job
        TRACKED_INFORMATION[repo_name]['repo_url'] = jenkins_info['url']
      else:
        REPOS_TO_TRACK.remove(repo_dict)
  else:
    print_and_log(constants.NO_REPOS_CONFIG, 'ERROR')
    print_and_log(constants.EXIT_MESSAGE, 'INFO')
    exit(1)
  if(len(TRACKED_INFORMATION) <= 0):
    print_and_log(constants.NO_TRACKABLE_REPOS_ERROR_MESSAGE, 'ERROR')
    print_and_log(constants.EXIT_MESSAGE, 'INFO')
    exit(1)
  
def watch_jenkins():
  global TRACKED_INFORMATION
  global IS_JOB_BUILDING
  while 1:
    current_time = datetime.datetime.now().time()
    if(SHOULD_PAUSE and (not current_time >= START_WATCH or not current_time <= END_WATCH)):
      print_and_log(constants.PAUSING_WATCHDOG_MESSAGE.format(resume_time=str(START_WATCH)), 'INFO')
      pause.minutes(60)
      continue

    iteration_start_time = time.time()
    old_tracked_information = deepcopy(TRACKED_INFORMATION)
    
    notification_string = ''
    notification_type = ''
    jobs_added_count = 0
    jobs_deleted_count = 0
    jobs_status_change_count = 0

    is_job_building = False

    for repo_name, repo_jobs in TRACKED_INFORMATION.items():
      try:
        repo_url = '%s/api/json/' % TRACKED_INFORMATION[repo_name]['repo_url']
        get_response = get(repo_url)
        jenkins_info = json.loads(get_response.text.encode('utf-8').strip())
        for job in jenkins_info['jobs']:
          job_name = job['name']
          TRACKED_INFORMATION[repo_name]['watched_jobs'][job_name] = job
      except ConnectionError as e:
        print_and_log(constants.CONNECT_ERROR_MESSAGE.format(repo_url=repo_url), 'ERROR')
        print_and_log(e, 'ERROR')
        continue
      except ValueError as e:
        print_and_log(constants.VALUE_ERROR_MESSAGE.format(repo_url=repo_url), 'ERROR')
        print_and_log(e, 'ERROR')
        continue
      current_repo_jobs = TRACKED_INFORMATION[repo_name]['watched_jobs']
      old_repo_jobs = old_tracked_information[repo_name]['watched_jobs']
      for old_repo_job_name, old_repo_job_information in old_repo_jobs.items():
        full_job_name = repo_name + '/' + old_repo_job_name
        if(not old_repo_job_name in current_repo_jobs):
          #Job was deleted from repo
          if(not notification_type == constants.STATUS_NOTIF_TYPE and not notification_type == constants.ADD_NOTIF_TYPE):
            notification_type = constants.DELETE_NOTIF_TYPE # Delete notification has lowest priority
            if(not notification_string and not jobs_deleted_count):
              notification_string = constants.JOB_WAS_DELETED.format(job_name=full_job_name)
          jobs_deleted_count += 1
          log_information(constants.JOB_WAS_DELETED.format(job_name=full_job_name))

      for job_name, job_information in current_repo_jobs.items():
        full_job_name = repo_name + '/' + job_name
        current_job_name = job_information['name']
        current_job_color = job_information['color']
        current_job_url = job_information['url']
        current_repo = TRACKED_INFORMATION
        if('anime' in current_job_color):
          is_job_building = True
        if(not current_job_name in old_repo_jobs):
          # Job was added to repo
          if(not notification_type == constants.STATUS_NOTIF_TYPE):
            notification_type = constants.ADD_NOTIF_TYPE # Add has second highest priority
            if(not notification_string and not jobs_added_count):
              notification_string = constants.JOB_WAS_ADDED.format(job_name=full_job_name)
          jobs_added_count += 1
          log_information(constants.JOB_WAS_ADDED.format(job_name=full_job_name))
        elif(current_job_color != old_repo_jobs[job_name]['color']):
          # Job changed status
          notification_type = constants.STATUS_NOTIF_TYPE # Status has highest priority
          if(not notification_string and not jobs_status_change_count):
            notification_string = constants.JOB_CHANGED_STATUS.format(job_name=full_job_name, old_status=old_repo_jobs[job_name]['color'], new_status=current_job_color)
          jobs_status_change_count += 1
          log_information(constants.JOB_CHANGED_STATUS.format(job_name=full_job_name, old_status=old_repo_jobs[job_name]['color'], new_status=current_job_color))


    if(notification_type ):
      if(not notification_string and notification_type == constants.DELETE_NOTIF_TYPE):
        notification_string = constants.MULTIPLE_DELETES.format(count=jobs_deleted_count)
      elif(not notification_string and notification_type == constants.ADD_NOTIF_TYPE):
        notification_string = constants.MULTIPLE_ADDITIONS.format(count=jobs_added_count)
      elif(not notification_string and notification_type == constants.STATUS_NOTIF_TYPE):
        notification_string = constants.MULTIPLE_STATUS_CHANGES.format(count=jobs_status_change_count)
      notification.notify(title='Jenkins Watchdog', message=notification_string, app_icon=None, timeout=10)
    # stopped_time = datetime.datetime.now().time()
    if not is_job_building:
      print('INFO:%s - No jobs building. Sleeping for 5 minutes.' % get_formatted_time())
      pause.minutes(5)
    else:
      print('INFO:%s - Jobs are building. Sleeping for 1 minute.' % get_formatted_time() )
      pause.minutes(1)
        
def main():
  setup_config()
  print_and_log("PID = %d" % os.getpid(), 'INFO')
  setup_jobs()
  watch_jenkins()


if __name__ == "__main__":
  main()

