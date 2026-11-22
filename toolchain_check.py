"""Checks that this run's commands ran in the team's toolchain image (wardby #599 test)."""
import getpass
import sys

import teamext  # only the toolchain image has this C extension

print("python", sys.version.split()[0], sys.executable)
print("teamext", teamext.answer())
print("user", getpass.getuser())
