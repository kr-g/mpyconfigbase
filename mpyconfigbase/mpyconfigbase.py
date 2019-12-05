
def _get_machine_id():
    import machine
    return machine.unique_id()

def _get_machine_aes():
    import ucryptolib, ubinascii
    return ucryptolib.aes(ubinascii.hexlify( _get_machine_id() *2 ),1)

class _State:
    
    def __init__( self, name, active=False, isconnected=False, ifconfig=None ):
        self.name = name
        self.active = active
        self.isconnected = isconnected
        self.ifconfig = ifconfig
        
    def __repr__(self):
        return "<%s active=%s isconnected=%s ifconfig=%s>" % ( self.name, self.active, self.isconnected, self.ifconfig )


class MPyConfigBase:
    
    SOFTAP_CFG = "softap.cfg"
    WLAN_CFG = "wlan.cfg"
    WEBREPL_CFG = "webrepl_cfg.py"

    CONFIG_FILE = "mpyconfigbase"

    def load_from_conv(self,s):
        """overload this in subclass to encrypt credits info"""
        return s
    
    def save_to_conv(self,s):
        """overload this in subclass to decrypt credits info"""
        return s
    
    def __init__(self):
        self.webrepl = None
    
    def start(self):
        """start services configured before"""
        self.softap_start()
        self.wlan_start()
        self.webrepl_start()
        
    def stop(self):
        """stop all services"""
        self.webrepl_stop()
        self.wlan_stop()
        self.softap_stop()
    
    def _state( self, name, inet = None ):
        if inet:
            return _State( name, active=inet.active(), isconnected=inet.isconnected(), ifconfig=inet.ifconfig() )
        return _State( name )
    
    def __repr__(self):
        wlan_state = self._state("wlan",self.wlan)
        softap_state=self._state("ap",self.ap)
        
        webrepl_state=self._state("webrepl")
        if self.webrepl:
            webrepl_state = self._state( "webrepl", self.webrepl.network.WLAN() )
            
        return "\n".join( [repr( wlan_state ), repr( softap_state ), repr( webrepl_state )] )
    
    def softap_config(self,ssid,passwd):
        """set softap ssid and password for automatic connection during startup"""
        softap_cfg = "\n".join( [ssid, passwd] )
        if passwd == None or len(passwd)<8:
            raise Exception("password too short")
        try:
            with open( MPyConfigBase.SOFTAP_CFG, "wb" ) as f:
                f.write( self.save_to_conv( softap_cfg ) )
        except Exception as ex:
            print("softap config error:", ex )
    
    def softap_remove(self):
        """remove softap info and disable automatic connection during startup"""
        import uos
        self.softap_stop()
        uos.remove( MPyConfigBase.SOFTAP_CFG )
    
    def softap_start(self,active=True):
        """start softap if configured before, otherwise do nothing"""
        try:
            import network
            self.ap = network.WLAN(network.AP_IF)
            self.ap.active(False)
        except Exception as ex:
            pass
            
        try:
            with open( MPyConfigBase.SOFTAP_CFG ) as f:
                content = self.load_from_conv(f.read())
        except Exception as ex:
            # not configured fo autostart
            return

        try:
            credits = list(filter( lambda x : len(x) > 0, content.strip().split("\n") ))
            
            if active:
                self.ap.active(active)
                self.ap.config(essid=credits[0])
                self.ap.config(authmode=3, password = credits[1] )
                print( "softap", self.ap.ifconfig() )
                
        except Exception as ex:
            print("softap config error:", ex )
    
    def softap_stop(self):
        """disabled softap, no reconfiguration of prior configuration"""
        self.softap_start(active=False)
    
    
    def wlan_config(self,ssid,passwd):
        """set wlan ssid and password for automatic connection during startup"""
        wlan_cfg = "\n".join( [ssid, passwd] )
        if passwd == None or len(passwd)<8:
            raise Exception("password too short")
        try:
            with open( MPyConfigBase.WLAN_CFG, "wb" ) as f:
                f.write( self.save_to_conv( wlan_cfg ) )
        except Exception as ex:
            print("wlan config error:", ex )
            
    def wlan_remove(self):
        """remove wlan info and disable automatic connection during startup"""
        import uos
        self.wlan_stop()
        uos.remove( MPyConfigBase.WLAN_CFG )

    def wlan_start(self,active=True):
        """start wlan if configured before, otherwise do nothing"""
        try:
            import network
            self.wlan = network.WLAN(network.STA_IF)
            self.wlan.active(False)
        except:
            pass
    
        try:        
            with open( MPyConfigBase.WLAN_CFG ) as f:
                content = self.load_from_conv(f.read())
        except:
            return
        
        try:
            credits = list(filter( lambda x : len(x) > 0, content.strip().split("\n") ))
            
            if active:
                self.wlan.active(active)
                self.wlan.connect(credits[0].strip(), credits[1].strip())
                print( "wlan", self.wlan.ifconfig() )
                
        except Exception as ex:
            print("wlan config error:", ex )

    def wlan_stop(self):
        """disabled wlan, no reconfiguration of prior configuration"""
        if self.wlan:
            self.wlan_start(active=False)


    def webrepl_config(self,passwd):
        """set webrepl password for automatic connection during startup"""
        import uos
        try:
            uos.remove( MPyConfigBase.WEBREPL_CFG )
        except:
            pass
        if passwd == None:
            return
        if len(passwd)<6:
            raise Exception("password too short")
        with open( MPyConfigBase.WEBREPL_CFG, "w" ) as f:
            f.write( "PASS = '%s'\n" % passwd )

    def webrepl_remove(self):
        """remove webrepl info and disable automatic connection during startup"""
        self.webrepl_stop( )
        self.webrepl_config( None )

    def webrepl_start(self,active=True):
        """start webrepl if configured before, otherwise do nothing"""
        self.webrepl = None
        try:
            import webrepl
            if active:
                with open( MPyConfigBase.WEBREPL_CFG ) as f:
                    webrepl.start()
                    self.webrepl = webrepl
            else:
                webrepl.stop()
        except Exception as ex:
            pass        

    def webrepl_stop(self):
        """disabled webrepl, no reconfiguration of prior configuration"""
        self.webrepl_start(False)
        
    @classmethod    
    def get_class_source(cls):
        import inspect, textwrap
        src,lines = inspect.getsourcelines( cls )
        sourcecode = "".join(src)
        return ( MPyConfigBase.CONFIG_FILE+".py", textwrap.dedent(sourcecode)) # remove common leading withespace

    @classmethod    
    def get_boot_install_code(cls):
        import textwrap
        pycode = """
            from %s import *
            try:
                configbase = %s()
                configbase.start()
            except Exception as ex:
                print( "error:", ex )
            """ % ( MPyConfigBase.CONFIG_FILE, cls.__name__ )
        return textwrap.dedent(pycode)
