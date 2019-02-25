import os

if os.environ.get('LOGGERD_ROOT', False):
  ROOT = os.environ['LOGGERD_ROOT']
  print("Custom loggerd root: ", ROOT)
else:
  ROOT = '/data/media/0/realdata/'
  if not os.path.exists(ROOT):
    # take the params file, that should exist
    ROOT = '/data/params/d'

SEGMENT_LENGTH = 60
