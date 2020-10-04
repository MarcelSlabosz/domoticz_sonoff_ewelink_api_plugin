# domoticz_sonoff_ewelink_api_plugin
Domoticz plugin for Sonoff Original Soft eWeLink API

# Installation
* Plugin works with Domoticz stable v2020.2. If you face any bug please don't hesistate to report an issue.
* Make sure your Domoticz instance supports Domoticz Plugin System - see more https://www.domoticz.com/wiki/Using_Python_plugins

## Install dependencies
0. Check if Node.js is already installed, by executing command: `node -v`
    * If command print something similar to `v10.21.0` go to next point
    * If not, install it: https://nodejs.org/en/
0. Install eWeLink open source API module: https://ewelink-api.now.sh/docs/introduction
    ```
    npm install ewelink-api
   ```

## Plugin
0. Get plugin data into `YOUR_DOMOTICZ_PATH/plugins` directory
```
cd YOUR_DOMOTICZ_PATH/plugins
git clone git@github.com:MarcelSlabosz/domoticz_sonoff_ewelink_api_plugin.git
```
0. Restart Domoticz instance, eg.:  
```
systemctl restart domoticz.service
```

# How to configure

## Obtain parameters
0. Go to directory: `YOUR_DOMOTICZ_PATH/plugins/domoticz_sonoff_ewelink_api_plugin/`
0. Copy `credentials_template.js` to `credentials.js`
    ```
    cp credentials_template.js credentials.js
    ```
0. Open `credentials.js` file and type your eWeLink account credentials: email, password
0. Get the **Application token**, **Application key** and **Region** by executing command:
    ```
    node get_credentials.js
    ```
0. Get **Device id**. Run command:
    ```
    node list_devices.js
    ```
This command will list all devices added to your eWeLink account. Unfortunately there is no human readable names.
Base on *model* and *created date* try to choose right device id . 

## Add hardware
0. Go to Setup -> Hardware
0. Add new Hardware Type "Sonoff Original Soft eWeLink API" 

0. Fill form with parameters obtained in previous section
    * Name
    * Application token	
    * Application key	
    * Region
    * Device id

0. Click Add.
0. Now new device should appear in Domoticz: `{Name} - Switch`

# Add multiple hardware instances
To add multiple hardware instances you must use same **Application token**, **Application key** pair
in all off them. Each time when you call `node get_credentials.js` you need update parameters in all instances.

# Dependencies
* Node.js
* eWeLink opensource API: https://ewelink-api.now.sh/docs/introduction

# Troubleshooting

0. **"Node.js is not installed or not added to PATH!" is reported to logs.** 
    
    0. Make sure that node is available in PATH environment variable.
    0. Follow the step 1 in Install dependencies section. 
    
0. **"Plugin file call_ewelink_api.js was deleted! Revert changes in plugin dir." is reported to logs.**

    Probably some plugin file was accidentally removed. Revert changes by calling command
    ```git reset --hard``` in plugin root directory. If it doesn't help, please report the issue: 
    https://github.com/MarcelSlabosz/domoticz_sonoff_ewelink_api_plugin/issues
    