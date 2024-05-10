import sys
import trace
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


# def execute_script_with_input(script_path, input_path):
#     # Step 1: Read the script content
#     with open(script_path, 'r') as file:
#         script_content = file.read()

#     # Step 3: Read the input content
#     with open(input_path, 'r') as file:
#         # Assuming the input file contains a single integer on the first line
#         input_value = int(file.readline().strip())

#     # Step 2: Prepare the local environment
#     # Assume `script.py` contains a function call like `factorial(input_value)`
#     # We will replace `input_value` in the script with the actual input
#     local_vars = {}
#     global_vars = {}

#     # Injecting the input value into the script
#     # This assumes that the script is expecting a variable named 'input_value'
#     local_vars['input_value'] = input_value

#     # Step 4: Execute the script
#     exec(script_content, global_vars, local_vars)



# def execute_script_with_input(script_path, input_path, coverage_instance):
#     # Step 1: Read the script content
#     with open(script_path, 'r') as file:
#         script_content = file.read()

#     # Step 3: Read the input content
#     with open(input_path, 'r') as file:
#         input_value = int(file.readline().strip())  # Assuming the input is an integer

#     # Prepare the local and global environment
#     local_vars = {'input_value': input_value}
#     global_vars = globals().copy()  # Get a copy of global environment

#     # Include the Coverage instance in the execution environment
#     global_vars['cov'] = coverage_instance

#     # Setting the trace function to this instance's traceit method
#     old_trace = sys.gettrace()  # Preserve the old trace function
#     sys.settrace(cov.traceit)  # Set the new trace function

#     try:
#         # Step 4: Execute the script
#         exec(script_content, global_vars, local_vars)
#     finally:
#         # Restore the original trace function after execution
#         sys.settrace(old_trace)


# extract tokens from command line
python_script = sys.argv[1]
input_dir = sys.argv[2]

# extracting files from dir
files = os.listdir(input_dir)
file_in_dir = os.path.join(input_dir, files[0])
total_statement = total_statements(file_in_dir)

# # understand the coverage
# with Coverage() as cov:
#     # execute_script_with_input(python_script, file_in_dir, cov)
#     exec(open(python_script).read(), globals())

# coverage_done = cov.coverage
# print(coverage_done)

import factorial
with Coverage() as cov:
    factorial.factorial(3)
print(cov.coverage())
print(len(cov.coverage()))
print(total_statements(python_script))

print(f"Statement Coverage: {(len(cov.coverage())/total_statements(python_script))*100:.2f}%")