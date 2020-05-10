
from __future__ import print_function
import sys
import time
import argparse
import requests
import esperclient
from esperclient.rest import ApiException
import datetime

#### Enterprise Configuration #######

# Please fill the varibales under <>
CONFIGURATION = esperclient.Configuration()
CONFIGURATION.host = 'https://demo-api.shoonyacloud.com/api'
CONFIGURATION.api_key['Authorization'] = 'WkprtBXbwFhMVWbIqRtIE1ew2xnotf'
CONFIGURATION.api_key_prefix['Authorization'] = 'Bearer'
ENTERPRISE_ID = '2c9ad94f-8cdd-4749-9024-fcaa6008ed36'

# int | Number of results to return per page. (optional) (default to 20)
CONFIGURATION.per_page_limit = 5000
# int | The initial index from which to return the results.(optional) default to 0)
CONFIGURATION.per_page_offset = 0


# returns difference in time in seconds between two dates
def get_time_diff(dt2, dt1):
  #print("new: ", dt2)
  #print("old: ", dt1)
  timedelta = dt2 - dt1
  return (timedelta.days * 24 * 3600 + timedelta.seconds)


# print device downtime for each day in minutes
# consider device downtime only if cloud doesn't receive status event in 3 minutes.
# check back again for next event in every 2 minute
def get_device_downtime(device_id):
    last_status_event_time = ""
    downtime = 0
    api_instance = esperclient.DeviceApi(esperclient.ApiClient(CONFIGURATION))
    try:
        while (1):
            api_response = api_instance.get_device_event(ENTERPRISE_ID,device_id=device_id, latest_event=1)
            if len(api_response.results):
                for event in api_response.results:
                    latest_status_event_time = event.created_on
                    # initialize last status to current if just started
                    if (last_status_event_time == ""):
                        last_status_event_time = latest_status_event_time
                        # new days has started, reset the downtime for this day and print
                    if (last_status_event_time.date() != latest_status_event_time.date()):
                        print("Downtime for: ", last_status_event_time.date(), " is: ", (downtime/60) ," minutes")
                        downtime = 0
                        # reset the latest_status_event_time and last_status_event_time to same and start again
                        last_status_event_time = latest_status_event_time
                    # consider device downtime if it has not received status in 3 minutes
                    time_diff = (get_time_diff(latest_status_event_time, last_status_event_time))
                    if time_diff > 180 :
                        downtime = (downtime) + time_diff
                    last_status_event_time = latest_status_event_time
            print("downtime so far for", latest_status_event_time.date(), "is:", str(downtime/60), "minutes")
            # check back again for next status event in 60 seconds
            time.sleep(120)

    except ApiException as api_exception:
        print("Exception when calling DeviceApi->get_device_event: %s\n" % api_exception)


"""
Main Function
"""
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-c', '--command', '--name',
        dest='command',
        #required=True,
        choices=['uninstall', 'install', 'whitelist', 'brightness', 'alarm_volume', 'ring_volume',
                 'music_volume', 'notification_volume', 'bluetooth', 'wifi', 'gps', 'ping',
                 'reboot'],
        help="Esper Management App Release Channel."
    )

    parser.add_argument(
        '-g', '--group-id',
        dest='group_id',
        #required=True,
        help="get group id"
    )

    parser.add_argument(
        '-d', '--device_id',
        dest='device_id',
        required=True,
        help="get device id"
    )

    parser.add_argument(
        '-v', '--value',
        dest='value',
        help="value"
    )

    parser.add_argument(
        '-version', '--version',
        dest='version',
        help="version"
    )

    args = parser.parse_args()

    # make sure if command is given, value should also be provided
    if args.command and (args.value is None):
        if (not (args.command in ["ping", "reboot"])):
            print("\nValue has to be provided along with command with -v option.\n")
            parser.print_help()
            sys.exit(1)
    if args.value and (args.command is None):
        print("Please pass the command as well along with value")
        sys.exit(1)


    get_device_downtime(args.device_id)


if __name__ == "__main__":
    main()
