# Sample code to use managed configuration APIs of Esper.
# This code run the APIs on the chrome browser and help in
# 1. Place specific URLs on an allowlist
# 2. Place specific URLs on a blocklist
# 3. Disable browser incognito mode on Android
# 4. Enable forced Safe Search on a device

# Code can be run either on set of devices or set of groups
# provided as a argument to the command request


import esperclient
from esperclient.rest import ApiException
from esperclient.models.v0_command_args import V0CommandArgs as CommandArgs

# Configure API key authorization: apiKey
configuration = esperclient.Configuration()
configuration.host = 'https://<endpoint-name>-api.esper.cloud/api'
configuration.api_key['Authorization'] = '<API-Key>'
configuration.api_key_prefix['Authorization'] = 'Bearer'

# create an instance of the API class
api_instance = esperclient.CommandsV2Api(esperclient.ApiClient(configuration))
enterprise_id = '<Enterprise ID>' # str | ID of the enterprise

# Modify this Python Dict to set your own managed configurations
command_args = CommandArgs(
    custom_settings_config={
        "managedAppConfigurations": {
            "com.android.chrome": {
                "URLBlacklist": ["https://www.omegle.com/","Facebook.com","instagram.com"], # not allow these websites to work
                "URLWhitelist": ["*"], # rest all allowed to open
                "IncognitoModeAvailability": "1",   # disable incognito mode
                "ForceGoogleSafeSearch" : "true",   # enable safe search to work
                "HomepageLocation": "https://esper.io"  # set chrome home page
            }
        }
    }
)

# int | Number of results to return per page. (optional) (default to 20)
configuration.per_page_limit = 5000
# int | The initial index from which to return the results.(optional) default to 0)
configuration.per_page_offset = 0

allgroups = []

# get all the groups id present in the enterprise and stores in allgroups[]
def get_all_groups_in_enterprise():
    # create an instance of the API class
    api_instance = esperclient.DeviceGroupApi(esperclient.ApiClient(configuration))
    try:
        api_response = api_instance.get_all_groups(enterprise_id,
                                                    limit=configuration.per_page_limit,
                                                    offset=configuration.per_page_offset)
        if len(api_response.results):
            for group in api_response.results:
                # add all the devices in this group to global list of devices
                allgroups.append(group.id)
        print(allgroups)

    except ApiException as e:
        print("Exception when calling DeviceGroupApi->get_all_groups: %s\n" % e)

# V0CommandRequest | The request body to create a command for set of devices or groups
## command_type ->
##  * DEVICE: command request is meant for devices
##  * GROUP: command request is meant for groups
##  * DYNAMIC: command request is meant for dynamic set of devices i.e subset of devices from different groups or otherwise.
## Type of devices to run commands on
##  * active: Run commands on currently online devices
##  * inactive: Run commands on currently offline devices
##  * all: Run commands on all the devices. Commands will be queued for offline devices until they come back online.

# contains the group id of all the groups in the enterprise
def run_managed_configuration():

    request = esperclient.V0CommandRequest(
        enterprise=enterprise_id,
        command_type="GROUP",
        device_type="all",
        groups = allgroups,
        command="UPDATE_DEVICE_CONFIG",
        command_args=command_args
    )

    try:
        # Create a command request
        api_response = api_instance.create_command(enterprise_id, request)
        #print(api_response)

        request_id = api_response.id
        response = api_instance.get_command_request_status(enterprise_id, request_id)
        status = response.results[0]
        #print(status)

        while status.state not in ["Command Success", "Command Failure", "Command TimeOut", "Command Cancelled", "Command Queued"]:
            response = api_instance.get_command_request_status(enterprise_id, request_id)
            status = response.results[0]
            print(status)

    except ApiException as e:
        print("Exception when calling CommandsV2Api->create_command: %s\n" % e)


"""
Main Function
"""
def main():
    get_all_groups_in_enterprise()
    run_managed_configuration()

if __name__ == "__main__":
    main()

