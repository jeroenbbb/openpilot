#!/usr/bin/env python
# simple boardd wrapper that updates the panda first
import os
from panda import ensure_st_up_to_date
from common.params import Params

params = Params()

is_panda_absent = params.get("IsPandaAbsent").decode() == '1'

def main(gctx=None):

  if is_panda_absent:
    print ("No Panda available")
  else:
    ensure_st_up_to_date()
  
  #print ("Launch boardd")
  #os.chdir("boardd")
  #os.execvp("./boardd", ["./boardd"])
  
  # launch of boardd is now done in manager, this is not the right place

if __name__ == "__main__":
  main()

