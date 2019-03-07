#!/usr/bin/env python
import os
import time
from sys import exit
from common.params import Params

is_panda_absent = params.get("IsPandaAbsent").decode() == '1'

def ensure_st_up_to_date():
  from panda import Panda, PandaDFU, BASEDIR

  with open(os.path.join(BASEDIR, "VERSION")) as f:
    repo_version = f.read()

  panda = None
  panda_dfu = None
  should_flash_recover = False
  
  if is_panda_absent:
    exit(0)

  while not is_panda_absent:
    
    # break on normal mode Panda
    panda_list = Panda.list()
    if len(panda_list) > 0:
      panda = Panda(panda_list[0])
      break

    # flash on DFU mode Panda
    panda_dfu = PandaDFU.list()
    if len(panda_dfu) > 0:
      panda_dfu = PandaDFU(panda_dfu[0])
      panda_dfu.recover()
      
    print ("waiting for board in panda.python.update.py ...")
    time.sleep(1)

  if panda.bootstub or not panda.get_version().startswith(repo_version):
    panda.flash()

  if panda.bootstub:
    panda.recover()

  assert(not panda.bootstub)
  version = str(panda.get_version())
  print("%s should be %s" % (version, repo_version))
  assert(version.startswith(repo_version))

if __name__ == "__main__":
  ensure_st_up_to_date()

