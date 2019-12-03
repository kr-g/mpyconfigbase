
import textwrap, time
import serial # its pyserial 
from mpycntrl import *
from mpyconfigbase import *


def sample_code():
    
    debug = True # display more information 
    trace = False # display no detail trace information 

    port = '/dev/ttyUSB0'
    baud = 115200
    bytesize = 8
    parity = 'N'
    stopbits = 1
    timeout = .35
    
    blk_size_esp8266 = 2048

    with serial.Serial(port=port, baudrate=baud,
                       bytesize=bytesize, parity=parity, stopbits=stopbits,
                       timeout=timeout) as ser:

        mpyc = MPyControl(ser,debug=debug,
                          trace=trace
                          )
            
        # enter raw-repl mode
        try:
            r = mpyc.send_cntrl_c()
            print( "received", r )
        except:
            r = mpyc.send_cntrl_c()
            print( "received", r )
        
        # get directory listing
        r = mpyc.cmd_ls()
        print( "received", r )
 
         # install the required py module
 
        fnam, src = MPyConfigBase.get_class_source() # get the module code
        cfgbootcode = MPyConfigBase.get_boot_install_code() # get the minimal autconfig code
 
        # put the module code onto the board
        # (its a hack here for the demo)
        # best practice is:
        # 1. send cntrl+c
        # 2. upload the module file along with the configuration files directly
        # 3. send reset
        r = mpyc.cmd_put( fnam, content = src.encode(), blk_size=blk_size_esp8266 )
        print( "received", r )

        # put some different code in boot.py to enable automatic configuration

        boot_org_code = """
            # This file is executed on every boot (including wake-boot from deepsleep)
            #import esp
            #esp.osdebug(None)
            import uos, machine
            #uos.dupterm(None, 1) # disable REPL on UART(0)

            import gc
            gc.collect()
        """
        
        custom_boot_code = """
            import time
            while True:
                print( "->", time.localtime( time.time() ) )
                time.sleep(1)
        """
        
        new_boot_code = "".join( [
            textwrap.dedent(boot_org_code),
            cfgbootcode, # <-- this contains the autoconfiguration module code, see above how to retrieve 
            textwrap.dedent(custom_boot_code) ] )
        
        r = mpyc.cmd_put( "boot.py", content = new_boot_code.encode(), blk_size=blk_size_esp8266 )
        print( "received", r )
       
        # reset micropython to bring in the new code
        r = mpyc.send_hardreset()
        print( "received", r )
              
        # enter raw-repl mode again
        try:
            r = mpyc.send_cntrl_c()
            print( "received", r )
        except:
            r = mpyc.send_cntrl_c()
            print( "received", r )

        # get directory listing
        with mpyc.timeout( 1 ) as tout:
            r = mpyc.cmd_ls()
            print( "received", r )

        # configure wlan, ap and webrepl autostartup
        # see below at the end how to disable it again by code
        cmd = """
            configbase.wlan_config( "your-ssid", "your-passwd" )
            configbase.webrepl_config( "123456" )
            configbase.softap_config( "MySSID-test", "12345678" )
            """
        with mpyc.timeout( 1 ) as tout:
            r = mpyc.sendcmd(cmd)
            print( "received", r )

        r = mpyc.cmd_ls()
        print( "received", r )

        # reset micropython to activate interfaces
        r = mpyc.send_hardreset()
        print( "received", r )
        
        # follow the output until cntrl+c is pressed
        # since enabling is async the config output will show some dummy ip adr (default behaviour)
        while True:
            r = mpyc.serial.readlines()
            print( "received", r )
           
        # 
        # execute manually via shell eg. mpfshell / rshell
        # and test the output by restarting with cntrl+d
        #
        # configbase.wlan_remove()
        #
        # configbase.webrepl_remove()
        #
        # configbase.softap_remove()
        # 
           
sample_code()
