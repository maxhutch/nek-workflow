from subprocess import call, check_output

def globus_exists(path):
  foo = check_output(args=["/usr/bin/ssh", "globus", "ls {:s}".format(path)])
  return not len(foo) == 0

def transfer_sync(transfer, label="workflow_sync"):
  with open("tmp.transfer", "w") as f:
    f.write(transfer)
  taskid = check_output(args=["/usr/bin/ssh", "globus", "transfer --generate-id"]).decode("utf-8")
  with open("tmp.transfer", "r") as f:
    call(args=["/usr/bin/ssh", "globus", "transfer -s 3 --label={:s} --taskid={:s}".format(label, taskid)], stdin=f)
  print("Waiting for globus task {:s}".format(taskid))
  call(args=["/usr/bin/ssh", "globus", "wait -q {:s}".format(taskid)])

def transfer_async(transfer, label="workflow_async"):
  with open("tmp.transfer", "w") as f:
    f.write(transfer)
  with open("tmp.transfer", "r") as f:
    call(args=["/usr/bin/ssh", "globus", "transfer -s 3 --label={:s}".format(label)], stdin=f)

def upload_results(home_end, output, source):
  from os.path import dirname, basename
  experiment = dirname(source)
  run = basename(source)
  parts = home_end.partition("/")
  home = parts[1] + parts[2]
  # setup transfer
  transfer = ""
  transfer += "{:s}/{:s}-results/ {:s}/{:s}-results/ -r \n".format(home_end, source, output, source)
  transfer += "{:s}/{:s}.json {:s}/{:s}.json \n".format(home_end, source, output, source)
  from os import listdir
  for file in listdir(home+experiment):
    if file[-3:] == "png":
      transfer += "{:s}/{:s} {:s}/{:s}/img/{:s} \n".format(home_end+experiment, file, output, experiment, file)
    if file[-3:] == "npz":
      transfer += "{:s}/{:s} {:s}/{:s}/dat/{:s} \n".format(home_end+experiment, file, output, experiment, file)
 
  # write and execute transfer
  transfer_async(transfer, "upload_{:s}_proc".format(run))

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
  transfer_async(transfer, "archive_{:s}_raw".format(run))

def recover_chest(archive, home_end, source):
  from os.path import basename
  run = basename(source)
  fname_src = "{:s}/{:s}-results/".format(archive, source)
  fname_dst = "{:s}/{:s}-results/".format(home_end, source)
  transfer = ""
  if globus_exists(fname_src):
    transfer += "{:s} {:s} -r \n".format(fname_src, fname_dst)
  fname_src = "{:s}/{:s}.json".format(archive, source)
  fname_dst = "{:s}/{:s}.json".format(home_end, source)
  if globus_exists(fname_src):
    transfer += "{:s} {:s} \n".format(fname_src, fname_dst)

  transfer_sync(transfer, "recover_{:s}_chest".format(run))

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
  transfer_sync(transfer, "restore_{:s}_raw".format(run))
