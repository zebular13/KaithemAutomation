#Copyright Daniel Black 2013
#This file is part of Kaithem Automation.

#Kaithem Automation is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, version 3.

#Kaithem Automation is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with Kaithem Automation.  If not, see <http://www.gnu.org/licenses/>.

"""This file handles the big configuration file, provides access to it, and handles default settings"""

import yaml,argparse,sys,os, validictory

def load():
    _argp = argparse.ArgumentParser()
    
    #Manually specify a confifuration file, or else there must be one in /etc/kaithem
    _argp.add_argument("-c")
    _argp.add_argument("-p")
    argcmd = _argp.parse_args(sys.argv[1:])
    
    _dn = os.path.dirname(os.path.realpath(__file__))
    
    #This can't bw gotten from directories or wed get a circular import
    with open(os.path.join(_dn,"../data/default_configuration.yaml")) as f:
        _defconfig = yaml.load(f)
    
    #Attempt to open any manually specified config file
    if argcmd.c:
        with open(argcmd.c) as f:
            _usr_config = yaml.load(f)
            print ("Loaded configuration from "+ argcmd.c)
    else:
        _usr_config ={}
        print ("No CFG File Specified. Using Defaults.")
            
    
    #Config starts out as the default but individual options
    #Can be added or overridden by the user's settings.
    config = _defconfig.copy()
    
    for i in _usr_config:
        config[i] = _usr_config[i]
        
    if argcmd.p:
        config['https-port'] = int(argcmd.p)
    return config
            
c = load()
#This only tells us if it matches the general format, NOT if it
#is valid data. A filename can be a valid string but not refer to any valid file
#Even so, it is much better than nothing.
_dn = os.path.dirname(os.path.realpath(__file__))
with open(os.path.join(_dn,"../data/config-schema.yaml")) as f:
    validictory.validate(c,yaml.load(f))
config = c
del c
