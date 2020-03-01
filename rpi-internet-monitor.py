#!/usr/bin/env python3

import subprocess
import sys
import time

try:
    sys.argv[2] == "-test" # force a router reboot
    DELAY_BETWEEN_PINGS = 1    # delay in seconds
    DELAY_BETWEEN_TESTS = 10  # delay in seconds
    LONG_DELAY = 20 # delay in seconds
    SITES = ["google.blah", "comcast.blah"]
except:
    DELAY_BETWEEN_PINGS = 1    # delay in seconds
    DELAY_BETWEEN_TESTS = 120  # delay in seconds
    LONG_DELAY = 3600 # delay in seconds
    SITES = ["google.com", "comcast.com"]


# turn off the usb port connected to the power strip for DELAY_BETWEEN_TESTS time
def turn_off_usb(reboot):
    if reboot == 0:
      cmd = "sudo /home/pi/uhubctl/uhubctl -l 1-1 -a off"
      try:
        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
        debug_message(debug, output)
        time.sleep(DELAY_BETWEEN_TESTS) # wait some time for the router to power down
        cmd = "sudo /home/pi/uhubctl/uhubctl -l 1-1 -a on"
        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
        debug_message(debug, output)
        time.sleep(DELAY_BETWEEN_TESTS) # wait for the router to boot back up befoe continuing
        time.sleep(DELAY_BETWEEN_TESTS)
        print("--- Rebooted the router! ---")
      except subprocess.CalledProcessError:
        debug_message(debug, cmd + ": error")
        return 0    
    else:
        debug_message(debug, "--- waiting a long time ---")
        print("--- In long wait loop. ---")
        time.sleep(LONG_DELAY)
        return 1

# print messages for debugging when indicator is set
def debug_message(debug_indicator, output_message):
  if debug_indicator:
    print(output_message)

# issue Linux ping command to determine internet connection status
def ping(site):
  cmd = "/bin/ping -c 1 " + site
  try:
    output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
  except subprocess.CalledProcessError:
    debug_message(debug, site + ": not reachable")
    return 0
  else:
    debug_message(debug, site + ": reachable")
    return 1

# ping the sites in the site list the specified number of times
# and calculate the percentage of successful pings
def ping_sites(site_list, wait_time, times):
  successful_pings = 0
  attempted_pings = times * len(site_list)
  for t in range(0, times):
    for s in site_list:
      successful_pings += ping(s)
      time.sleep(wait_time)
  debug_message(debug, "Percentage successful: " + str(int(100 * (successful_pings / float(attempted_pings)))) + "%")
  return successful_pings / float(attempted_pings)   # return percentage successful 

      
# main program starts here

# check to see if the user wants to print debugging messages
debug = False
if len(sys.argv) > 1:
  if sys.argv[1] == "-debug":
    debug = True
  else:
    print("unknown option specified: " + sys.argv[1])
    sys.exit(1)


# main loop: ping sites, turn appropriate lamp on, wait, repeat
test = 0
reboot = -1
while True:
  test+=1
  debug_message(debug, "----- Test " + str(test) + " -----")
  try:
      sys.argv[2] == "-test" # force a router reboot
      success = 0
  except:
      success = ping_sites(SITES, DELAY_BETWEEN_PINGS, 2)
  if success == 0:
      debug_message(debug, "---- No internet - restarting router ----")
      reboot+=1
      turn_off_usb(reboot)
  else:
      debug_message(debug, "---- Internet is working fine ----")
      reboot = -1
  debug_message(debug, "Waiting " + str(DELAY_BETWEEN_TESTS) + " seconds until next test.")
  time.sleep(DELAY_BETWEEN_TESTS)

