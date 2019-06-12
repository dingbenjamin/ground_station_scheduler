# Takes a TLE from a provided input file and schedules a pass script
# to run on the next pass of the requested satellite
#
# Package requirements: at
# Pip3 requirements: numpy, skyfield, pytz
#
# Example usage: 
# python3 scheduler.py -i tle.txt -s "ISS (ZARYA)" -p "python3 track.py"

from skyfield.api import Topos, load
from pytz import timezone
import sys, getopt
import datetime
import numpy as np
import os

GROUND_STATION = Topos('37.8136 S', '144.9631 E')
DEFAULT_TLE_FILE = 'tle.txt'
DEFAULT_SATELLITE_NAME = "ACRUX-1"
DEFAULT_PASS_SCRIPT = "python3 pass.py"

def get_next_pass(satellite, satellite_name):
    # Create a time vector of 24 hours
    ts = load.timescale()
    current = datetime.datetime.now()
    minutes = range(current.minute, 60 * 24 + current.minute)
    t = ts.utc(current.year, current.month, current.day, current.hour, \
            minutes)
    
    orbit = (satellite - GROUND_STATION).at(t)
    alt, az, distance = orbit.altaz()

    above_horizon = alt.degrees > 0
    boundaries, = np.diff(above_horizon).nonzero()
    passes = boundaries.reshape(len(boundaries) // 2, 2)
    if len(passes) > 0:
        return passes[0]
    else:
        print("Error, no passes found for {}".format(satellite_name))
        sys.exit(2)

# Takes a TLE file and finds the ACRUX1 entry. 
# If no correct entry exists the program will abort
def schedule(tle_file, satellite_name, pass_script):
    satellites = load.tle(tle_file, reload=True)
    if satellite_name in satellites:
        satellite = satellites[satellite_name]
        next_pass = get_next_pass(satellite, satellite_name)
        
        if next_pass[0] - 1 > 0:
            minutes_to_wait = next_pass[0] - 1
        else:
            minutes_to_wait = 0

        # Schedule the defined command to run on a pass
        os.system("{} | at now + {} minutes".format(pass_script, \
                str(minutes_to_wait)))
        print("Scheduling success")

    else:
        print('Did not find {} in provided TLE'.format(satellite_name))

def main(argv):
    tle_file = DEFAULT_TLE_FILE
    satellite_name = DEFAULT_SATELLITE_NAME
    pass_script = DEFAULT_PASS_SCRIPT

    try:
        opts, args = getopt.getopt(argv,"hi:s:p:", \
                ["tle=","satellite=","pass-script"])
    except getopt.GetoptError:
        print('scheduler.py -i <tle> -s <satellite>')
        sys.exit(2)
    
    for opt, arg in opts:
        if opt in ('-i, "--tle"'):
            tle_file = arg
        elif opt in ('-s, "--satellite"'):
            satellite_name = arg
        elif opt in ('-p, "--pass-script"'):
            pass_script = arg

    print('Scheduling the next pass from TLE:', tle_file)
    schedule(tle_file, satellite_name, pass_script)

if __name__ == "__main__":
    main(sys.argv[1:])
