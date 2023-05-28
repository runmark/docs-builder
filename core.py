import os
import typing


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

    def execute_task(self, task_list: list, task):
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


class AstNode:
    def __init__(self, name, data=None):
        self.name = name
        self.data = data
        self.children = None

    def append_child(self, child):
        self.children = self.children or []
        self.children.append(child)

    def ast_string(self, depth: int):
        indent = " " * (depth * 2)
        result = f"{indent}{self.name}"
        if self.data:
            result += f"({self.data})"
        return result

    def iter(self, depth: int):
        yield depth, self
        for child in self.children or []:
            for descendant in child.iter(depth + 1):
                yield descendant
            # TODO why `yield child.iter(depth + 1)` is wrong?

    def header_level(self):
        header_marks = ("h1", "h2", "h3", "h4", "h5", "h6")
        if self.name in header_marks:
            return int(self.name[1:])
        return 0


class AstDoc(AstNode):
    def __init__(self, data):
        super().__init__("doc", data)

    def dump_ast(self):
        return "\n".join([node.ast_string(depth) for depth, node in self.iter(depth=0)])

    def title(self) -> str:
        def find_first(items, predicate):
            return next((x for x in items if predicate(x)), None)

        h1 = find_first(self.iter(0), lambda x: x[1].name == "h1")
        return h1[1]._data if h1 is not None else "Untitled"

    def headers(self) -> typing.List:
        return [node for _, node in self.iter(0) if node.header_level() > 0]


class Code:
    def __init__(self, name):
        self.name = name
        self.title = None
        self.html = []
        self.toctree = []
        self.dependencies = set()

    def add_toctree(self, *args):
        self.toctree.extend(args)


if __name__ == "__main__":
    root = AstDoc("install")
    root.append_child(AstNode("h1", "Installation"))

    print(root.dump_ast())
