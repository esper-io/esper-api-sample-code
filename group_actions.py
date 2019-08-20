"""
esper app usage

usage: esper_group_actions [-h]
        -c  {uninstall, install, whitelist, brightness, alarm_volume, ring_volume,
             music_volume, notification_volume, bluetooth, wifi, gps, ping, reboot}
        -g  GROUP_ID
        -v  VALUE

example:

./esper_group_actions -g 52ecfb3c-d1ad-4e66-8cf9-85daff8d7f3c -c ring_volume -v 50
./esper_group_actions -g 52ecfb3c-d1ad-4e66-8cf9-85daff8d7f3c -c ping
./esper_group_actions -g 52ecfb3c-d1ad-4e66-8cf9-85daff8d7f3c -c install -v io.esper.samplesdk -version "1.0"


Runs on all active devices in a group. API key is required.
"""
from __future__ import print_function
import sys
import time
import argparse
import requests
import esperclient
from esperclient.rest import ApiException


ACTIVE_DEVICE_LIST = []
INACTIVE_DEVICE_LIST = []


#### Enterprise Configuration #######

# Please fill the varibales under <>
CONFIGURATION = esperclient.Configuration()
CONFIGURATION.host = 'https://<endpoint-name>-api.shoonyacloud.com/api'
CONFIGURATION.api_key['Authorization'] = '<API-KEY>'
CONFIGURATION.api_key_prefix['Authorization'] = 'Bearer'
ENTERPRISE_ID = '<ENTERPRISE-ID>'

# int | Number of results to return per page. (optional) (default to 20)
CONFIGURATION.group_per_page_limit = 5000
# int | The initial index from which to return the results.(optional) default to 0)
CONFIGURATION.group_per_page_offset = 0

###############################

"""
Whitelist the package name on the device using API
"""
def run_whitelist_command(device, package_name):
    api_instance = esperclient.CommandsApi(esperclient.ApiClient(CONFIGURATION))
    command_args = esperclient.CommandArgs(package_name=package_name)
    command = esperclient.CommandRequest(command='ADD_TO_WHITELIST', command_args=command_args)
    try:
        api_response = api_instance.run_command(ENTERPRISE_ID, device.id, command)

        if api_response.id is not None:
            print('Whitelist command fired successfully on {} for {}'.
                  format(device.device_name, package_name))
    except ApiException as api_exception:
        print("Exception when calling CommandsApi->run_command: %s\n" % api_exception)

"""
returns the whitelist API URL
"""
def get_whitelist_api_url(device_id):
    return CONFIGURATION.host + '/enterprise/' + ENTERPRISE_ID +\
                                    '/device/' + device_id + '/app/'


"""
Check whether is package Already whitelisted on this device id or not
"""
def is_package_whitelisted(device_id, package_name):
    url = get_whitelist_api_url(device_id)
    querystring = {"package_name": package_name, "whitelisted":"false"}
    payload = ""
    headers = {
        'Authorization': "Bearer " + CONFIGURATION.api_key['Authorization'],
        'cache-control': "no-cache",
        }

    response = requests.request("GET", url, data=payload, headers=headers,\
                                                        params=querystring)
    print("Whitelist query match: " + str(response.json().get('count')))
    return False if response.json().get('count') == 1 else True

"""
Whitelist the package on entire group
"""
def whitelist_package_in_group_devices(package_name):
    print("Currently active devices in group: ")
    print([device.device_name for device in ACTIVE_DEVICE_LIST])

    for device in ACTIVE_DEVICE_LIST:
        if not is_package_whitelisted(device.id, package_name):
            try:
                run_whitelist_command(device, package_name)
            except Exception as exception:
                print('Could not fire command on {} : {}'.format(device.device_name, str(exception)))
            time.sleep(1)
        else:
            print('Warning: Package already whitelisted or not present on device: {}'
                .format(device.device_name))

# ====== INSTALL TO GROUP ==========


"""
Return application id of specific package name and version code stored 
in environemnt. Return None if not present.
"""
def get_app_id(package_name, version_code):
    try:
        app_api_instance = esperclient.ApplicationApi(esperclient.ApiClient(CONFIGURATION))
        response = app_api_instance.get_all_applications(ENTERPRISE_ID)
        i = 0 # loop over all the packages in system

        while (response is not None and i < response.count):
            # found the package already present in the environment
            if response.results[i] and response.results[i].package_name == package_name:
                version_len = (len(response.results[i].versions))

                # if version_code is none, then use the first version provided to install
                j = 0 # loop over all the versions of this app
                while (j < version_len and version_code is not None):
                    if response.results[i].versions is not None and \
                            response.results[i].versions[j].version_code == version_code:
                        # found the same version code to install, store the j value to use
                        # else use the first instance of App version given
                        break
                    else:
                        j = j+1

                if j == version_len:
                    # this means that specific version code is not found in the list, do nothing
                    # bail out from here
                    print("Version not found")
                    return None

                # Here will come if version found or no version is provided to install
                app_version_id = response.results[i].versions[j].id
                return app_version_id
            else:
                # check for next package in list
                i = i+1
    except Exception as exception:
        print("Exception when calling CommandsApi->run_command: %s\n" % exception)
    return None

"""
Run installation of app package name and specific app_version to device
"""
def run_install_command(device, package_name, app_version_id):

    api_instance = esperclient.CommandsApi(esperclient.ApiClient(CONFIGURATION))
    command_args = esperclient.CommandArgs(package_name=package_name, app_version=app_version_id)
    command = esperclient.CommandRequest(command='INSTALL', command_args=command_args)
    try:
        api_response = api_instance.run_command(ENTERPRISE_ID, device.id, command)
        if api_response.id is not None:
            print('Install command fired successfully on ' + device.device_name + \
                  ' for ' + package_name)
    except ApiException as api_exception:
        print("Exception when calling CommandsApi->run_command: %s\n" % api_exception)

"""
install package to entire group active devices
"""
def install_package_to_group_devices(package_name, version_code):
    # get app_id from version code
    app_id = get_app_id(package_name, version_code)
    if app_id is None:
        print("No Such App or App Version exist in Environment, Please upload it first and then install")
        return

    print("Install Currently active devices in group: ")
    print([device.device_name for device in ACTIVE_DEVICE_LIST])

    # install the app_id on all active devices
    for device in ACTIVE_DEVICE_LIST:
        run_install_command(device, package_name, app_id)

# ====== UNINSTALL FROM GROUP ==========

"""
Run uninstallation of app package name from device
"""
def run_uninstall_command(device, package_name, app_id):
    api_instance = esperclient.CommandsApi(esperclient.ApiClient(CONFIGURATION))
    command_args = esperclient.CommandArgs(package_name=package_name, app_version=app_id)
    command = esperclient.CommandRequest(command='UNINSTALL', command_args=command_args)
    try:
        api_response = api_instance.run_command(ENTERPRISE_ID, device.id, command)
        if api_response.id is not None:
            print('Uninstall command fired successfully on ' + device.device_name +\
                                                            ' for ' + package_name)
    except ApiException as api_exception:
        print("Exception when calling CommandsApi->run_command: %s\n" % api_exception)


"""
uninstall package from entire group
"""
def uninstall_package_in_group_devices(package_name):

    print("Currently active devices in group: ")
    print([device.device_name for device in ACTIVE_DEVICE_LIST])

    for device in ACTIVE_DEVICE_LIST:
        app_id = get_package_id(device.id, package_name)
        if app_id:
            try:
                run_uninstall_command(device, package_name, app_id)
            except Exception as exception:
                print('Could not fire command on {} : {}'.format(device.device_name, str(exception)))
            time.sleep(1)
        else:
            print('Warning: Package already uninstalled or not present on device: '\
                                                                + device.device_name)

"""
This function returns the package app id if installed else return null
"""
def get_package_id(device_id, package_name):
    api_instance = esperclient.DeviceApi(esperclient.ApiClient(CONFIGURATION))
    response = api_instance.get_app_installs(ENTERPRISE_ID, device_id, package_name=package_name)
    if response and response.count > 0:
        print("getting package id for package_name")
        app_id = response.results[0].application.version.app_version_id
        if app_id:
            return response.results[0].application.version.app_version_id
    return None

"""
Get All the devices in a group
"""
def get_devices_in_group(group_id):
    # create an instance of the API class
    api_instance = esperclient.DeviceApi(esperclient.ApiClient(CONFIGURATION))
    try:
        api_response = api_instance.get_all_devices(ENTERPRISE_ID, group=group_id,
                                                    limit=CONFIGURATION.group_per_page_limit,
                                                    offset=CONFIGURATION.group_per_page_offset)
        if len(api_response.results):
            for device in api_response.results:
                if device.status == 1:  # Check for active devices only
                    ACTIVE_DEVICE_LIST.append(device)
                else:
                    INACTIVE_DEVICE_LIST.append(device)
    except ApiException as api_exception:
        print("Exception when calling DeviceApi->get_all_devices: %s\n" % api_exception)

"""
parse command and value and call appropriate functions
"""
def parse_command(command, value, group_id, version_code):
    get_devices_in_group(group_id)
    if command == "whitelist":
        whitelist_package_in_group_devices(value)
    elif command == "uninstall":
        uninstall_package_in_group_devices(value)
    elif command == "install":
        install_package_to_group_devices(value, version_code)
    else:
        # for all other device commands
        change_device_settings(command, value)

"""
change device settings
"""
def change_device_settings(command, value):
    if command == "brightness":
        for device in ACTIVE_DEVICE_LIST:
            api_instance = esperclient.CommandsApi(esperclient.ApiClient(CONFIGURATION))
            if int(value) > 100 or int(value) < 0:
                print("Brightness value has to be in between 0-100")
                sys.exit(1)

            command_args = esperclient.CommandArgs(brightness_value=int(value))
            command = esperclient.CommandRequest(command='SET_BRIGHTNESS_SCALE',
                                                 command_args=command_args)
            try:
                api_response = api_instance.run_command(ENTERPRISE_ID, device.id, command)
                if api_response.id is not None:
                    print('brightness command fired successfully on ' + device.device_name)
            except ApiException as api_exception:
                print("Exception when calling CommandsApi->run_command: %s\n" % api_exception)

    elif command == "alarm_volume":
        for device in ACTIVE_DEVICE_LIST:
            api_instance = esperclient.CommandsApi(esperclient.ApiClient(CONFIGURATION))
            if int(value) > 100 or int(value) < 0:
                print("Alarm volume value has to be in between 0-100")
                sys.exit(1)

            command_args = esperclient.CommandArgs(volume_level=int(value), stream=int(2))
            command = esperclient.CommandRequest(command='SET_STREAM_VOLUME',
                                                 command_args=command_args)
            try:
                api_response = api_instance.run_command(ENTERPRISE_ID, device.id, command)
                if api_response.id is not None:
                    print('alarm volume change command fired successfully on ' + device.device_name)
            except ApiException as api_exception:
                print("Exception when calling CommandsApi->run_command: %s\n" % api_exception)

    elif command == "ring_volume":
        for device in ACTIVE_DEVICE_LIST:
            api_instance = esperclient.CommandsApi(esperclient.ApiClient(CONFIGURATION))
            if int(value) > 100 or int(value) < 0:
                print("Ring volume value has to be in between 0-100")
                sys.exit(1)

            command_args = esperclient.CommandArgs(volume_level=int(value), stream=int(0))
            command = esperclient.CommandRequest(command='SET_STREAM_VOLUME',
                                                 command_args=command_args)
            try:
                api_response = api_instance.run_command(ENTERPRISE_ID, device.id, command)
                if api_response.id is not None:
                    print('Ring volume change command fired successfully on ' + device.device_name)
            except ApiException as api_exception:
                print("Exception when calling CommandsApi->run_command: %s\n" % api_exception)


    elif command == "notification_volume":
        for device in ACTIVE_DEVICE_LIST:
            api_instance = esperclient.CommandsApi(esperclient.ApiClient(CONFIGURATION))
            if int(value) > 100 or int(value) < 0:
                print("Notification volume value has to be in between 0-100")
                sys.exit(1)

            command_args = esperclient.CommandArgs(volume_level=int(value), stream=int(1))
            command = esperclient.CommandRequest(command='SET_STREAM_VOLUME',
                                                 command_args=command_args)
            try:
                api_response = api_instance.run_command(ENTERPRISE_ID, device.id, command)
                if api_response.id is not None:
                    print('Notification volume change command fired successfully on '+
                          device.device_name)
            except ApiException as api_exception:
                print("Exception when calling CommandsApi->run_command: %s\n" % api_exception)

    elif command == "music_volume":
        for device in ACTIVE_DEVICE_LIST:
            api_instance = esperclient.CommandsApi(esperclient.ApiClient(CONFIGURATION))
            if int(value) > 100 or int(value) < 0:
                print("Music volume value has to be in between 0-100")
                sys.exit(1)

            command_args = esperclient.CommandArgs(volume_level=int(value), stream=int(3))
            command = esperclient.CommandRequest(command='SET_STREAM_VOLUME',
                                                 command_args=command_args)
            try:
                api_response = api_instance.run_command(ENTERPRISE_ID, device.id, command)
                if api_response.id is not None:
                    print('Music volume change command fired successfully on ' + device.device_name)
            except ApiException as api_exception:
                print("Exception when calling CommandsApi->run_command: %s\n" % api_exception)

    elif command == "bluetooth":
        for device in ACTIVE_DEVICE_LIST:
            api_instance = esperclient.CommandsApi(esperclient.ApiClient(CONFIGURATION))
            command_args = esperclient.CommandArgs(bluetooth_state=value)
            command = esperclient.CommandRequest(command='SET_BLUETOOTH_STATE',
                                                 command_args=command_args)
            # print(command)
            try:
                api_response = api_instance.run_command(ENTERPRISE_ID, device.id, command)
                if api_response.id is not None:
                    print('Bluetooth change command fired successfully on ' + device.device_name)
            except ApiException as api_exception:
                print("Exception when calling CommandsApi->run_command: %s\n" % api_exception)

    elif command == "wifi":
        for device in ACTIVE_DEVICE_LIST:
            api_instance = esperclient.CommandsApi(esperclient.ApiClient(CONFIGURATION))
            command_args = esperclient.CommandArgs(wifi_state=value)
            command = esperclient.CommandRequest(command='SET_WIFI_STATE',
                                                 command_args=command_args)
            try:
                api_response = api_instance.run_command(ENTERPRISE_ID, device.id, command)
                if api_response.id is not None:
                    print('Wifi change command fired successfully on ' + device.device_name)
            except ApiException as api_exception:
                print("Exception when calling CommandsApi->run_command: %s\n" % api_exception)

    elif command == "gps":
        for device in ACTIVE_DEVICE_LIST:
            if value == "off":
                state = 0
            elif value == "sensors_only":
                state = 1
            elif value == "battery_saving":
                state = 2
            elif value == "high":
                state = 3
            else:
                print("Invalid GPS state: Valid states are: off, high, sensors_only"
                      "and battery_saving")
                sys.exit(1)

            api_instance = esperclient.CommandsApi(esperclient.ApiClient(CONFIGURATION))
            command_args = esperclient.CommandArgs(gps_state=int(state))
            command = esperclient.CommandRequest(command='SET_GPS_STATE',
                                                 command_args=command_args)
            try:
                api_response = api_instance.run_command(ENTERPRISE_ID, device.id, command)
                if api_response.id is not None:
                    print('GPS change command fired successfully on ' + device.device_name)
            except ApiException as api_exception:
                print("Exception when calling CommandsApi->run_command: %s\n" % api_exception)

    elif command == "ping":
        for device in ACTIVE_DEVICE_LIST:
            api_instance = esperclient.CommandsApi(esperclient.ApiClient(CONFIGURATION))
            command_args = esperclient.CommandArgs()
            command = esperclient.CommandRequest(command='UPDATE_HEARTBEAT',
                                                 command_args=command_args)
            try:
                api_response = api_instance.run_command(ENTERPRISE_ID, device.id, command)
                if api_response.id is not None:
                    print('UPDATE_HEARTBEAT command fired successfully on ' + device.device_name)
            except ApiException as api_exception:
                print("Exception when calling CommandsApi->run_command: %s\n" % api_exception)

    elif command == "reboot":
        for device in ACTIVE_DEVICE_LIST:
            api_instance = esperclient.CommandsApi(esperclient.ApiClient(CONFIGURATION))
            command_args = esperclient.CommandArgs()
            command = esperclient.CommandRequest(command='REBOOT',
                                                 command_args=command_args)
            # print(command)
            try:
                api_response = api_instance.run_command(ENTERPRISE_ID, device.id, command)
                if api_response.id is not None:
                    print('Reboot command fired successfully on ' + device.device_name)
            except ApiException as api_exception:
                print("Exception when calling CommandsApi->run_command: %s\n" % api_exception)


"""
Main Function
"""
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-c', '--command', '--name',
        dest='command',
        required=True,
        choices=['uninstall', 'install', 'whitelist', 'brightness', 'alarm_volume', 'ring_volume',
                 'music_volume', 'notification_volume', 'bluetooth', 'wifi', 'gps', 'ping',
                 'reboot'],
        help="Esper Management App Release Channel."
    )

    parser.add_argument(
        '-g', '--group-id',
        dest='group_id',
        required=True,
        help="get group id"
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

    parse_command(args.command, args.value, args.group_id, args.version)


if __name__ == "__main__":
    main()
