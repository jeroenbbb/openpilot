import json
import subprocess

from selfdrive.swaglog import cloudlog
from selfdrive.version import version, training_version
from common.api import api_get
from common.params import Params

# register device usung IMEI, serial number
# but RPi has no IMEI so put in fake numbers
#

def get_imei():
  #ret = subprocess.check_output(["getprop", "oem.device.imeicache"]).strip()
  ret = "RPi"
  if ret == "":
    ret = "000000000000000"
  return ret

def get_serial():
  #return subprocess.check_output(["getprop", "ro.serialno"]).strip()
  cpuserial = "0000000000000000"
  try:
    f = open('/proc/cpuinfo','r')
    for line in f:
      if line[0:6]=='Serial':
        cpuserial = line[10:26]
    f.close()
  except:
    cpuserial = "ERROR000000000"
  return cpuserial


def get_git_commit():
  return subprocess.check_output(["git", "rev-parse", "HEAD"]).strip()

def get_git_branch():
  return subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"]).strip()

def get_git_remote():
  return subprocess.check_output(["git", "config", "--get", "remote.origin.url"]).strip()

def register():
  params = Params()
  params.put("Version", version)
  params.put("TrainingVersion", training_version)
  params.put("GitCommit", get_git_commit())
  params.put("GitBranch", get_git_branch())
  params.put("GitRemote", get_git_remote())

  dongle_id, access_token = params.get("DongleId"), params.get("AccessToken")

  try:
    if dongle_id is None or access_token is None:
      cloudlog.info("getting pilotauth")
      # read http://api.commadotai.com/ using IMEI and serial number
      print ("Posting to pilotauth")
      resp = api_get("v1/pilotauth/", method='POST', timeout=15,
                     imei=get_imei(), serial=get_serial())
      print ("Output received using " + get_imei() + " / " + get_serial() + "=" + resp)
      dongleauth = json.loads(resp.text)
      print ("Reading pilotauth - 2")
      dongle_id, access_token = dongleauth["dongle_id"].encode('ascii'), dongleauth["access_token"].encode('ascii')

      params.put("DongleId", dongle_id)
      params.put("AccessToken", access_token)
    return dongle_id, access_token
  except Exception:
    cloudlog.exception("failed to authenticate")
    return None

if __name__ == "__main__":
  print(api_get("").text)
  print(register())
