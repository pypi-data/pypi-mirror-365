"""
Utilities
"""

import os
import sys
import re
import subprocess
import psutil
import argparse

###############################################################################
def expect(condition, error_msg, exc_type=RuntimeError, error_prefix="ERROR:"):
###############################################################################
    """
    Similar to assert except doesn't generate an ugly stacktrace. Useful for
    checking user error, not programming error.

    >>> expect(True, "error1")
    >>> expect(False, "error2")
    Traceback (most recent call last):
        ...
    SystemExit: ERROR: error2
    """
    if not condition:
        msg = error_prefix + " " + error_msg
        raise exc_type(msg)

###############################################################################
def run_cmd(cmd, from_dir=None, verbose=None, dry_run=False, env_setup=None,
            arg_stdout=subprocess.PIPE, arg_stderr=subprocess.PIPE,
            combine_output=False):
###############################################################################
    """
    Wrapper around subprocess to make it much more convenient to run shell commands

    >>> run_cmd('ls file_i_hope_doesnt_exist')[0] != 0
    True
    """

    # If the cmd needs some env setup, the user can pass the setup string, which will be
    # executed right before the cmd
    if env_setup:
        cmd = f"{env_setup} && {cmd}"

    arg_stderr = subprocess.STDOUT if combine_output else arg_stderr

    from_dir = str(from_dir) if from_dir else from_dir

    if verbose:
        print(f"RUN: {cmd}\nFROM: {os.getcwd() if from_dir is None else from_dir}")

    if dry_run:
        return 0, "", ""

    proc = subprocess.Popen(cmd,
                            shell=True,
                            stdout=arg_stdout,
                            stderr=arg_stderr,
                            stdin=None,
                            text=True, # automatically decode output bytes to string
                            cwd=from_dir)

    output, errput = proc.communicate(None)
    if output is not None:
        output = output.strip()
    if errput is not None:
        errput = errput.strip()
    proc.wait()

    return proc.returncode, output, errput

###############################################################################
def run_cmd_no_fail(cmd, from_dir=None, verbose=None, dry_run=False,env_setup=None,
                    arg_stdout=subprocess.PIPE, arg_stderr=subprocess.PIPE,
                    combine_output=False):
###############################################################################
    """
    Wrapper around subprocess to make it much more convenient to run shell commands.
    Expects command to work. Just returns output string.
    """
    stat, output, errput = run_cmd(cmd, from_dir=from_dir,verbose=verbose,dry_run=dry_run,env_setup=env_setup,
                                   arg_stdout=arg_stdout,arg_stderr=arg_stderr,
                                   combine_output=combine_output)
    expect (stat==0,
            "Command failed unexpectedly"
            f"  - command: {cmd}"
            f"  - error: {errput if errput else output}"
            f"  - from dir: {from_dir or os.getcwd()}")

    return output

###############################################################################
def check_minimum_python_version(major, minor):
###############################################################################
    """
    Check your python version.

    >>> check_minimum_python_version(sys.version_info[0], sys.version_info[1])
    >>>
    """
    msg = "Python " + str(major) + ", minor version " + str(minor) + " is required, you have " + str(sys.version_info[0]) + "." + str(sys.version_info[1])
    expect(sys.version_info[0] > major or
           (sys.version_info[0] == major and sys.version_info[1] >= minor), msg)

###############################################################################
class GoodFormatter(
    argparse.ArgumentDefaultsHelpFormatter,
    argparse.RawDescriptionHelpFormatter
):
###############################################################################
    """
    We want argument default info to be added but we also want to
    preserve formatting in the description string.
    """

###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################
def logical_cores_per_physical_core():
###############################################################################
    return psutil.cpu_count() // psutil.cpu_count(logical=False)

###############################################################################
def get_cpu_ids_from_slurm_env_var():
###############################################################################
    """
    Parse the SLURM_CPU_BIND_LIST, and use the hexadecimal value to determine
    which CPUs on this node are assigned to the job
    NOTE: user should check that the var is set BEFORE calling this function
    """

    cpu_bind_list = os.getenv('SLURM_CPU_BIND_LIST')

    expect (cpu_bind_list is not None,
            "SLURM_CPU_BIND_LIST environment variable is not set. Check, before calling this function")

    # Remove the '0x' prefix and convert to an integer
    mask_int = int(cpu_bind_list, 16)

    # Generate the list of CPU IDs
    cpu_ids = []
    for i in range(mask_int.bit_length()):  # Check each bit position
        if mask_int & (1 << i):  # Check if the i-th bit is set
            cpu_ids.append(i)

    return cpu_ids

###############################################################################
def get_available_cpu_count(logical=True):
###############################################################################
    """
    Get number of CPUs available to this process and its children. logical=True
    will include hyperthreads, logical=False will return only physical cores
    """
    if 'SLURM_CPU_BIND_LIST' in os.environ:
        cpu_count = len(get_cpu_ids_from_slurm_env_var())
    else:
        cpu_count = len(psutil.Process().cpu_affinity())

    if not logical:
        hyperthread_ratio = logical_cores_per_physical_core()
        return int(cpu_count / hyperthread_ratio)
    else:
        return cpu_count

###############################################################################
class SharedArea(object):
###############################################################################
    """
    Enable 0002 umask within this manager
    """

    def __init__(self, new_perms=0o002):
        self._orig_umask = None
        self._new_perms  = new_perms

    def __enter__(self):
        self._orig_umask = os.umask(self._new_perms)

    def __exit__(self, *_):
        os.umask(self._orig_umask)

###############################################################################
def evaluate_py_expressions(tgt_obj, src_obj_dict):
###############################################################################

    # Only user-defined types have the __dict__ attribute
    if hasattr(tgt_obj,'__dict__'):
        for name,val in vars(tgt_obj).items():
            setattr(tgt_obj,name,evaluate_py_expressions(val,src_obj_dict))

    elif isinstance(tgt_obj,dict):
        for name,val in tgt_obj.items():
            tgt_obj[name] = evaluate_py_expressions(val,src_obj_dict)

    elif isinstance(tgt_obj,list):
        for i,val in enumerate(tgt_obj):
            tgt_obj[i] = evaluate_py_expressions(val,src_obj_dict)

    elif isinstance(tgt_obj,str):

        # First, extract content of ${...} (if any)
        beg = tgt_obj.find("${")
        end = tgt_obj.rfind("}")

        if beg==-1:
            expect (end==-1, f"Badly formatted expression '{tgt_obj}'.")
            return tgt_obj

        expect (end>beg, f"Badly formatted expression '{tgt_obj}'.")

        expression = tgt_obj[beg+2:end]

        pattern = r'\b(\w+)\.(\w+)\b'
        matches = re.findall(pattern,expression)
        for obj_name, att_name in matches:
            expect (obj_name in src_obj_dict.keys(),
                    f"Invalid expression '{obj_name}.{att_name}': '{obj_name}' must be in {src_obj_dict.keys()}")

            expression = expression.replace(f'{obj_name}.{att_name}',f"src_obj_dict['{obj_name}'].{att_name}")

        expect (safe_expression(expression),
                f"Cannot evaluate expression '{tgt_obj}'. A dangerous pattern was detected in the expression")

        try:
            result = eval(expression)
            tgt_obj = tgt_obj[:beg] + str(result) + tgt_obj[end+1:]
        except AttributeError:
            print (f"Could not evaluate expression {tgt_obj}.\n")
            raise

    return tgt_obj

#########################################################
def safe_expression(expression):
#########################################################

    # List of dangerous patterns
    dangerous_patterns = [
        r'\bimport\b',           # Import statements
        r'\bexec\b',             # Exec statements
        r'\beval\b',             # Eval statements
        r'\bos\.system\b',       # OS system calls
        r'\bsubprocess\.run\b',  # Subprocess calls
        r'\bglobals\b',          # Globals access
        r'\blocals\b',           # Locals access
        r';',                    # Multiple statements
        r'\bopen\b',             # File access
        r'\bos\.getenv\b',       # Environment variable access
        r'\b__\w+__\b'           # Catch all for any double underscore attributes
    ]

    # Check for any dangerous patterns
    for pattern in dangerous_patterns:
        if re.search(pattern, expression):
            return False  # Unsafe expression
    
    return True  # Safe expression

###############################################################################
def evaluate_bash_commands(tgt_obj,env_setup=None):
###############################################################################

    # Only user-defined types have the __dict__ attribute
    if hasattr(tgt_obj,'__dict__'):
        for name,val in vars(tgt_obj).items():
            setattr(tgt_obj,name,evaluate_bash_commands(val,env_setup))

    elif isinstance(tgt_obj,dict):
        for name,val in tgt_obj.items():
            tgt_obj[name] = evaluate_bash_commands(val,env_setup)

    elif isinstance(tgt_obj,list):
        for i,val in enumerate(tgt_obj):
            tgt_obj[i] = evaluate_bash_commands(val,env_setup)

    elif isinstance(tgt_obj,str):
        pattern = r'\$\((.*?)\)'

        matches = re.findall(pattern,tgt_obj)
        for cmd in matches:
            stat,out,err = run_cmd(cmd,env_setup=env_setup)
            expect (stat==0,
                    "Could not evaluate the command.\n"
                    f"  - original string: {tgt_obj}\n"
                    f"  - command: {cmd}\n"
                    f"  - error: {err}\n")

            tgt_obj = tgt_obj.replace(f"$({cmd})",out)

    return tgt_obj

###############################################################################
def str_to_bool(s, var_name):
###############################################################################
    if s=="True":
        return True
    elif s=="False":
        return False
    else:
        raise ValueError(f"Invalid value '{s}' for '{var_name}'.\n"
                          "Should be either 'True' or 'False'")

###############################################################################
def is_git_repo(repo=None):
###############################################################################
    """
    Check that the folder is indeed a git repo
    """

    stat, _, _ = run_cmd("git rev-parse --is-inside-work-tree",from_dir=repo)

    return stat==0

###############################################################################
def get_current_ref(repo=None):
###############################################################################
    """
    Return the name of the current branch for a repository
    If in detached HEAD state, returns None
    """

    return run_cmd_no_fail("git rev-parse --abbrev-ref HEAD",from_dir=repo)

###############################################################################
def get_current_sha(short=False,repo=None):
###############################################################################
    """
    Return the sha1 of the current HEAD commit

    >>> get_current_commit() is not None
    True
    """

    return run_cmd_no_fail(f"git rev-parse {'--short' if short else ''} HEAD",from_dir=repo)
