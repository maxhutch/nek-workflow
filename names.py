
def get_fname(source, proc_i, frame, params, fmt = None):
  from os.path import dirname, basename
  from math import log10
  if fmt == None and params["io_files"] > 0:
    fmt = "{root:s}{name:s}{proc:s}.f{frame:05d}"
  elif fmt == None:
    fmt = "{root:s}/A{proc:s}/{name:s}{proc:s}.f{frame:05d}"
  root = dirname(source)
  name  = basename(source)
  dir_width = int(log10(max(abs(params["io_files"])-1,1)))+1
  proc = "{:0{width}d}".format(proc_i, width=dir_width)
  fname = fmt.format(**locals())
  return fname

