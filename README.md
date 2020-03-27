# esper-api-sample-code
Sample Codes demonstrating use of Esper API's

- This python script allows all the individual device commands to be
  fire on the specific group or all the device under enterprise.
- This will fetch all the active devices in a group or enterprise and initiate the
  command on the same.

Please edit the python file to update your Enterprise Related information
under CONFIGURATION: endpoint-name, API-KEY and ENTERPRISE-ID

CONFIGURATION.host = 'https://<endpoint-name>-api.shoonyacloud.com/api'
CONFIGURATION.api_key['Authorization'] = '<API-KEY>'
ENTERPRISE_ID = '<ENTERPRISE-ID>'


- Supported commands:
  uninstall, whitelist, brightness, alarm_volume, ring_volume, music_volume, notification_volume, bluetooth, wifi, gps, ping, reboot
  
- Usage:
  esper_group_actions [-h]
   -c {uninstall, whitelist, brightness, alarm_volume, ring_volume, music_volume, notification_volume, bluetooth, wifi, gps, ping, reboot}
   -g GROUP_ID (or "all" for all the devices in a all the groups)
   -v VALUE
   
- Example:
  ./esper_group_actions -g 52ecfb3c-d1ad-4e66-8cf9-85daff8d7f3c -c ring_volume -v 50
  ./esper_group_actions -g 52ecfb3c-d1ad-4e66-8cf9-85daff8d7f3c -c ping
  ./esper_group_actions -g 52ecfb3c-d1ad-4e66-8cf9-85daff8d7f3c -c reboot
  ./esper_group_actions -g all -c reboot
  ./esper_group_actions -g all -c ping


  
