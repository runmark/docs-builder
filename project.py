import os
import shutil
import sys


class Project:
    def __init__(self, base_dir):
        self.src_dir = os.path.join(base_dir, "src")
        self.cache_dir = os.path.join(base_dir, "cache")
        self.build_dir = os.path.join(base_dir, "build")
        self.targets = ("build", "clean", "rebuild")

    def usage(self):
        entry = os.path.basename(sys.argv[0])
        print("Usage:")
        for target in self.targets:
            method = getattr(self, target)
            print(f"{entry} {method.__name__} - {method.__doc__}")

    def run(self, target_name):
        method = getattr(self, target_name)
        method()

    def build(self):
        pass

    def clean(self):
        shutil.rmtree(self.build_dir, ignore_errors=True)
        shutil.rmtree(self.cache_dir, ignore_errors=True)
        print("Cleaned up.")

    def rebuild(self):
        self.clean()
        self.build()
