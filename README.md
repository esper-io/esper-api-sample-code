# esper-api-sample-code
Code samples demonstrating use of Esper APIs

- esper-group-action:
  -- this script allows all the individual device commands to be
     fire on the specific group or all the device under enterprise.
  -- This will fetch all the active devices in a group or enterprise and initiate the
     command on the same.
     
  -- Supported commands:

     uninstall, whitelist, brightness, alarm_volume, ring_volume, music_volume, notification_volume, bluetooth, wifi, gps, ping, reboot
  
  -- Usage:

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


     
- managed-configuration-chrome:

  -- script demonstrates the use of the esper managed configuration APIs
     to block URLs on chrome, enable safe search and disable incognito mode.
  -- Same format can be used to allow managed configuration on other apps like
     gmail, outlook etc
     
   -- Usage:
    -- ./managed-configuration-chrome.py
 

Please edit the python file to update your Enterprise Related information
under CONFIGURATION: endpoint-name, API-KEY and ENTERPRISE-ID

```
CONFIGURATION.host = 'https://<endpoint-name>-api.shoonyacloud.com/api'
CONFIGURATION.api_key['Authorization'] = '<API-KEY>'
ENTERPRISE_ID = '<ENTERPRISE-ID>'
```
