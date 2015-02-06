#!/usr/bin/env python3

#!/home/maxhutch/anaconda3/bin/python

arch_end = "acherry#hpss_test/~/pub/"
outp_end = "maxhutch#alpha-admin/pub/"
home_end = "maxhutch#edoras/home/maxhutch/science/RTI/"
home = "/home/maxhutch/science/RTI/"

#source = "fingers/hemisphere/hemi_finger"
#source = "fingers/hemisphere_wide/hemi_wide"
source = "fingers/cone/cone_finger"

from os.path import dirname, basename
experiment = dirname(source)
run = basename(source)
start = 4
end   = 4
nodes = 1

enable_archive = False
enable_upload = True

import json
with open("{:s}.json".format(home+source), "r") as f:
  params = json.load(f)

from names import get_fname
fname = get_fname(home+source, 0, end, params)
from os.path import exists
new_source = exists(fname)

if new_source:
 if enable_archive:
  print("Found {:s}, archiving".format(fname))
  from globus import archive
  archive(arch_end, home_end, source, start, end, params)
else:
  print("Not Found {:s}, recovering".format(fname))
  from globus import recover
  recover(arch_end, home_end, source, start, end, params)

# queue processing job
if nodes != 0:
  from analyze import process
  process(home+source, start, end, nodes)

# setup upload
from globus import upload_results
if enable_upload:
  upload_results(home_end, outp_end, source)

# setup archive
if enable_upload:
  upload_results(home_end, arch_end, source)

