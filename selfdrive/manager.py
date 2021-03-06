#!/usr/bin/env python3.5

# manager will start all requird processes (Python, C, C++)
# for testing see also https://medium.com/@comma_ai/open-sourcing-openpilot-development-tools-a5bc427867b6


import os
import sys
import fcntl
import errno
import signal
import subprocess
#import logging

#instead of setting the PYTHONPATH, it is better to set it here:
sys.path.append("/home/pi/openpilot")

from common.basedir import BASEDIR
sys.path.append(os.path.join(BASEDIR, "pyextra"))
os.environ['BASEDIR'] = BASEDIR

def unblock_stdout():
  # get a non-blocking stdout
  child_pid, child_pty = os.forkpty()
  if child_pid != 0: # parent

    # child is in its own process group, manually pass kill signals
    signal.signal(signal.SIGINT, lambda signum, frame: os.kill(child_pid, signal.SIGINT))
    signal.signal(signal.SIGTERM, lambda signum, frame: os.kill(child_pid, signal.SIGTERM))

    fcntl.fcntl(sys.stdout, fcntl.F_SETFL,
       fcntl.fcntl(sys.stdout, fcntl.F_GETFL) | os.O_NONBLOCK)

    while True:
      try:
        dat = os.read(child_pty, 4096)
      except OSError as e:
        if e.errno == errno.EIO:
          break
        continue

      if not dat:
        break

      try:
        sys.stdout.write(dat.decode("utf-8"))
      except (OSError, IOError):
        pass

    os._exit(os.wait()[1])


# update NEOS routine
# not required on Rpi

if __name__ == "__main__":
  neos_update_required = os.path.isfile("/init.qcom.rc") \
    and (not os.path.isfile("/VERSION") or int(open("/VERSION").read()) < 8)
  if neos_update_required:
    # update continue.sh before updating NEOS
    if os.path.isfile(os.path.join(BASEDIR, "scripts", "continue.sh")):
      from shutil import copyfile
      copyfile(os.path.join(BASEDIR, "scripts", "continue.sh"), "/data/data/com.termux/files/continue.sh")

    # run the updater
    print("Starting NEOS updater")
    subprocess.check_call(["git", "clean", "-xdf"], cwd=BASEDIR)
    os.system(os.path.join(BASEDIR, "installer", "updater", "updater"))
    raise Exception("NEOS outdated")
  elif os.path.isdir("/data/neoupdate"):
    from shutil import rmtree
    rmtree("/data/neoupdate")

  unblock_stdout()

import glob
import shutil
import hashlib
import importlib
import subprocess
import traceback
from multiprocessing import Process

import zmq
from setproctitle import setproctitle  #pylint: disable=no-name-in-module

from common.params import Params
import cereal
ThermalStatus = cereal.log.ThermalData.ThermalStatus

from selfdrive.services import service_list
from selfdrive.swaglog import cloudlog
import selfdrive.messaging as messaging
from selfdrive.registration import register
from selfdrive.version import version, dirty
import selfdrive.crash as crash

from selfdrive.loggerd.config import ROOT

cloudlog.info('Cloudlog info level is activated')

# comment out anything you don't want to run
# compilation in orb is an issue because it uses screen functions and an include file that is not available in headless env
# loggerd is compiled stuff so dont run it, its only logging anyway...
# gpsd replaced by gps.py
# and geofgence added

managed_processes = {
  "thermald": "selfdrive.thermald",
#  "uploader": "selfdrive.loggerd.uploader",
  "controlsd": "selfdrive.controls.controlsd",
  "radard": "selfdrive.controls.radard",
#  "ubloxd": "selfdrive.locationd.ubloxd",
#  "mapd": "selfdrive.mapd.mapd",
#  "loggerd": ("selfdrive/loggerd", ["./loggerd"]),
  "logmessaged": "selfdrive.logmessaged",
#  "tombstoned": "selfdrive.tombstoned",
#  "logcatd": ("selfdrive/logcatd", ["./logcatd"]),
#  "proclogd": ("selfdrive/proclogd", ["./proclogd"]),
   "boardd": "selfdrive.boardd.boardd",   # use python version
#  "boardd": ("selfdrive/boardd", ["./boardd"]),   # use python version  
   "pandad": "selfdrive.pandad",
#  "ui": ("selfdrive/ui", ["./start.sh"]),
  "calibrationd": "selfdrive.locationd.calibrationd",
#  "visiond": ("selfdrive/visiond", ["./visiond"]),
#  "sensord": ("selfdrive/sensord", ["./sensord"]),
#  "gpsd": ("selfdrive/sensord", ["./gpsd"]),
   "gpsd": "selfdrive.sensord.gps",
   "geofence": "selfdrive.sensord.geofence",  
#  "orbd": ("selfdrive/orbd", ["./orbd_wrapper.sh"]),
#  "updated": "selfdrive.updated",
}
android_packages = ("ai.comma.plus.offroad", "ai.comma.plus.frame")

running = {}
def get_running():
  return running

# due to qualcomm kernel bugs SIGKILLing visiond sometimes causes page table corruption
unkillable_processes = ['visiond']

# processes to end with SIGINT instead of SIGTERM
interrupt_processes = []

persistent_processes = [
  'thermald',
  'logmessaged',
  'logcatd',
  'tombstoned',
  'uploader',
  'ui',
  'gpsd',
  'geofence',
  'updated',
]

car_started_processes = [
  'controlsd',
  'loggerd',
  'sensord',
  'radard',
  'calibrationd',
  'visiond',
  'proclogd',
  'ubloxd',
  'orbd',
  'mapd',
]

def register_managed_process(name, desc, car_started=False):
  global managed_processes, car_started_processes, persistent_processes
  print("registering %s" % name)
  managed_processes[name] = desc
  if car_started:
    car_started_processes.append(name)
  else:
    persistent_processes.append(name)

# ****************** process management functions ******************
def launcher(proc, gctx):
  try:
    # import the process
    mod = importlib.import_module(proc)

    # rename the process
    setproctitle(proc)

    # exec the process
    mod.main(gctx)
  except KeyboardInterrupt:
    cloudlog.warning("child %s got SIGINT" % proc)
  except Exception:
    # can't install the crash handler becuase sys.excepthook doesn't play nice
    # with threads, so catch it here.
    crash.capture_exception()
    raise

def nativelauncher(pargs, cwd):
  # exec the process
  os.chdir(cwd)

  # because when extracted from pex zips permissions get lost -_-
  os.chmod(pargs[0], 0o700)
  
  # native processesmay fail 
  try:
    os.execvp(pargs[0], pargs)
  except OSError:
    cloudlog.info("Warning: native process not started: " + pargs[0] + " in directory " + cwd)

def start_managed_process(name):
  if name in running or name not in managed_processes:
    # cloudlog.info("name not in managed processes: %s" % name)
    return
  proc = managed_processes[name]
  if isinstance(proc, str):
    cloudlog.info("starting python %s" % proc)
    running[name] = Process(name=name, target=launcher, args=(proc, gctx))
  else:
    pdir, pargs = proc
    cwd = os.path.join(BASEDIR, pdir)
    cloudlog.info("starting process %s" % name)
    running[name] = Process(name=name, target=nativelauncher, args=(pargs, cwd))
  running[name].start()

def prepare_managed_process(p):
  proc = managed_processes[p]
  if isinstance(proc, str):
    # import this python
    cloudlog.info("preimporting %s" % proc)
    importlib.import_module(proc)
  else:
    # build this process
    cloudlog.info("building %s" % (proc,))
    try:
      subprocess.check_call(["make", "-j4"], cwd=os.path.join(BASEDIR, proc[0]))
    except subprocess.CalledProcessError:
      # make clean if the build failed
      cloudlog.warning("building %s failed, make clean" % (proc, ))
      subprocess.check_call(["make", "clean"], cwd=os.path.join(BASEDIR, proc[0]))
      # strange, why try again ?? comment out
      # subprocess.check_call(["make", "-j4"], cwd=os.path.join(BASEDIR, proc[0]))

def kill_managed_process(name):
  if name not in running or name not in managed_processes:
    return
  cloudlog.info("killing %s" % name)

  if running[name].exitcode is None:
    if name in interrupt_processes:
      os.kill(running[name].pid, signal.SIGINT)
    else:
      running[name].terminate()

    # give it 5 seconds to die
    running[name].join(5.0)
    if running[name].exitcode is None:
      if name in unkillable_processes:
        cloudlog.critical("unkillable process %s failed to exit! rebooting in 15 if it doesn't die" % name)
        running[name].join(15.0)
        if running[name].exitcode is None:
          cloudlog.critical("FORCE REBOOTING PHONE!")
          os.system("date >> /sdcard/unkillable_reboot")
          os.system("reboot")
          raise RuntimeError
      else:
        cloudlog.info("killing %s with SIGKILL" % name)
        os.kill(running[name].pid, signal.SIGKILL)
        running[name].join()

  cloudlog.info("%s is dead with %d" % (name, running[name].exitcode))
  del running[name]

def pm_apply_packages(cmd):
  for p in android_packages:
    system("pm %s %s" % (cmd, p))

def cleanup_all_processes(signal, frame):
  cloudlog.info("caught ctrl-c %s %s" % (signal, frame))

  pm_apply_packages('disable')

  for name in list(running.keys()):
    kill_managed_process(name)
    cloudlog.info("Killing " + name)
  cloudlog.info("everything is dead")


# ****************** run loop ******************

def manager_init(should_register=True):
  global gctx

  if should_register:
    reg_res = register()
    if reg_res:
      dongle_id, dongle_secret = reg_res
    else:
      raise Exception("server registration failed")
  else:
    dongle_id = "c"*16

  # set dongle id
  dongle_id_str = dongle_id.decode()
  cloudlog.info("dongle id is " + dongle_id_str)
  os.environ['DONGLE_ID'] = dongle_id_str

  cloudlog.info("dirty is %d" % dirty)
  if not dirty:
    os.environ['CLEAN'] = '1'

  cloudlog.bind_global(dongle_id=dongle_id_str, version=version, dirty=dirty, is_eon=True)
  crash.bind_user(id=dongle_id_str)
  crash.bind_extra(version=version, dirty=dirty, is_eon=True)

  os.umask(0)
  try:
    os.mkdir(ROOT, 0o777)
  except OSError:
    pass

  # set gctx
  gctx = {}

def system(cmd):
  try:
    cloudlog.info("running %s" % cmd)
    subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
  except subprocess.CalledProcessError as e:
    cloudlog.event("running failed",
      cmd=e.cmd,
      output=e.output[-1024:],
      returncode=e.returncode)

#--- manager thread --------------------------------------------
def manager_thread():
  # now loop
  context = zmq.Context()
  thermal_sock = messaging.sub_sock(context, service_list['thermal'].port)

  cloudlog.info("manager start")
  cloudlog.info({"environ": os.environ})

  # save boot log
  # this is closed software so it cannot run on a RPi
  logger_dead = False
  try:
    subprocess.call(["./loggerd", "--bootlog"], cwd=os.path.join(BASEDIR, "selfdrive/loggerd"))
  except OSError:
    # no worries, it is only logging
    logger_dead = True

  for p in persistent_processes:
    start_managed_process(p)

  # start frame
  pm_apply_packages('enable')
  system("am start -n ai.comma.plus.frame/.MainActivity")

  if os.getenv("NOBOARD") is None:
    cloudlog.info("start pandad and boardd")
    start_managed_process("pandad")

  params = Params()

  while 1:

    # read thermal msg to check cpu temperature and free space
    msg = messaging.recv_sock(thermal_sock, wait=True)

    # uploader is gated based on the phone temperature
    if msg.thermal.thermalStatus >= ThermalStatus.yellow:
      kill_managed_process("uploader")
    else:
      start_managed_process("uploader")

    if msg.thermal.freeSpace < 0.05:
      logger_dead = True

    # if thermal msg is available, start all car_started processes
    if msg.thermal.started:
      for p in car_started_processes:
        if p == "loggerd" and logger_dead:
          kill_managed_process(p)
        else:
          start_managed_process(p)
    else:
      logger_dead = False
      for p in car_started_processes:
        kill_managed_process(p)

    
    # check if pandad has finished and boardd is not running yet
    # pandad is updating the panda module and needs to be finished before we can start boardd
    # a process gives exit code 0 if it ended correctly
    # exit code == None is process is still running
    if 'pandad' in running and 'boardd' not in running:
      if running['pandad'].exitcode == 0:
        start_managed_process('boardd')
    
    # check the status of all processes, did any of them die?
    # and minimize number of logmessages
    cloudMsg = "Running: "
    for p in running:
      cloudMsg = cloudMsg + " %s %s, " % (p, running[p])
      # cloudlog.debug("   Running %s %s" % (p, running[p]))
    cloudlog.info(cloudMsg)

    # is this still needed?
    if params.get("DoUninstall") == "1":
      break

def get_installed_apks():
  # use pm command to list all available packages, not required on Rpi
  try:
    dat = subprocess.check_output(["pm", "list", "packages", "-f"]).strip().split("\n")
  except FileNotFoundError:
    # make empty list
    dat = []
    
  ret = {}
  for x in dat:
    if x.startswith("package:"):
      v,k = x.split("package:")[1].split("=")
      ret[k] = v
  return ret

def install_apk(path):
  # can only install from world readable path
  install_path = "/sdcard/%s" % os.path.basename(path)
  shutil.copyfile(path, install_path)

  ret = subprocess.call(["pm", "install", "-r", install_path])
  os.remove(install_path)
  return ret == 0

def update_apks():
  # install apks
  installed = get_installed_apks()

  install_apks = glob.glob(os.path.join(BASEDIR, "apk/*.apk"))
  for apk in install_apks:
    app = os.path.basename(apk)[:-4]
    if app not in installed:
      installed[app] = None

  cloudlog.info("installed apks %s" % (str(installed), ))

  for app in installed.keys():

    apk_path = os.path.join(BASEDIR, "apk/"+app+".apk")
    if not os.path.exists(apk_path):
      continue

    h1 = hashlib.sha1(open(apk_path).read()).hexdigest()
    h2 = None
    if installed[app] is not None:
      h2 = hashlib.sha1(open(installed[app]).read()).hexdigest()
      cloudlog.info("comparing version of %s  %s vs %s" % (app, h1, h2))

    if h2 is None or h1 != h2:
      cloudlog.info("installing %s" % app)

      success = install_apk(apk_path)
      if not success:
        cloudlog.info("needing to uninstall %s" % app)
        system("pm uninstall %s" % app)
        success = install_apk(apk_path)

      assert success

def manager_update():
  if os.path.exists(os.path.join(BASEDIR, "vpn")):
    cloudlog.info("installing vpn")
    os.system(os.path.join(BASEDIR, "vpn", "install.sh"))
  update_apks()

def manager_prepare():
  # build cereal first
  # cereal is capnp stuff for rpc calls to c++ and java
  # subprocess.check_call(["make", "-j4"], cwd=os.path.join(BASEDIR, "cereal"))

  # build all processes
  os.chdir(os.path.dirname(os.path.abspath(__file__)))
  for p in managed_processes:
    prepare_managed_process(p)

def uninstall():
  cloudlog.warning("uninstalling")
  with open('/cache/recovery/command', 'w') as f:
    f.write('--wipe_data\n')
  # IPowerManager.reboot(confirm=false, reason="recovery", wait=true)
  os.system("service call power 16 i32 0 s16 recovery i32 1")

def xstr(s):
    return '' if s is None else str(s)  
    
def main():
  # the flippening!
  os.system('LD_LIBRARY_PATH="" content insert --uri content://settings/system --bind name:s:user_rotation --bind value:i:1')
  
  cloudlog.info('NOLOG=' + xstr(os.getenv("NOLOG")))
  cloudlog.info('NOUPLOAD=' + xstr(os.getenv("NOUPLOAD")))
  cloudlog.info('NOVISION=' + xstr(os.getenv("NOVISION")))
  cloudlog.info('LEAN=' + xstr(os.getenv("LEAN")))
  cloudlog.info('NOCONTROL=' + xstr(os.getenv("NOCONTROL")))
  cloudlog.info('PASSIVE=' + xstr(os.getenv("PASSIVE")))
  cloudlog.info('PREPAREONLY=' + xstr(os.getenv("PREPAREONLY")))
  cloudlog.info('BASEDIR=' + xstr(os.getenv("BASEDIR")))

  if os.getenv("NOLOG") is not None:
    del managed_processes['loggerd']
    del managed_processes['tombstoned']
  if os.getenv("NOUPLOAD") is not None:
    del managed_processes['uploader']
  if os.getenv("NOVISION") is not None:
    del managed_processes['visiond']
  if os.getenv("LEAN") is not None:
    del managed_processes['uploader']
    del managed_processes['loggerd']
    del managed_processes['logmessaged']
    del managed_processes['logcatd']
    del managed_processes['tombstoned']
    del managed_processes['proclogd']
  if os.getenv("NOCONTROL") is not None:
    del managed_processes['controlsd']
    del managed_processes['radard']

  # support additional internal only extensions
  try:
    import selfdrive.manager_extensions
    selfdrive.manager_extensions.register(register_managed_process)
  except ImportError:
    pass

  params = Params()
  params.manager_start()

  # set unset params
  if params.get("IsMetric") is None:
    params.put("IsMetric", "0")
  if params.get("RecordFront") is None:
    params.put("RecordFront", "0")
  if params.get("IsFcwEnabled") is None:
    params.put("IsFcwEnabled", "1")
  if params.get("HasAcceptedTerms") is None:
    params.put("HasAcceptedTerms", "0")
  if params.get("IsUploadVideoOverCellularEnabled") is None:
    params.put("IsUploadVideoOverCellularEnabled", "1")
  if params.get("IsDriverMonitoringEnabled") is None:
    params.put("IsDriverMonitoringEnabled", "1")
  if params.get("IsGeofenceEnabled") is None:
    params.put("IsGeofenceEnabled", "-1")
  if params.get("SpeedLimitOffset") is None:
    params.put("SpeedLimitOffset", "0")
  if params.get("LongitudinalControl") is None:
    params.put("LongitudinalControl", "0")
  if params.get("LimitSetSpeed") is None:
    params.put("LimitSetSpeed", "0")
  if params.get("GeoFence") is None:
    params.put("GeoFence", "")
  if params.get("UploadWebsite") is None:
    params.put("UploadWebsite", "")

  # is this chffrplus?
  if os.getenv("PASSIVE") is not None:
    params.put("Passive", str(int(os.getenv("PASSIVE"))))

  if params.get("Passive") is None:
    raise Exception("Passive must be set to continue")

  # put something on screen while we set things up
  if os.getenv("PREPAREONLY") is not None:
    spinner_proc = None
  else:
    spinner_text = "chffrplus" if params.get("Passive")=="1" else "openpilot"
    cloudlog.info('Try to start C executable Spinner=' + spinner_text)
    # TODO: add try/
    try:
      spinner_proc = subprocess.Popen(["./spinner", "loading %s"%spinner_text],
        cwd=os.path.join(BASEDIR, "selfdrive", "ui", "spinner"),
        close_fds=True)
    except OSError:
      cloudlog.info('C executable Spinner falied with OSError')
      spinner_proc = False
      
  try:
    manager_update()
    manager_init()
    manager_prepare()
  finally:
    if spinner_proc:
      spinner_proc.terminate()

  if os.getenv("PREPAREONLY") is not None:
    return

  # SystemExit on sigterm
  signal.signal(signal.SIGTERM, lambda signum, frame: sys.exit(1))

  try:
    manager_thread()
  except Exception:
    traceback.print_exc()
    crash.capture_exception()
  finally:
    cleanup_all_processes(None, None)

  if params.get("DoUninstall") == "1":
    uninstall()

if __name__ == "__main__":
  cloudlog.info('Start main()')
  main()
  # manual exit because we are forked
  sys.exit(0)
