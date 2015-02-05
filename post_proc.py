#!/home/maxhutch/anaconda3/bin/python

archive = "acherry#hpss_test/~/pub/"
output = "maxhutch#alpha-admin/pub/"
home_end = "alcf#dtn_mira/projects/alpha-nek/"
home = "/projects/alpha-nek/"

#source = "fingers/hemisphere/hemi_finger"
source = "fingers/hemisphere_wide/hemi_wide"
#source = "fingers/cone/cone_finger"

from os.path import dirname, basename
experiment = dirname(source)
run = basename(source)
start = 1
end   = 3
nodes = 1

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

def upload(home_end, output, source):
    experiment = dirname(source)
    parts = home_end.partition("/")
    home = parts[1] + parts[2]
    # setup transfer
    transfer = ""
    transfer += "{:s}/{:s}-results.dat {:s}/cache/{:s}-results.dat \n".format(home_end, source, output, source)
    transfer += "{:s}/{:s}.json {:s}/cache/{:s}.json \n".format(home_end, source, output, source)
    from os import listdir
    for file in listdir(home+experiment):
      if file[-3:] == "png":
        transfer += "{:s}/{:s} {:s}/{:s}/img/{:s} \n".format(home_end+experiment, file, output, experiment, file)
      if file[-3:] == "npz":
        transfer += "{:s}/{:s} {:s}/{:s}/dat/{:s} \n".format(home_end+experiment, file, output, experiment, file)
 
    # write and execute transfer
    with open("tmp.transfer", "w") as f:
      f.write(transfer)
    with open("tmp.transfer", "r") as f:
      call(args=["/usr/bin/ssh", "globus", "transfer -s 3 --label=upload_{:s}_proc".format(run)], stdin=f)

import json
with open("{:s}.json".format(home+source), "r") as f:
  params = json.load(f)

from os.path import exists
fname = get_fname(home+source, 0, end, params)
new_source = exists(fname)

from subprocess import call
if new_source:
  print("Found {:s}, archiving".format(fname))
  transfer = ""
  for j in range(start, end+1):
    for i in range(int(abs(params["io_files"]))):
      fname_src = get_fname(source, i, j, params) 
      fname_dst = get_fname(source, i, j, params, fmt = "{root:s}/raw/T{frame:05d}/{name:s}{proc:s}.f{frame:05d}") 
      transfer += "{:s}{:s} {:s}/{:s}\n".format(home_end, fname_src, archive, fname_dst)
  with open("tmp.transfer", "w") as f:
    f.write(transfer)
  
  with open("tmp.transfer", "r") as f:
    call(args=["/usr/bin/ssh", "globus", "transfer -s 3 --label=archive_{:s}_raw".format(run)], stdin=f)
else:
  print("Not Found {:s}, recovering".format(fname))
  transfer = ""
  for j in range(start, end+1):
    for i in range(int(abs(params["io_files"]))):
      fname_src = get_fname(source, i, j, params) 
      fname_dst = get_fname(source, i, j, params, fmt = "/raw/{root:s}/T{frame:05d}/{name:s}{proc:s}.f{frame:05d}") 
      transfer += "{:s}/{:s} {:s}/{:s}\n".format(archive, fname_dst, home_end, fname_src)
  with open("tmp.transfer", "w") as f:
    f.write(transfer)
  
  with open("tmp.stdout", "w") as f:
    call(args=["/usr/bin/ssh", "globus", "transfer --generate-id"], stdout=f)
  with open("tmp.stdout", "r") as f:
    taskid = f.readline()
  with open("tmp.transfer", "r") as f:
    call(args=["/usr/bin/ssh", "globus", "transfer -s 3 --label=restore_{:s}_raw --taskid={:s}".format(run, taskid)], stdin=f)
  print("Waiting for globus task {:s}".format(taskid))
  call(args=["/usr/bin/ssh", "globus", "wait -q {:s}".format(taskid)])

# queue processing job
if nodes != 0:
  with open("tmp.stdout", "w") as f:
    call(args=["qsub", "-t 60", "-n {:d}".format(nodes), "/projects/alpha-nek/pp.sh", home+source, "{:d} {:d}".format(start, end)], stdout=f)
  # wait for processing job
  with open("tmp.stdout", "r") as f:
    jobid = int(f.readline())
  print("Waiting for job {:d}".format(jobid))
  call(args=["cqwait", "{:d}".format(jobid)])

# setup upload
upload(home_end, output, source)

"""
from os import listdir
transfer = ""
transfer += "{:s}{:s}-results.dat {:s}/cache/{:s}-results.dat \n".format(home_end, source, output, source)
transfer += "{:s}{:s}.json {:s}/cache/{:s}.json \n".format(home_end, source, output, source)
for file in listdir(home+experiment):
  if file[-3:] == "png":
    transfer += "{:s}/{:s} {:s}/{:s}/img/{:s} \n".format(home_end+experiment, file, output,experiment, file)
  if file[-3:] == "npz":
    transfer += "{:s}/{:s} {:s}/{:s}/dat/{:s} \n".format(home_end+experiment, file, output,experiment, file)

# write and execute transfer
with open("tmp.transfer", "w") as f:
  f.write(transfer)
with open("tmp.transfer", "r") as f:
  call(args=["/usr/bin/ssh", "globus", "transfer -s 3 --label=upload_{:s}_proc".format(run)], stdin=f)
"""

# setup archive
upload(home_end, archive, source)

"""
transfer = ""
transfer += "{:s}{:s}-results.dat {:s}/cache/{:s}-results.dat \n".format(home_end, source, archive, source)
transfer += "{:s}{:s}.json {:s}/cache/{:s}.json \n".format(home_end, source, archive, source)
for file in listdir(home+experiment):
  if file[-3:] == "png":
    transfer += "{:s}/{:s} {:s}/{:s}/img/{:s} \n".format(home_end+experiment, file, archive, experiment, file)
  if file[-3:] == "npz":
    transfer += "{:s}/{:s} {:s}/{:s}/dat/{:s} \n".format(home_end+experiment, file, archive, experiment, file)

# write and execute transfer
with open("tmp.transfer", "w") as f:
  f.write(transfer)
with open("tmp.transfer", "r") as f:
  call(args=["/usr/bin/ssh", "globus", "transfer -s 3 --label=archive_{:s}_proc".format(run)], stdin=f)
"""

