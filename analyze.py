
"""
def process(source, start, end, nodes):
  from subprocess import call
  with open("tmp.stdout", "w") as f:
    call(args=["qsub", "-t 60", "-n {:d}".format(nodes), "/projects/alpha-nek/pp.sh", source, "{:d} {:d}".format(start, end)], stdout=f)
  # wait for processing job
  with open("tmp.stdout", "r") as f:
    jobid = int(f.readline())
  print("Waiting for job {:d}".format(jobid))
  call(args=["cqwait", "{:d}".format(jobid)])
"""

def process(source, start, end, nodes):
  from subprocess import call
  call(args=["/home/maxhutch/src/nek-analyze/load.py", source, "-f {:d}".format(start), "-e {:d}".format(end)])

