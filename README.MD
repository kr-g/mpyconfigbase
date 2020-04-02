
# MPyConfigBase

Configure automatic startup of MicroPython WLAN / AP / WebRepl / NTP time during boot 

## General information

Use this together with [mpycntrl](https://pypi.org/project/mpycntrl/) for automation of the setup/deployment and configuration of MicroPython base interfaces. see also [mpycntrl on github](https://github.com/kr-g/mpycntrl)

## Usage

The information given in the files `wlan.cfg`, `softap.cfg` and `webrepl_cfg.py` are used for configuration.

wlan.cfg and softap.cfg are text files containing ESSID and password in 2 lines

webrepl_cfg.py is a python file containing a single line like 

    PASS = '123456'

During wlan start the time from NTP is fetched by default.


## Best practice

* send cntrl+c
* upload the module file along with the configuration files directly (the config files are `wlan.cfg`, `softap.cfg` and `webrepl_cfg.py`)
* send reset


## Sample Code (in boot.py)

    from mpyconfigbase import *
    try:
        configbase = MPyConfigBase()
        configbase.start()
    except Exception as ex:
        print( "error:", ex )

    print("set ntp time", configbase.ntp )

    import time
    while True:
        print( "->", time.localtime( time.time() ) )
        time.sleep(1)


## Installation during deployment

The python class code can be retrieved by calling:

    fnam, src = MPyConfigBase.get_class_source() # get the module code
    cfgbootcode = MPyConfigBase.get_boot_install_code() # get the minimal autconfig code
 
 
## Sample Code (deployment)

Some sample code for automatic deployment and configuration is
available [here on github](https://github.com/kr-g/mpyconfigbase/blob/master/sample.py)

In case of timeouts (error message: could not enter raw-repl) consider to
use `with mpyc.timeout(1) as tout:` code block. 

Reset the board during the deployment is required since MicroPython needs
to bring in the new code before the configuration can take place.
If you follow the best practice given above this dont needs to be done.

               
## Limitations

on esp8266 the combined startup with `start` will probably fail.

on esp32 it will work :-)


