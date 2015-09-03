#!/home/maxhutch/anaconda3/bin/python

from ui import command_line_ui
args = command_line_ui()

from os.path import dirname, basename
experiment = dirname(args.name)
run = basename(args.name)

if args.sync:
  from globus import recover_chest
  recover_chest(args.arch_end, args.home_end, args.name)

import json
with open("{:s}.json".format(args.root+args.name), "r") as f:
  params = json.load(f)

from names import get_fname
from os.path import exists
fname = get_fname(args.root+args.name, 0, args.frame_end, params)
new_source = not exists(fname)

if not new_source:
 if args.archive:
  print("Found {:s}, archiving".format(fname))
  from globus import archive
  archive(args.arch_end, args.home_end, args.root, args.name, args.frame, args.frame_end, params)
else:
 if args.process:
  print("Not Found {:s}, recovering".format(fname))
  from globus import recover
  recover(args.arch_end, args.home_end, args.name, args.frame, args.frame_end, params)

# queue processing job
if args.process and args.nodes != 0:
  from analyze import process
  process(args.root+args.name, args.frame, args.frame_end, args.nodes, args.analysis)

#from analyze import visualize
#from analyze import visualize
#visualize(args.root+args.name, args.frame, args.frame_end, args.nodes)

# setup upload
from globus import upload_results
if args.upload:
  upload_results(args.home_end, args.outp_end, args.name)

# setup archive
if args.upload:
  upload_results(args.home_end, args.arch_end, args.name)

