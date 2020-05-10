"""
esper app usage

usage: esper_group_actions [-h]
        -c  {uninstall, install, whitelist, brightness, alarm_volume, ring_volume,
             music_volume, notification_volume, bluetooth, wifi, gps, ping, reboot}
        -g GROUP_ID (or "all" for all the devices in a all the groups)
        -v  VALUE

example:

./esper_group_actions -g 52ecfb3c-d1ad-4e66-8cf9-85daff8d7f3c -c ring_volume -v 50
./esper_group_actions -g 52ecfb3c-d1ad-4e66-8cf9-85daff8d7f3c -c ping
./esper_group_actions -g 52ecfb3c-d1ad-4e66-8cf9-85daff8d7f3c -c install -v io.esper.samplesdk -version "1.0"
./esper_group_actions -g all -c reboot
./esper_group_actions -g all -c ping

Runs on all active devices in a group. API key is required.
"""

from __future__ import print_function
import sys
import time
import argparse
import requests
import esperclient
from esperclient.rest import ApiException
import datetime


ACTIVE_DEVICE_LIST = []
INACTIVE_DEVICE_LIST = []




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



def get_time_diff(dt2, dt1):
  print("new: ", dt2)
  print("old: ", dt1)
  timedelta = dt2 - dt1
  return (timedelta.days * 24 * 3600 + timedelta.seconds)

"""
def get_uptime():
    # create an instance of the API class
    api_instance = esperclient.DeviceApi(esperclient.ApiClient(CONFIGURATION))
    try:
        api_response = api_instance.get_all_devices(ENTERPRISE_ID,
                                                    limit=CONFIGURATION.per_page_limit,
                                                    offset=CONFIGURATION.per_page_offset)
        if len(api_response.results):
            for device in api_response.results:
                if device.device_name == "ESP-DMO-2N7Z":
                    print(device.device_name)
                    get_device_uptime(device)
                    break

    except ApiException as api_exception:
        print("Exception when calling DeviceApi->get_all_devices: %s\n" % api_exception)

"""

def get_device_uptime(device_id):
    prev = ""
    downtime = 0
    api_instance = esperclient.DeviceApi(esperclient.ApiClient(CONFIGURATION))
    try:
        while (1):
            api_response = api_instance.get_device_event(ENTERPRISE_ID,device_id=device_id, latest_event=1)
            if len(api_response.results):
                for event in api_response.results:
                    new = event.created_on
                    if (prev == ""):
                        prev = new
                    # consider device downtime if it has not received status in 3 minutes
                    if (downtime > 180):
                        downtime = (downtime) + (get_time_diff(new, prev))
                    prev = new
            print("downtime: ", str(downtime))
            # check back again for next status event in 60 seconds
            time.sleep(60)


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


    get_device_uptime(args.device_id)


if __name__ == "__main__":
    main()
