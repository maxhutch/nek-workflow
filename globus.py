from subprocess import call, check_output
from globussh import exists, transfer

def tar(tar, files):
  call(args=["tar", "cvf", tar,]+files)

def upload_results(home_end, output, source):
  from os.path import dirname, basename
  experiment = dirname(source)
  run = basename(source)
  parts = home_end.partition("/")
  home = parts[1] + parts[2]
  # setup transfer
  xfr = ""
  xfr += "{:s}/{:s}-results/ {:s}/{:s}-results/ -r \n".format(home_end, source, output, source)
  xfr += "{:s}/{:s}.json {:s}/{:s}.json \n".format(home_end, source, output, source)
  from os import listdir
  for file in listdir(home+experiment):
    if file[-3:] == "png":
      xfr += "{:s}/{:s} {:s}/{:s}/img/{:s} \n".format(home_end+experiment, file, output, experiment, file)
    if file[-6:] == "output":
      xfr += "{:s}/{:s} {:s}/{:s}/stdout/{:s} \n".format(home_end+experiment, file, output, experiment, file)
 
  # write and execute transfer
  transfer(xfr, sync=None, label="upload_proc".format(run), block=False)

def archive(archive, home_end, root, source, start, end, params):
  from os.path import basename
  from os import remove
  run = basename(source)
  from names import get_fname
  for j in range(start, end+1):
    files_src = []
    for i in range(int(abs(params["io_files"]))):
      files_src.append(get_fname(root+source, i, j, params))
    tar_file = "{:s}/T{:05d}.tar".format(root,j)
    tar(tar_file, files_src)

    fname_dst = get_fname(source, i, j, params, fmt = "{root:s}/raw/T{frame:05d}.tar") 
    xfr = "{:s}/T{:05d}.tar {:s}/{:s}\n".format(home_end, j, archive, fname_dst)
    transfer(xfr, label="archive_raw", block=True)
    remove(tar_file) 

def recover_chest(archive, home_end, source):
  from os.path import basename
  run = basename(source)
  fname_src = "{:s}/{:s}-results/".format(archive, source)
  fname_dst = "{:s}/{:s}-results/".format(home_end, source)
  xfr = ""
  if exists(fname_src):
    xfr += "{:s} {:s} -r \n".format(fname_src, fname_dst)
  fname_src = "{:s}/{:s}.json".format(archive, source)
  fname_dst = "{:s}/{:s}.json".format(home_end, source)
  if exists(fname_src):
    xfr += "{:s} {:s} \n".format(fname_src, fname_dst)

  transfer(xfr, sync=None, label="recover_{:s}_chest".format(run), block=True)

def recover(archive, home_end, source, start, end, params):
  from os.path import basename
  run = basename(source)
  from names import get_fname
  xfr = ""
  for j in range(start, end+1):
    for i in range(int(abs(params["io_files"]))):
      fname_src = get_fname(source, i, j, params) 
      fname_dst = get_fname(source, i, j, params, fmt = "/{root:s}/raw/T{frame:05d}/{name:s}{proc:s}.f{frame:05d}") 
      xfr += "{:s}/{:s} {:s}/{:s}\n".format(archive, fname_dst, home_end, fname_src)
  transfer(xfr, label="restore_raw".format(run), block=True)
