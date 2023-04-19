import sys
from hera._version import version

def hera_print_version():
  print("Installed Hera version: ", version)

def hera_check_version(version_to_check):
  if version_to_check == version:
    return True
  else:
    print("Unsuported Hera version:", version_to_check)
    hera_print_version()
    sys.exit()


