import os
import shutil
import sys


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


class BuildContext:
    def __init__(self, base_dir):
        self.src_dir = os.path.join(base_dir, "src")
        self.cache_dir = os.path.join(base_dir, "cache")
        self.build_dir = os.path.join(base_dir, "build")
        self.compile_tasks = []
        self.link_tasks = []
        self.executed_tasks = []

    def add_compile_task(self, task):
        self.compile_tasks.append(task)

    def add_link_task(self, task):
        self.link_tasks.append(task)

    def execute_task(self, task_list: list, task: Task):
        task.exec(self)
        if task_list:
            task_list.remove(task)
        self.executed_tasks.append(task)

    def execute_tasks(self, task_list):
        while task_list:
            for task in task_list[:]:
                self.execute_task(task_list, task)


class Task:
    def exec(self, ctx: BuildContext):
        self.ctx = ctx
        self.run()

    def run(self):
        raise NotImplementedError()


class Scan(Task):
    def __str__(self):
        return "scan"

    def run(self):
        for filename in os.listdir(self.ctx.src_dir):
            if filename.endswith(".rst"):
                self.ctx.add_compile_task(Parse(filename))
                self.ctx.add_link_task(Link(filename))


class Parse(Task):
    """rst file -> ast model"""

    def __init__(self, filename):
        self._filename = filename

    def __str__(self):
        return f"parse({self._filename})"

    def run(self):
        self.ctx.add_compile_task(Transform(self._filename))


class Transform(Task):
    """ast model -> code model"""

    def __init__(self, filename):
        self._filename = filename

    def __str__(self):
        return f"transform({self._filename})"

    def run(self):
        self.ctx.add_compile_task(WriteCache(self._filename))


class WriteCache(Task):
    """write code to cache"""

    def __init__(self, filename):
        self._filename = filename

    def __str__(self):
        return f"writecache({self._filename})"

    def run(self):
        pass


class Link(Task):
    """generate final output"""

    def __init__(self, filename):
        self._filename = filename

    def __str__(self):
        return f"link({self._filename})"

    def run(self):
        pass
