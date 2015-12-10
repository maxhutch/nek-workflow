
cobalt_template =  \
"""#!/bin/sh
#COBALT -M maxhutch@gmail.com


NODES=`cat $COBALT_NODEFILE | wc -l`
PROCS=$((NODES * 1))

cat $COBALT_NODEFILE
mpirun -f $COBALT_NODEFILE -n ${{PROCS}} --prepend-rank /bin/uname -n
set -x

cd /home/maxhutch/nek-analyze

/home/maxhutch/anaconda3/bin/ipcontroller --profile=mpi --ip='*' &
sleep 10
mpirun -f $COBALT_NODEFILE --n=${{PROCS}} /home/maxhutch/anaconda3/bin/ipengine --profile=mpi  &
sleep 10

#./load.py $1 -f $2 -e $3 -nt 16 -nb 256 --mapreduce=RTI_new.MapReduce --post=RTI_new.single_post 
./load.py $1 -f $2 -e $3 -nt 24 -nb 1024 --mapreduce={analysis:s}.MapReduce --post={analysis:s}.single_post  --parallel  --single_pos --figs=$(dirname $1)/img/
#./load.py $1 -f $2 -e $3 -nt 12 -nb 256 --mapreduce={analysis:s}.MapReduce --post={analysis:s}.single_post  --parallel 
#./load.py $1 -f $2 -e $3 -nt 16 -nb 256 --mapreduce=RTI.MapReduce --post=RTI.single_post  --parallel --params=/projects/alpha-nek/${{1}}.json --chest=/projects/alpha-nek/${{1}}-resultss --figs=/projects/alpha-nek/${{1}}-figs
sleep 5
kill %2
sleep 5
kill %1
sleep 5
exit
"""

def process(source, start, end, nodes, analysis = "RTI"):
  from subprocess import check_output, call
  from os import chmod
  import stat
  with open("tmp.job", "w") as f:
    f.write(cobalt_template.format(analysis=analysis))
  chmod("tmp.job", stat.S_IXUSR | stat.S_IWUSR | stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)
  stdout = check_output(args=["qsub", "-t", "15", "-A", "alpha-nek", 
                              #"--queue=pubnet", 
                              "-n", "{:d}".format(nodes), "tmp.job", source, "{:d}".format(start),  "{:d}".format(end)])
  # wait for processing job
  jobid = int(stdout)
  print("Waiting for job {:d}".format(jobid))
  call(args=["cqwait", "{:d}".format(jobid)])

"""
def process(source, start, end, nodes, analysis = "RTI"):
  from subprocess import call
  opts = ["--thread=8", "-v", "--mapreduce={:s}.MapReduce".format(analysis), "--post={:s}.single_post".format(analysis), "--single_pos"]
  #opts = ["--thread=1", "-v"]
  call(args=["/home/maxhutch/src/nek-analyze/load.py", source, "-f {:d}".format(start), "-e {:d}".format(end)] + opts)

def visualize(source, start, end, nodes):
  from subprocess import call
  opts = []
  call(args=["/home/maxhutch/src/nek-analyze/visualize.py", source, "-f {:d}".format(start), "-e {:d}".format(end)] + opts)
"""
