'''
esper app usage

usage: esper_group_actions [-h]
                            -c  {uninstall, whitelist, brightness, alarm_volume, ring_volume, music_volume, notification_volume, bluetooth, wifi, gps, ping, reboot}
                            -g  GROUP_ID
                            -v  VALUE

example:

./esper_group_actions -g 52ecfb3c-d1ad-4e66-8cf9-85daff8d7f3c -c ring_volume -v 50
./esper_group_actions -g 52ecfb3c-d1ad-4e66-8cf9-85daff8d7f3c -c ping

Runs on all active devices in a group. API key is required.
'''

import sys
import requests
import esperclient
import time
from esperclient.rest import ApiException

import argparse
active_device_list = []
inactive_device_list = []

#### TYRELL CORP CONFIG #######

configuration = esperclient.Configuration()
configuration.host = 'https://tyrellcorp-api.shoonyacloud.com/api'
configuration.api_key['Authorization'] = 'RaCh1Ty3L181AdE4uN32e593rD3ck36'
configuration.api_key_prefix['Authorization'] = 'Bearer'
enterprise_id = '5da4cf47-398c-4cea-82be-2796a3f23c3c'

###############################

def run_whitelist_command(device, package_name):
    api_instance = esperclient.CommandsApi(esperclient.ApiClient(configuration))
    command_args = esperclient.CommandArgs(package_name=package_name)
    command = esperclient.CommandRequest(command='ADD_TO_WHITELIST', command_args=command_args)
    try:
        api_response = api_instance.run_command(enterprise_id, device.id, command)

        if api_response.id is not None:
            print('Whitelist command fired successfully on ' +  device.device_name + ' for ' + package_name)
    except ApiException as e:
        print("Exception when calling CommandsApi->run_command: %s\n" % e)

def get_whitelist_api_url(device_id):
    return configuration.host + '/enterprise/' + enterprise_id + '/device/' + device_id + '/app/'

def is_package_whitelisted(device_id, package_name):
    url = get_whitelist_api_url(device_id)
    querystring = {"package_name": package_name, "whitelisted":"false"}
    payload = ""
    headers = {
        'Authorization': "Bearer " + configuration.api_key['Authorization'],
        'cache-control': "no-cache",
        }

    response = requests.request("GET", url, data=payload, headers=headers, params=querystring)    
    print("Whitelist query match: " + str(response.json().get('count')))
    return False if response.json().get('count') == 1 else True


def whitelist_package_in_group_devices(device_list, package_name):
    # Fetch all devices in group

    # None check
    print("Currently active devices in group: ")
    print([device.device_name for device in device_list])

    for device in device_list:
        if not is_package_whitelisted(device.id, package_name):
            try:
                run_whitelist_command(device, package_name)
            except Exception as e:
                print('Could not fire command on ' + device.device_name + ": " + str(e))
            time.sleep(1)
        else:
            print('Warning: Package already whitelisted or not present on device: ' + device.device_name)


# ====== UNINSTALL FROM GROUP ==========            


def run_uninstall_command(device, package_name, app_id):
    api_instance = esperclient.CommandsApi(esperclient.ApiClient(configuration))
    command_args = esperclient.CommandArgs(package_name=package_name, app_version = app_id)
    command = esperclient.CommandRequest(command='UNINSTALL', command_args=command_args)
    #print(command)
    try:
        api_response = api_instance.run_command(enterprise_id, device.id, command)
        if api_response.id is not None:
            print('Uninstall command fired successfully on ' +  device.device_name + ' for ' + package_name)
    except ApiException as e:
        print("Exception when calling CommandsApi->run_command: %s\n" % e)


def uninstall_package_in_group_devices(device_list, package_name):
    # Fetch all devices in group

    print("Currently active devices in group: ")
    print([device.device_name for device in device_list])

    for device in device_list:
        app_id = is_package_installed(device.id, package_name)
        if app_id:
            try:
                run_uninstall_command(device, package_name, app_id)
            except Exception as e:
                print('Could not fire command on ' + device.device_name + ": " + str(e))
            time.sleep(1)
        else:
            print('Warning: Package already uninstalled or not present on device: ' + device.device_name)

def is_package_installed(device_id, package_name):
    querystring = {"package_name": package_name, "whitelisted":"false"}
    payload = ""
    headers = {
        'Authorization': "Bearer " + configuration.api_key['Authorization'],
        'cache-control': "no-cache",
        }

    api_instance = esperclient.DeviceApi(esperclient.ApiClient(configuration))
    response = api_instance.get_app_installs(enterprise_id, device_id, package_name=package_name)
    #print(response)
    if response and response.count > 0:
        app_id = response.results[0].application.version.app_version_id
        if app_id:
          return response.results[0].application.version.app_version_id
        else:
            return 0
    else:
        #print("App doesn't exist")
        return 0


# ====== Get All the devices in a group ========

def get_devices_in_group(group_id):
    # create an instance of the API class

    api_instance = esperclient.DeviceApi(esperclient.ApiClient(configuration))
    limit = 5000 # int | Number of results to return per page. (optional) (default to 20)
    offset = 0 # int | The initial index from which to return the results. (optional) (default to 0)

    try:
        api_response = api_instance.get_all_devices(enterprise_id, group=group_id, limit=limit, offset=offset)
        #print(api_response)
        active_device_list = []
        # None check
        if len(api_response.results) > 0:
            for device in api_response.results:
                if device.status == 1:  # Check for active devices only
                    active_device_list.append(device)
                else:
                    inactive_device_list.append(device)
    except ApiException as e:
        print("Exception when calling DeviceApi->get_all_devices: %s\n" % e)

    return active_device_list

def get_group_id_by_name(name):
    api_instance = esperclient.DeviceApi(esperclient.ApiClient(configuration))

def change_settings(command, value, group_id):
    device_list = get_devices_in_group(group_id)
    if command == "whitelist":
        whitelist_package_in_group_devices(device_list, value)
    elif command == "uninstall":    
        uninstall_package_in_group_devices(device_list, value)
    else:
        # for all other device commands
        change_device_settings(command, value, device_list)

'''
STREAM_RING(0),
STREAM_NOTIFICATION(1);
STREAM_ALARM(2),
STREAM_MUSIC(3)
'''
def change_device_settings(command, value, device_list):

    if command == "brightness":
        for device in device_list:
            api_instance = esperclient.CommandsApi(esperclient.ApiClient(configuration))
            if int(value) > 100 or int(value) < 0:
                print("Brightness value has to be in between 0-100")
                sys.exit(1)

            command_args = esperclient.CommandArgs(brightness_value=int(value))
            command = esperclient.CommandRequest(command='SET_BRIGHTNESS_SCALE', command_args=command_args)
            # print(command)
            try:
                api_response = api_instance.run_command(enterprise_id, device.id, command)
                if api_response.id is not None:
                    print('brightness command fired successfully on ' + device.device_name)
            except ApiException as e:
                print("Exception when calling CommandsApi->run_command: %s\n" % e)

    elif command == "alarm_volume":
        for device in device_list:
            api_instance = esperclient.CommandsApi(esperclient.ApiClient(configuration))
            if int(value) > 100 or int(value) < 0:
                print("Alarm volume value has to be in between 0-100")
                sys.exit(1)

            command_args = esperclient.CommandArgs(volume_level=int(value), stream=int(2))
            command = esperclient.CommandRequest(command='SET_STREAM_VOLUME', command_args=command_args)
            # print(command)
            try:
                api_response = api_instance.run_command(enterprise_id, device.id, command)
                if api_response.id is not None:
                    print('alarm volume change command fired successfully on ' + device.device_name)
            except ApiException as e:
                print("Exception when calling CommandsApi->run_command: %s\n" % e)

    elif command == "ring_volume":
        for device in device_list:
            api_instance = esperclient.CommandsApi(esperclient.ApiClient(configuration))
            if int(value) > 100 or int(value) < 0:
                print("Ring volume value has to be in between 0-100")
                sys.exit(1)

            command_args = esperclient.CommandArgs(volume_level=int(value), stream=int(0))
            command = esperclient.CommandRequest(command='SET_STREAM_VOLUME', command_args=command_args)
            # print(command)
            try:
                api_response = api_instance.run_command(enterprise_id, device.id, command)
                if api_response.id is not None:
                    print('Ring volume change command fired successfully on ' + device.device_name)
            except ApiException as e:
                print("Exception when calling CommandsApi->run_command: %s\n" % e)


    elif command == "notification_volume":
        for device in device_list:
            api_instance = esperclient.CommandsApi(esperclient.ApiClient(configuration))
            if int(value) > 100 or int(value) < 0:
                print("Notification volume value has to be in between 0-100")
                sys.exit(1)

            command_args = esperclient.CommandArgs(volume_level=int(value), stream=int(1))
            command = esperclient.CommandRequest(command='SET_STREAM_VOLUME', command_args=command_args)
            # print(command)
            try:
                api_response = api_instance.run_command(enterprise_id, device.id, command)
                if api_response.id is not None:
                    print('Notification volume change command fired successfully on ' + device.device_name)
            except ApiException as e:
                print("Exception when calling CommandsApi->run_command: %s\n" % e)

    elif command == "music_volume":
        for device in device_list:
            api_instance = esperclient.CommandsApi(esperclient.ApiClient(configuration))
            if int(value) > 100 or int(value) < 0:
                print("Music volume value has to be in between 0-100")
                sys.exit(1)

            command_args = esperclient.CommandArgs(volume_level=int(value), stream=int(3))
            command = esperclient.CommandRequest(command='SET_STREAM_VOLUME', command_args=command_args)
            # print(command)
            try:
                api_response = api_instance.run_command(enterprise_id, device.id, command)
                if api_response.id is not None:
                    print('Music volume change command fired successfully on ' + device.device_name)
            except ApiException as e:
                print("Exception when calling CommandsApi->run_command: %s\n" % e)

    elif command == "bluetooth":
        for device in device_list:
            api_instance = esperclient.CommandsApi(esperclient.ApiClient(configuration))
            command_args = esperclient.CommandArgs(bluetooth_state= value)
            command = esperclient.CommandRequest(command='SET_BLUETOOTH_STATE', command_args=command_args)
            # print(command)
            try:
                api_response = api_instance.run_command(enterprise_id, device.id, command)
                if api_response.id is not None:
                    print('Bluetooth change command fired successfully on ' + device.device_name)
            except ApiException as e:
                print("Exception when calling CommandsApi->run_command: %s\n" % e)

    elif command == "wifi":
        for device in device_list:
            api_instance = esperclient.CommandsApi(esperclient.ApiClient(configuration))
            command_args = esperclient.CommandArgs(wifi_state= value)
            command = esperclient.CommandRequest(command='SET_WIFI_STATE', command_args=command_args)
            # print(command)
            try:
                api_response = api_instance.run_command(enterprise_id, device.id, command)
                if api_response.id is not None:
                    print('Wifi change command fired successfully on ' + device.device_name)
            except ApiException as e:
                print("Exception when calling CommandsApi->run_command: %s\n" % e)

    elif command == "gps":
        '''
        LOCATION_MODE_OFF(0),
        LOCATION_MODE_SENSORS_ONLY(1),
        LOCATION_MODE_BATTERY_SAVING(2),
        LOCATION_MODE_HIGH_ACCURACY(3);
        '''
        for device in device_list:
            if value == "off":
                state = 0
            elif value == "sensors_only":
                state = 1
            elif value == "battery_saving":
                state = 2
            elif value == "high":
                state = 3
            else:
                print("Invalid GPS state: Valid states are: off, high, sensors_only and battery_saving")
                sys.exit(1)

            api_instance = esperclient.CommandsApi(esperclient.ApiClient(configuration))
            command_args = esperclient.CommandArgs(gps_state = int(state))
            command = esperclient.CommandRequest(command='SET_GPS_STATE', command_args=command_args)
            # print(command)
            try:
                api_response = api_instance.run_command(enterprise_id, device.id, command)
                if api_response.id is not None:
                    #print(api_response)
                    print('GPS change command fired successfully on ' + device.device_name)
            except ApiException as e:
                print("Exception when calling CommandsApi->run_command: %s\n" % e)

    elif command == "ping":
        for device in device_list:
            api_instance = esperclient.CommandsApi(esperclient.ApiClient(configuration))
            command_args = esperclient.CommandArgs()
            command = esperclient.CommandRequest(command='UPDATE_HEARTBEAT', command_args=command_args)
            # print(command)
            try:
                api_response = api_instance.run_command(enterprise_id, device.id, command)
                if api_response.id is not None:
                    #print(api_response)
                    print('UPDATE_HEARTBEAT command fired successfully on ' + device.device_name)
            except ApiException as e:
                print("Exception when calling CommandsApi->run_command: %s\n" % e)

    elif command == "reboot":
        for device in device_list:
            api_instance = esperclient.CommandsApi(esperclient.ApiClient(configuration))
            command_args = esperclient.CommandArgs()
            command = esperclient.CommandRequest(command='REBOOT', command_args=command_args)
            # print(command)
            try:
                api_response = api_instance.run_command(enterprise_id, device.id, command)
                if api_response.id is not None:
                    #print(api_response)
                    print('Reboot command fired successfully on ' + device.device_name)
            except ApiException as e:
                print("Exception when calling CommandsApi->run_command: %s\n" % e)


# ====== Main Function ========
 

def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-c', '--command', '--name',
        dest='command',
        required=True,
        choices=['uninstall', 'whitelist', 'brightness', 'alarm_volume', 'ring_volume', 'music_volume', 'notification_volume', 'bluetooth', 'wifi', 'gps', 'ping', 'reboot'],
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
        #required=True,
        help="value"
    )

    args = parser.parse_args()

    #print(args.command)
    #print(args.group_id)
    #print(args.value)

    # make sure if command is given, value should also be provided
    if args.command and (args.value is None) and args.command != "ping":
        print("\nValue has to be provided along with command with -v option.\n")
        parser.print_help()
        sys.exit(1)
    if args.value and (args.command is None):
        print("Please pass the command as well along with value")
        sys.exit(1)

    change_settings(args.command, args.value, args.group_id)


if __name__ == "__main__":
    main(sys.argv[1:])
