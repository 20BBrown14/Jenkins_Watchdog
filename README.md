# Jenkins Watchdog

This is a Python script that runs and tracks changes in specified Jenkins repos. It keeps a log file of all changes with a time stamp as well as displays desktop notifications.

- [Setup](#Setup)
  - [Requirements](#Requirements)
  - [Config](#Config)
  - [Config File Options](#Config-File-Options)
  - [trackedRepos](#trackedRepos)
  - [watchConfig](#watchConfig)
- [Running](#Running)
- [Author](#Author)
- [Source](#Source)
- [Contributing](#Contributing)

## Setup
This section describes what is required to get the project running
### Requirements
This project requires at least [Python 3.6](https://www.python.org/downloads/release/python-365/).

This project includes a [requirements](requirements.txt) file. Before you'll be able to run the script you'll need to install the required dependencies with

`pip install -r requirements.txt` or `pip3 install -r requirements.txt`

### Config

Setting up the config file is required. A [template](Jenkins_Watchdog_Config_TEMPLATE.json) is provided. Renaming the file to `Jenkins_Watchdog_Config.json` is required.

#### Config File Options

| Option | Description | Required |
| ------ | ----------- | -------- |
| logFileName | String indicating the name of the log file the script will output to. | :white_check_mark: |
| [trackedRepos](#trackedRepos) | Array of repos to track. | :white_check_mark: |
| [watchConfig](#watchConfig) | Object with settings for when to pause watching. | :white_check_mark: |

#### trackedRepos
Array of repos to track. Each item in the array should be a JSON object with the following items:

| Value | Description | Required |
| ----- | ----------- | -------- |
| name | String for the repo display name. | :white_check_mark: |
| url | String for the url of the repo. | :white_check_mark: |
| tracked | Boolean dictating whether the repo should be tracked. | :white_check_mark:

#### watchConfig
Object with settings for when to pause watching. This is useful if your machine is not able to access your Jenkins instance regularly. Using this option will prevent your log fom being cluttered with 'Unable to access' error messages.

| Value | Description | Required |
| ----- | ----------- | -------- |
| startWatching | String representing a time, in 24hr format, to start watching. Time is in your machine's local time. Can be empty string. | :x: |
| endWatch | String representing a time, in 24hr format, to stop watching. Time is in your machine's local time. Can be empty string. | :x: |
| useWatchShift | Boolean representing if the watching of repos should paused and restarted at specific times. | :white_check_mark: |

## Running
To run the script you must have completed the [setup](#Setup) then run `python Jenkins_Watchdog.py` or `python3 Jenkins_Watchdog.py` 

The console and log will print the PID.

## Author
This script was created by Branden Brown.
[Github](https://github.com/20BBrown14)

## Source
Source code available on [Github](https://github.com/20BBrown14/Jenkins_Watchdog)

## Contributing
To contribute to this project please open an issue or PR on Github