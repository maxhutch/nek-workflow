
def upload_results(home_end, output, source):
  from os.path import dirname, basename
  experiment = dirname(source)
  run = basename(source)
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
  from subprocess import call
  with open("tmp.transfer", "w") as f:
    f.write(transfer)
  with open("tmp.transfer", "r") as f:
    call(args=["/usr/bin/ssh", "globus", "transfer -s 3 --label=upload_{:s}_proc".format(run)], stdin=f)

def archive(archive, home_end, source, start, end, params):
  from os.path import basename
  run = basename(source)
  from names import get_fname
  transfer = ""
  for j in range(start, end+1):
    for i in range(int(abs(params["io_files"]))):
      fname_src = get_fname(source, i, j, params) 
      fname_dst = get_fname(source, i, j, params, fmt = "{root:s}/raw/T{frame:05d}/{name:s}{proc:s}.f{frame:05d}") 
      transfer += "{:s}{:s} {:s}/{:s}\n".format(home_end, fname_src, archive, fname_dst)
  with open("tmp.transfer", "w") as f:
    f.write(transfer)
  
  from subprocess import call
  with open("tmp.transfer", "r") as f:
    call(args=["/usr/bin/ssh", "globus", "transfer -s 3 --label=archive_{:s}_raw".format(run)], stdin=f)

def recover(archive, home_end, source, start, end, params):
  from os.path import basename
  run = basename(source)
  from names import get_fname
  transfer = ""
  for j in range(start, end+1):
    for i in range(int(abs(params["io_files"]))):
      fname_src = get_fname(source, i, j, params) 
      fname_dst = get_fname(source, i, j, params, fmt = "/{root:s}/raw/T{frame:05d}/{name:s}{proc:s}.f{frame:05d}") 
      transfer += "{:s}/{:s} {:s}/{:s}\n".format(archive, fname_dst, home_end, fname_src)
  with open("tmp.transfer", "w") as f:
    f.write(transfer)
  
  from subprocess import call
  with open("tmp.stdout", "w") as f:
    call(args=["/usr/bin/ssh", "globus", "transfer --generate-id"], stdout=f)
  with open("tmp.stdout", "r") as f:
    taskid = f.readline()
  with open("tmp.transfer", "r") as f:
    call(args=["/usr/bin/ssh", "globus", "transfer -s 3 --label=restore_{:s}_raw --taskid={:s}".format(run, taskid)], stdin=f)
  print("Waiting for globus task {:s}".format(taskid))
  call(args=["/usr/bin/ssh", "globus", "wait -q {:s}".format(taskid)])
