import os
import shutil
import sys

from core import BuildContext, Scan


class Project:
    """Manage CLI interface on project"""

    def __init__(self, base_dir):
        self.ctx = BuildContext(base_dir)
        self.targets = ("build", "clean", "rebuild")

    def usage(self):
        entry = os.path.basename(sys.argv[0])
        print("Usage:")
        for target in self.targets:
            method = getattr(self, target)
            print(f"{entry} {method.__name__} - {method.__doc__}")

    def run(self, target_name):
        """Run specified target"""
        assert target_name in self.targets, f"Unsupported target: {target_name}"
        method = getattr(self, target_name)
        method()

    def build(self):
        """Build project"""
        """
        1. get all tasks
        2. execute_all_tasks()
        """
        self.ctx.execute_task(None, Scan())
        self.ctx.execute_tasks(self.ctx.compile_tasks)
        self.ctx.execute_tasks(self.ctx.link_tasks)

    def clean(self):
        """Clean intermediate file"""
        shutil.rmtree(self.build_dir, ignore_errors=True)
        shutil.rmtree(self.cache_dir, ignore_errors=True)
        print("Cleaned up.")

    def rebuild(self):
        "Force rebuild"
        self.clean()
        self.build()
