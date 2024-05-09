import sys
import inspect
import ast
import os

class Coverage:
    """
    A simple coverage analysis tool that hooks into the Python trace framework
    to record which lines of code are executed during the runtime of a script.
    """
    def __init__(self) -> None:
        """
        Initialises the Coverage instance with an empty trace list.
        """
        self.trace = []

    def traceit(self, frame, event, arg):
        """
        Trace function called by sys.settrace for each event.
        """
        if self.orig_trace is not None:
            self.orig_trace(frame, event, arg)
        if event == "line":
            fi = inspect.getframeinfo(frame)
            name, num = fi.function, fi.lineno
            if name != '__exit__':
                self.trace.append((name, num))
        return self.traceit

    def __enter__(self):
        """
        Sets the trace function to this instance's traceit method.
        """
        self.orig_trace = sys.gettrace()
        sys.settrace(self.traceit)
        return self

    def __exit__(self, exc_type, exc_value, tb):
        """
        Restores the original trace function upon exiting the context.
        """
        sys.settrace(self.orig_trace)

    def coverage(self):
        """
        Returns a set of tuples representing the covered lines.
        """
        return set(self.trace)

    def __repr__(self) -> str:
        """
        Provides a visual representation of the covered lines in the source code.
        """
        txt = ""
        for f_name in set(f_name for (f_name, line_number) in self.coverage()):
            try:
                fun = eval(f_name)  # Convert to code object
            except Exception as exc:
                continue
            src, start_ln = inspect.getsourcelines(fun)
            for lineno in range(start_ln, start_ln + len(src)):
                ind = ('| ' if (f_name, lineno) in self.trace else '  ')
                fmt = '%s%2d  %s' % (ind, lineno, src[lineno - start_ln].rstrip())
                txt += fmt + '\n'
        return txt

def count_statements(node):
    # this function counts statement nodes in the AST
    count = 0
    # check if the node itself is a statement
    if isinstance(node, (ast.Assign, ast.AugAssign, ast.AnnAssign, ast.For, ast.While, ast.If, ast.With, ast.Try, ast.ExceptHandler, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Return, ast.Delete, ast.Raise, ast.Assert, ast.Import, ast.ImportFrom, ast.Global, ast.Nonlocal, ast.Pass, ast.Break, ast.Continue)):
        count += 1
    # recursively count statements in the children nodes
    for child in ast.iter_child_nodes(node):
        count += count_statements(child)
    return count

def total_statements(filename):
    with open(filename, "r") as source:
        # parse the source code into an AST
        tree = ast.parse(source.read())
    # count the statements in the AST
    return count_statements(tree)


def get_path_files(path: str, filetype_filter: str = "in") -> list[str]:
    if os.path.isdir(path):
        import glob
        slash = "/" if path[-1] != '/' else ""
        glob_str = path + slash + r"*." + filetype_filter

        return glob.glob(glob_str)
    else:
        pass


def execute_script_with_input(script_path: str, input_path: str):
    with open(script_path, 'r') as file:
        script_content = file.read()

    for input_file in get_path_files(input_path):
        print(script_content)
        exec_program(script_content, input_file)


def exec_program(program: str, input_file: str):
    print(input_file)
    with open(input_file, 'r') as file:
        # Assuming the input file contains a single integer on the first line
        input_value = int(file.readline().strip())

        with Coverage() as cov:
            local_vars = {'input_value': input_value}
            global_vars = globals().copy()  # Get a copy of global environment

            # Include the Coverage instance in the execution environment
            global_vars['cov'] = cov

            # Setting the trace function to this instance's traceit method
            old_trace = sys.gettrace()  # Preserve the old trace function
            sys.settrace(cov.traceit)  # Set the new trace function

            # execute_script_with_input(python_script, file_in_dir, cov)
            exec(program, global_vars)

            print(cov.coverage())


# # understand the coverage
# with Coverage() as cov:
#     exec(open(python_script).read(), globals())

# coverage_done = cov.coverage
# print(coverage_done)

python_script = sys.argv[1]
input_dir = sys.argv[2]
execute_script_with_input(python_script, input_dir)

#print(f"Statement Coverage: {(len(cov.coverage())/total_statements(python_script))*100:.2f}%")