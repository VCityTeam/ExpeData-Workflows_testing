#!/usr/bin/python3

import os.path
import sys
import shutil
import subprocess
import glob

# The CityTilers command doesn't offer a parameter flag in order to 
# specify an output directory. We thus have to collect the outputs
# and to move them to the /Output dir (that is by convention a
# docker mounted directory/volume).

command = ['python3']
kept_args = sys.argv[1:]  # The leading element is 'entrypoint.sh'

if len(kept_args) == 0:
    # This was a request for the documentation (since no arguments).
    print("CityTiler (docker) expects at least two arguments :")
    print("  1. the Tiler to be applied: either Tiler or TemporalTiler")
    print("  2. the database server configuration file")
    print("When requesting the TemporalTiler ")
    print("  3-n additionnal database server configuration files ")
    print("  n+1-2n+1 time stamps ")
    print("Exiting.")
    sys.exit()

TilerMode = kept_args[0]
if TilerMode == "Tiler":
    command.append("Tilers/CityTiler/CityTiler.py")
elif TilerMode == "TemporalTiler":
    command.append("Tilers/CityTiler/CityTemporalTiler.py")
else:
    print("Tiler argument must either be Tiler or TemporalTiler but got: ",
          TilerMode)
    print("Exiting.")
    sys.exit()
kept_args = kept_args[1:]

if TilerMode == "Tiler":
    DBConfigFile = 'Tilers/CityTiler/' + kept_args[0]
    command.append(DBConfigFile)
elif TilerMode == "TemporalTiler":
    # Deal with the database configuration files
    config_path_flag = kept_args.pop(0)
    if not config_path_flag == "--db_config_path":
        print("The second argument should have been the --db_config_path flag.")
        print("The given argument was ", config_path_flag)
        print("Exiting.")
        sys.exit()
    command.append(config_path_flag)
    # While there are arguments and while we do not encounter the --time_stamp
    # flag
    arg = kept_args.pop(0)
    while kept_args and arg != "--time_stamp":
        DBConfigFile = 'Tilers/CityTiler/' + arg
        command.append(DBConfigFile)
        arg = kept_args.pop(0)

    # Deal with the time stamps
    if not kept_args or arg != "--time_stamp":
        print("There should have been a --time_stamp flag. Exiting.")
        sys.exit()

    time_stamp_flag = arg
    command.append(time_stamp_flag)
    while kept_args:
        time_stamp = kept_args.pop(0)
        command.append(time_stamp)
    # Hardwiring the differences files
    command.append("--temporal_graph")
    difference_files = glob.glob(pathname='/Input/**/*DifferencesAsGraph.json',
                                 recursive=True)
    print('difference_files:')
    print(difference_files)
    command.extend(difference_files)
    print("Final command :", command)

print("Launching command :", command)
subprocess.call(command)

if os.path.isdir('junk_buildings'):
    shutil.copytree('junk_buildings', '/Output/BuildingsTileset')

if os.path.isdir('junk'):
    shutil.copytree('junk', '/Output/TemporalTileset')

print("Exiting ", TilerMode, " with success.")
