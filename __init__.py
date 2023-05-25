import os
import sys

from project import Project


def main():
    base_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), "./.docs"))
    proj = Project(base_dir)

    argv = sys.argv
    if len(argv) != 2:
        proj.usage()
        sys.exit(0)

    target_name = argv[1]
    proj.run(target_name)


if __name__ == "__main__":
    main()
