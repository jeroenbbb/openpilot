#!/usr/bin/env python
# simple boardd wrapper that updates the panda first
import os
from panda import ensure_st_up_to_date

def main(gctx=None):
  ensure_st_up_to_date()
  
  print ("Launch boardd")

  #os.chdir("boardd")
  #os.execvp("./boardd", ["./boardd"])
  
  # now done in manager, this is nnot the right place

if __name__ == "__main__":
  main()

