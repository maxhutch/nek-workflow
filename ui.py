"""
User interfaces for the nek-workflow script

Currently, there is only a command line interface
"""


def command_line_ui():
  """
  Command line interface for nek-workflow

  Uses python's ArgumentParser to read the command line and then creates
  shortcuts for common argument combinations
  """

  # grab defaults from config files
  from os.path import exists, expanduser, join
  import json
  defaults = {
               'start' : 1,
               'nodes' : 1,
               'archive' : False,
               'upload'  : False,
               'sync'    : True,
               'process' : False,
               'analysis' : "RTI", 
               'arch_end' : "alcf#dtn_hpss/~/pub/",
               'outp_end' : "maxhutch#alpha-admin/pub/",
               'home_end' : "maxhutch#edoras/home/maxhutch/science/RTI/",
               'foo'      : "bar"
             }
  if exists(join(expanduser("~"), ".nek-workflow.json")):
    with open(join(expanduser("~"), ".nek-workflow.json")) as f:
      defaults.update(json.load(f))

  # Define arguments
  from argparse import ArgumentParser
  p = ArgumentParser()
  p.add_argument("name",                 
                 help="Name and path of Nek output files")
  p.add_argument("-a", "--archive_end", 
                 help="Archive endpoint", dest="arch_end")
  p.add_argument("-m", "--home_end",
                 help="Home endpoint")
  p.add_argument("-o", "--output_end", 
                 help="Output endpoint", dest="outp_end")
  p.add_argument("-f",  "--frame", type=int, 
                 help="[Starting] Frame number")
  p.add_argument("-e",  "--frame_end", type=int, default=-1,   
                 help="Ending frame number")
  p.add_argument("--analysis", help="Anaysis package to use for post-processing")
  p.add_argument("--sync",       action="store_true",   help="Sync params and chest", dest="sync")
  p.add_argument("--no-sync",    action="store_false",  help="Sync params and chest", dest="sync")
  p.add_argument("--process",    action="store_true",   help="Process the frames", dest="process")
  p.add_argument("--no-process", action="store_false",  help="Process the frames", dest="process")
  p.add_argument("--archive",    action="store_true",   help="Archive raw",   dest="archive")
  p.add_argument("--no-archive", action="store_false",  help="Archive raw",   dest="archive")
  p.add_argument("--upload",     action="store_true",   help="Upload results", dest="upload")
  p.add_argument("--no-upload",  action="store_false",  help="Upload results", dest="upload")
  p.add_argument("-n", "--nodes", type=int,
                 help="Number of nodes to run on")
  p.set_defaults(**defaults)

  """ 
  p.add_argument("-s",  "--slice", action="store_true",
                 help="Display slice")
  p.add_argument("-c",  "--contour", action="store_true",     
                 help="Display contour")
  p.add_argument("-n",  "--ninterp", type=float, default = 1.,
                 help="Interpolating order")
  p.add_argument("-z",  "--mixing_zone", action="store_true",
                 help="Compute mixing zone width")
  p.add_argument("-m",  "--mixing_cdf", action="store_true",
                 help="Plot CDF of box temps")
  p.add_argument("-F",  "--Fourier", action="store_true",
                 help="Plot Fourier spectrum in x-y")
  p.add_argument("-b",  "--boxes", action="store_true",
                 help="Compute box covering numbers")
  p.add_argument("-nb", "--block", type=int, default=65536,
                 help="Number of elements to process at a time")
  p.add_argument("-nt", "--thread", type=int, default=1,
                 help="Number of threads to spawn")
  p.add_argument("-d",  "--display", action="store_true", default=False,  
                 help="Display plots with X")
  p.add_argument("-p",  "--parallel", action="store_true", default=False,
                 help="Use parallel map (IPython)")
  p.add_argument(       "--series", action="store_true", default=False,
                 help="Apply time-series analyses")
  p.add_argument("--mapreduce", default=defaults["mapreduce"],
                 help="Module containing Map and Reduce implementations")
  p.add_argument("--post", default=defaults["post"],
                 help="Module containing post_frame and post_series")
  p.add_argument("-v",  "--verbose", action="store_true", default=False,
                 help="Should I be really verbose, that is: wordy?")
  """
 
  # Load the arguments
  args = p.parse_args()
  if args.frame_end == -1:
      args.frame_end = args.frame
  args.root = "/" + args.home_end.partition("/")[2]
  
  return args
