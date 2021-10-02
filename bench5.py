#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = "Tommaso Marinelli"
__email__  = "tommarin@ucm.es"

# Select the benchmark suite to use
# (allowed values: spec2006, spec2017)
benchsuite = "spec2017"

# Simple log printing function
def log(string):
    print("[bench5] %s" % string)
    return

import argparse
from datetime import datetime, timedelta
import io
import os
import platform
import shlex
import shutil
import sys
import time
import threading
import uuid

python_version = float(".".join(map(str, sys.version_info[:2])))
if python_version < 3.2:
    import subprocess32 as subprocess
else:
    import subprocess

# Local modules
from simclass import BBVGeneration, SPGeneration, CptGeneration, \
    CptSimulation, TraceGeneration, TraceReplay, FullSimulation, MemProfile
import simparams
try:
    if benchsuite == "spec2006":
        import benchsuites.spec2006 as benchlist
    elif benchsuite == "spec2017":
        import benchsuites.spec2017 as benchlist
    else:
        raise ImportError("invalid benchmark suite: %s" % benchsuite)
except ImportError as e:
    log("error: %s" % e)
    exit(1)

valid_short_uuid = False
while not valid_short_uuid:
    short_uuid = str(uuid.uuid4())[-6:]
    if short_uuid[0].isalpha():
        valid_short_uuid = True
script_path = os.path.dirname(os.path.realpath(sys.argv[0]))
uppath = lambda _path, n: os.sep.join(_path.split(os.sep)[:-n])

# List of warnings due to missing resources
warnings = []
# Total number of spawned processes
count_pids = 0
# Total number of terminated processes (succeeded and failed)
count_term = 0
# Lock for processes list/counter update
lock_pids = threading.Lock()
# Lock for failed processes dict/counter update
lock_fail = threading.Lock()
# List of all the running subprocesses
sp_pids = []
# Dict which contains pending failed subprocesses with failure cause
sp_fail = {}
# Shutdown flag
shutdown = False


# Path type (with tilde expansion)
def path(s):
    return os.path.expanduser(s)


# Print a simple progress bar
# Original source: https://stackoverflow.com/a/45868571
def progress_bar(total, progress, prefix = ""):
    if prefix:
        prefix += " "
    bar_length, status = 40, ""
    progress = float(progress) / float(total)
    if progress >= 1.:
        progress, status = 1, "\r\n"
    block = int(round(bar_length * progress))
    text = "\r{}[{}] {:.0f}% {}".format(prefix,
        "#" * block + "-" * (bar_length - block), round(progress * 100, 0),
        status)
    sys.stdout.write(text)
    sys.stdout.flush()


# Reconstruct string from split command
def cmd_join(split_cmd):
    cmd = ""
    for param in split_cmd:
        if ' ' in param:
            cmd += "\'%s\' " % param
        else:
            cmd += "%s " % param
    return cmd


# Check if an executable is present in the current PATH
def cmd_exists(cmd):
    return any(
        os.access(os.path.join(path, cmd), os.X_OK)
        for path in os.environ["PATH"].split(os.pathsep)
    )


# Check for the presence of specific tools or paths in the system
def check_prerequisites(args, valgrind, simpoint, gem5):
    exe_path = ""

    if args.sge:
        sge_template = os.path.join(script_path, "sge.tpl")
        if not os.path.isfile(sge_template):
            log("error: Unable to find sge template in script directory")
            exit(2)

    if valgrind:
        # Check if valgrind exists in current system
        if not cmd_exists("valgrind"):
            log("error: valgrind utility not found in env path")
            exit(2)

        # Check if the CPU architecture matches the execution platform
        machine = platform.machine()
        archs_aarch64 = ("aarch64_be", "aarch64", "armv8b", "armv8l", "arm64")
        archs_arm = ("arm", "armv7b", "armv7l", "armhf")
        archs_x86_64 = ("x86_64", "x64", "amd64")
        if ((args.arch == "aarch64" and machine not in archs_aarch64) or
            (args.arch == "armhf" and machine not in archs_arm) or
            (args.arch == "x86-64" and machine not in archs_x86_64)):
            log("error: architecture mismatch")
            exit(3)

    if simpoint:
        # Check if simpoint tool exists in specified path
        simpoint_exe = os.path.join(args.sp_dir, "bin", "simpoint")
        if not os.path.isfile(simpoint_exe):
            log("error: simpoint executable not found in " + args.sp_dir)
            exit(2)
        exe_path = simpoint_exe

    if gem5:
        # Check if gem5 exists in specified path
        gem5_build = "X86" if args.arch == "x86-64" else "ARM"
        gem5_exe_dir  = os.path.join(args.gem5_dir, "build", gem5_build)
        gem5_exe_name = "gem5.opt" if args.debug else "gem5.fast"
        gem5_exe_path = os.path.join(gem5_exe_dir, gem5_exe_name)
        if not os.path.isfile(gem5_exe_path):
            log("error: " + gem5_exe_name + " executable not found in " +
                  gem5_exe_dir)
            exit(2)
        exe_path = gem5_exe_path

    return exe_path


# Get general benchmark parameters
def get_params(args, b_name):
    spec_b_folder = os.path.join(args.spec_dir, b_name)
    b_spl = b_name.split('.')

    # Check if the benchmark folder is present in SPEC path
    assert os.path.isdir(spec_b_folder), "%s not found in %s" % (
        b_name, args.spec_dir)

    # Check if the executable exists
    if b_name in benchlist.exe_name:
        b_exe_name = benchlist.exe_name[b_name] + "_base." + args.arch
    else:
        b_exe_name = b_spl[1] + "_base." + args.arch
    b_exe_folder = os.path.join(args.spec_dir, b_name, "exe")
    b_exe_path = os.path.join(b_exe_folder, b_exe_name)
    assert os.path.isfile(b_exe_path), "executable not found in %s" % (
        b_exe_folder)

    b_preproc  = benchlist.preprocessing.get(b_name, "")
    # Use 2GB by default
    b_mem_size = "2GB"
    set_mem_size = benchlist.mem_size.get(args.set[0], "")
    if set_mem_size and set_mem_size.get(b_name, ""):
        b_mem_size = set_mem_size[b_name]
    return b_exe_name, b_preproc, b_mem_size


# Get benchmark subset parameters
def get_ss_params(b_name, b_set):
    benchlist_subset = benchlist.subset.get(b_set)
    benchlist_params = benchlist.params.get(b_set)
    benchlist_input  = benchlist.input.get(b_set)
    if any(v is None for v in
        (benchlist_subset, benchlist_params, benchlist_input)):
        log("error: couldn't find benchmark set")
        exit(1)
    arguments = []
    b_params  = benchlist_params.get(b_name, "")
    b_input   = benchlist_input.get(b_name, "")
    if b_name in benchlist_subset:
        for i, ss in enumerate(benchlist_subset[b_name]):
            b_subset = ss + "_" + b_set
            arguments.append((b_subset,
                b_params[i] if isinstance(b_params, tuple) else "",
                b_input[i]  if isinstance(b_input, tuple) else ""))
    else:
        b_subset = b_set
        arguments.append((b_subset, b_params, b_input))
    return arguments


# Get host system memory utilization from /proc/meminfo
def get_host_mem():
    try:
        with open(os.path.join("/proc", "meminfo"), "r") as pidfile:
            stat = pidfile.readline()
            total = int(stat.split()[1])
            pidfile.readline()
            stat = pidfile.readline()
            avail = int(stat.split()[1])
            return(total, avail)
    except IOError:
        log("error: unable to read from /proc")
        exit(3)
    return 0


# Get process Resident Set Size (RSS) from /proc/[pid]/stat
def get_rss(pid):
    try:
        with open(os.path.join("/proc", str(pid), "stat"), 'r') as pidfile:
            stat = pidfile.readline()
            rss = int(stat.split(' ')[23])
            return rss
    except IOError:
        log("error: unable to read from /proc")
        exit(3)
    return 0


# Add a process to the failed list
def fail(pid, cause):
    global sp_fail

    with lock_fail:
        sp_fail[pid] = cause
    return


# Watchdog which prevents host system memory saturation or process stall
def watchdog(limit_time):
    # Memory monitoring
    total, avail = get_host_mem()
    if float(avail) / float(total) < 0.1 and any(sp_pids):
        # Find the child which is using more memory
        largest_mem = [0, 0]
        for pid in sp_pids:
            # Avoid re-targeting a dead child
            proc_dir = os.path.join("/proc", str(pid))
            if pid not in sp_fail and os.path.isdir(proc_dir):
                mem = get_rss(pid)
                if mem > largest_mem[1]:
                    largest_mem[0] = pid
                    largest_mem[1] = mem
        if largest_mem[0] != 0:
            # Take note and kill it
            target = largest_mem[0]
            fail(target, "hostmem")
            os.kill(target, 9)
            # Wait some more time
            time.sleep(4)

    # Time monitoring
    current_time = datetime.now()
    if limit_time == True:
        for pid in sp_pids:
            # Avoid re-targeting a dead child
            proc_dir = os.path.join("/proc", str(pid))
            if pid not in sp_fail and os.path.isdir(proc_dir):
                limit = timedelta(hours = 6)
                ptime = datetime.fromtimestamp(os.path.getmtime(proc_dir))
                if current_time - ptime > limit:
                    # Take note and kill it
                    fail(pid, "timeout")
                    os.kill(pid, 9)
    return


# Generate SGE job scripts from spawn list
def gen_sge_job(spawn_list, args):
    global count_pids

    sge_template = os.path.join(script_path, "sge.tpl")
    jobs_dir = os.path.join(args.out_dir, "jobs")
    if not os.path.isdir(jobs_dir):
        os.mkdir(jobs_dir)
    # Read the template file
    with open(sge_template, "r") as tpl:
        unparsed = tpl.read()
    log("generating sge job scripts")
    for s in spawn_list:
        job = unparsed
        split_cmd, in_name, tmp_dir, log_filepath = s
        # Reconstruct command string
        cmd = cmd_join(split_cmd)
        job_id = "%s%04d" % (short_uuid, count_pids)
        # Replace placeholders with real parameters
        job = job.replace("[EXEDIR]", tmp_dir)
        job = job.replace("[JOBNAME]", job_id)
        job = job.replace("[LOGPATH]", log_filepath)
        job = job.replace("[COMMAND]", cmd)
        # Write the job file
        with open(os.path.join(jobs_dir, "%s.sh" % job_id), "w") as out:
            out.write(job)
        # Increment the counter (no new process is spawned for real)
        count_pids += 1


# Spawn all the programs in the spawn list and control the execution
def execute(spawn_list, args, sem, limit_time=False):
    global shutdown

    # Create a thread for each child, to release the semaphore after execution
    # (this is needed because with subprocess it is only possible to wait for
    # a specific child to terminate, but we want to perform the operation when
    # ANY of them terminates, regardless of which one does)
    def run_in_thread(s):
        global count_pids
        global count_term
        global sp_pids
        global sp_fail

        # Do not even execute if the program is turning off
        if shutdown:
            # Release the semaphore (allows dummy processing of other entries)
            sem.release()
            return

        cmd, in_name, work_path, logpath = s
        with open(logpath, "w") as logfile:
            if in_name:
                in_file = open(os.path.join(work_path, in_name), "rb", 0)
                proc = subprocess.Popen(cmd, cwd=work_path, stdin=in_file,
                    stdout=logfile, stderr=subprocess.STDOUT)
            else:
                proc = subprocess.Popen(cmd, cwd=work_path, stdout=logfile,
                    stderr=subprocess.STDOUT)
            pid = proc.pid
            with lock_pids:
                count_pids += 1
                sp_pids.append(pid)
            # Necessary: sometimes the thread is idling inside the routine
            if (shutdown and
                os.path.exists(os.path.join("/proc", str(pid)))):
                os.kill(pid, 9)
            proc.wait()
            # Flush internal buffers before closing the logfile
            logfile.flush()
            os.fsync(logfile.fileno())
            if in_name:
                in_file.close()

        if pid not in sp_fail and not shutdown:
            # Check logfile for known strings indicating a bad execution
            with io.open(logpath, 'r', encoding='utf-8',
                         errors='replace') as logfile:
                log = logfile.read()
                if "fatal: Could not mmap" in log:
                    fail(pid, "alloc")
                elif "fatal: Out of memory" in log:
                    fail(pid, "oom")
                elif "fatal: Can't load checkpoint file" in log:
                    fail(pid, "parse")
                elif "fatal: syscall" in log:
                    fail(pid, "syscall")
                elif "panic: Unrecognized/invalid instruction" in log:
                    fail(pid, "instr")
                elif "panic: Tried to write unmapped address" in log:
                    fail(pid, "unmapad")
                elif "panic: Page table fault" in log:
                    fail(pid, "ptfault")
                elif "gem5 has encountered a segmentation fault!" in log:
                    fail(pid, "sigsegv")
                elif "Attempt to free invalid pointer" in log:
                    fail(pid, "invptr")
                elif "--- BEGIN LIBC BACKTRACE ---" in log:
                    fail(pid, "unknown")
                elif "Fortran runtime error" in log:
                    fail(pid, "fortran")
                elif ("Resuming from SimPoint" in log and
                        "Done running SimPoint!" not in log):
                    fail(pid, "incompl")

        # Directories cleanup / renaming
        work_dir = os.path.basename(work_path)
        out_path = (work_path if work_dir != "tmp" else uppath(work_path, 1))
        if not args.keep_tmp and shutdown:
            # It is useless to keep the output folder in case of brutal exit
            shutil.rmtree(out_path)
        else:
            # Move or rename relevant output files
            details = out_path.split('/')[-8:]
            sim_conf_id = (details[1].split('.')[0] + "_" +
                            details[0] + "_" +
                            details[3].replace("_", "") + "_" +
                            details[4].replace("-", "") + "_" +
                            details[5].replace("-", "") + "_" +
                            details[6].replace("-", "") + "_" +
                            ("cpt" + details[7].split('_')[1])
                             if "cpt" in out_path else "full")
            if (args.rename and
                os.path.isfile(os.path.join(out_path, "stats.txt"))):
                shutil.move(os.path.join(out_path, "stats.txt"),
                            os.path.join(out_path, sim_conf_id + "_stats.txt"))

            # Delete the temporary directory
            if work_dir == "tmp" and not args.keep_tmp:
                shutil.rmtree(work_path)
            if pid in sp_fail:
                # Rename directory indicating the cause of failure
                head, tail = os.path.split(out_path)
                dest_path = os.path.join(head,
                    "err_" + sp_fail[pid] + "_" + tail)
                if os.path.exists(dest_path):
                    shutil.rmtree(dest_path)
                os.rename(out_path, dest_path)

        # Remove the process from the running list
        with lock_pids:
            sp_pids.remove(pid)
            count_term += 1
            progress_bar(len(spawn_list), count_term, "[bench5]")

        # Release the semaphore (makes space for other processes)
        sem.release()
        return

    # The spawning procedure runs on a separate thread to avoid blocking
    # the main one (e.g. when the semaphore is waiting to be released)
    def spawn_in_thread():
        thread_list = []
        for s in spawn_list:
            # Acquire the semaphore (limits the number of active processes)
            sem.acquire()
            thread = threading.Thread(target=run_in_thread, args=(s,))
            thread_list.append(thread)
            thread.start()
            # Rate limiting
            time.sleep(1)
        # Wait for all threads to terminate
        for t in thread_list:
            t.join()
        return

    # Main thread
    instances = len(spawn_list)
    log("executing %d %s (%d at a time), please wait" % (
        len(spawn_list), "instance" if instances == 1 else "instances",
        min(args.max_proc, instances)))
    # Create and start the spawn thread
    spawn_thread = threading.Thread(target=spawn_in_thread)
    spawn_thread.start()
    progress_bar(instances, 0, "[bench5]")

    try:
        # Periodically check resources utilization
        while(spawn_thread.is_alive()):
            if (not args.no_wd):
                watchdog(limit_time)
            time.sleep(1)
    except KeyboardInterrupt:
        # "Graceful" shutdown
        shutdown = True
        for pid in sp_pids:
            os.kill(pid, 9)
        exit(4)
    return


# Provide simulation class and description
def get_sim_info(mode):
    # Simple simulation
    if mode == "bbv_gen":
        sim_class = BBVGeneration
        sim_desc  = "basic block vectors generation"
    elif mode == "sp_gen":
        sim_class = SPGeneration
        sim_desc  = "simpoints generation"
    elif mode == "cpt_gen":
        sim_class = CptGeneration
        sim_desc  = "checkpoints generation"
    elif mode == "trc_gen":
        sim_class = TraceGeneration
        sim_desc  = "elastic trace generation"
    elif mode == "profile":
        sim_class = MemProfile
        sim_desc  = "memory profiling"
    # Detailed simulation
    elif mode == "cpt_sim":
        sim_class = CptSimulation
        sim_desc  = "benchmark simulation from checkpoints"
    elif mode == "full_sim":
        sim_class = FullSimulation
        sim_desc  = "full benchmark simulation"
    elif mode == "trc_sim":
        sim_class = TraceReplay
        sim_desc  = "elastic trace replay"
    else:
        raise Exception("Unknown specified mode")
    return (sim_class, sim_desc)


# Prepare the environment and generate the spawn list
def detailed_list(sim, mode, args):
    global benchsuite
    global warnings
    spawn_list = []

    if mode == "cpt_sim":
        try:
            paths = sim.prepareEnvironment(benchsuite, args)
        except AssertionError as e:
            if str(e) not in warnings:
                warnings.append(str(e))
            return []
        cmd_list = sim.generateCommand(args)
        assert len(cmd_list) == len(paths), "arrays length mismatch"
        for i in range(len(paths)):
            tmp_dir, log_filepath = paths[i]
            split_cmd = shlex.split(cmd_list[i])
            spawn_list.append((split_cmd, "", tmp_dir,
                log_filepath))
    else:
        try:
            tmp_dir, log_filepath = sim.prepareEnvironment(benchsuite, args)
        except AssertionError as e:
            if str(e) not in warnings:
                warnings.append(str(e))
            return []
        cmd = sim.generateCommand(args)
        split_cmd = shlex.split(cmd)
        spawn_list.append((split_cmd, "", tmp_dir, log_filepath))
    return spawn_list


# Detailed simulation
def detailed_sim(sim_class, exe, mode, args):
    global warnings
    spawn_list = []

    if args.mp and mode == "cpt_sim":
        raise Exception("Multiprocessing not supported with checkpoints")

    # Select CPU architecture and corresponding parameters
    cpu = []
    for model in simparams.cpu_models[args.arch]:
        cpu.append((model, simparams.cpu_models[args.arch][model]))

    # Simulate all possible cases
    if mode != "trc_gen":
        instances = [(model, tech, case) for model in cpu
            for tech in simparams.mem_technologies.get(
                model[0], simparams.mem_technologies.get("default"))
            for case in simparams.mem_cases.get(
                tech, simparams.mem_cases.get("default"))]
    else:
        instances = [(model, "", "") for model in cpu]

    for i in instances:
        model = i[0]
        tech  = i[1]
        case  = i[2]

        if args.mp:
            sim_mp = sim_class(args)
            sim_mp.setSimPath(exe)
            sim_mp.setDetailedParams(model, tech, case, args)

        for b_name in args.benchmarks:
            b_set = args.set[0]

            # Get benchmark general parameters from benchlist.py
            try:
                b_params = get_params(args, b_name)
            except AssertionError as e:
                if str(e) not in warnings:
                    warnings.append(str(e))
                # Skip this benchmark if resources are not found
                continue

            # Get benchmark subset parameters from benchlist.py
            ss_params = get_ss_params(b_name, b_set)
            if args.sss:
                # Take first subset only
                ss_params = ss_params[:1]

            for subset in ss_params:
                if not args.mp:
                    # Generate a different instance each time
                    sim = sim_class(args)
                    sim.setSimPath(exe)
                    sim.setDetailedParams(model, tech, case, args)
                else:
                    # Use the same instance for all the benchmarks
                    sim = sim_mp
                sim.addWorkload(b_name, b_params, subset, args)
                if not args.mp:
                    b_spawn_list = detailed_list(sim, mode, args)
                    spawn_list.extend(b_spawn_list)

        """ If using multiprocessing, finalization happens after adding all the
            selected benchmarks as workloads """
        if args.mp:
            i_spawn_list = detailed_list(sim, mode, args)
            spawn_list.extend(i_spawn_list)
    return spawn_list


# Simple or dummy simulation
def simple_sim(sim_class, exe, mode, args):
    global benchsuite
    global warnings
    spawn_list = []

    if args.mp:
        log("note: parameter --mp is ignored in this mode")
    if mode == "trc_gen":
        if not args.trace_nohint:
            log("note: using hint from simpoint for fast-forwarding")
        else:
            log("note: using fast-forwarding value from --trace-skip")

    for b_name in args.benchmarks:
        b_set = args.set[0]

        # Get benchmark general parameters from benchlist.py
        try:
            b_params = get_params(args, b_name)
        except AssertionError as e:
            if str(e) not in warnings:
                warnings.append(str(e))
            # Skip this benchmark if resources are not found
            continue

        # Get benchmark subset parameters from benchlist.py
        ss_params = get_ss_params(b_name, b_set)
        if args.sss:
            # Take first subset only
            ss_params = ss_params[:1]

        for subset in ss_params:
            b_spl = b_name.split('.')
            b_abbr = b_spl[0] + b_spl[1]
            sim = sim_class(args)
            sim.addWorkload(b_name, b_params, subset, args)
            try:
                tmp_dir, log_filepath = sim.prepareEnvironment(
                    benchsuite, args)
            except AssertionError as e:
                if str(e) not in warnings:
                    warnings.append(str(e))
                continue
            if mode == "bbv_gen" and not args.use_gem5:
                out_dir = sim.getOutPath()
                bbv_filepath = os.path.join(out_dir, "bb.out.%s.%s" % (
                    b_abbr, subset[0]))
                pc_filepath = os.path.join(out_dir, "pc.%s.%s" % (
                    b_abbr, subset[0]))
                # Execute valgrind with exp-bbv tool
                cmd = ("valgrind --tool=exp-bbv" +
                    " --interval-size=" + str(args.int_size) +
                    " --bb-out-file=" + bbv_filepath +
                    " --pc-out-file=" + pc_filepath +
                    " ./" + b_params[0] + " " + subset[1])
                in_name = subset[2]
            elif mode == "sp_gen":
                out_dir = sim.getOutPath()
                bbv_filepath = sim.getBBVFilePath()
                sp_filepath  = os.path.join(out_dir, "simpoint_%s" % subset[0])
                wgt_filepath = os.path.join(out_dir, "weight_%s" % subset[0])
                log_filepath = os.path.join(out_dir, "log_%s" % subset[0])
                # Execute the simpoint utility
                cmd = (exe +
                   (" -inputVectorsGzipped" if args.use_gem5 else "") +
                    " -loadFVFile " + bbv_filepath +
                    " -maxK " + str(args.maxk) +
                    " -saveSimpoints " + sp_filepath +
                    " -saveSimpointWeights " + wgt_filepath)
                in_name = ""
            elif mode == "profile":
                out_dir = sim.getOutPath()
                mem_filepath = os.path.join(out_dir, "mem.%s.%s" % (
                    b_abbr, subset[0]))
                log_filepath = os.path.join(out_dir, "%s.%s.log" % (
                    b_abbr, subset[0]))
                # Execute valgrind with massif tool
                cmd = ("valgrind --tool=massif" +
                    " --pages-as-heap=yes" +
                    " --massif-out-file=" + mem_filepath +
                    " ./" + b_params[0] + " " + subset[1])
                in_name = subset[2]
            else:
                sim.setSimPath(exe)
                cmd = sim.generateCommand(args)
                in_name = ""
            split_cmd = shlex.split(cmd)
            spawn_list.append((split_cmd, in_name, tmp_dir, log_filepath))
    return spawn_list


def simulate(mode, args, sem):
    global warnings
    sim_class, sim_desc = get_sim_info(mode)
    log("-> %s <-" % sim_desc)

    valgrind = (mode == "bbv_gen" and not args.use_gem5) or mode == "profile"
    simpoint = (mode == "sp_gen")
    gem5 = (mode != "sp_gen" and (mode != "bbv_gen" or args.use_gem5))
    exe_path = check_prerequisites(args, valgrind, simpoint, gem5)

    if not args.dry:
        log("preparing the environment, please wait")
    if sim_class(args).isDetailed():
        spawn_list = detailed_sim(sim_class, exe_path, mode, args)
    else:
        spawn_list = simple_sim(sim_class, exe_path, mode, args)

    if warnings:
        for w in warnings:
            log("warning: %s" % w)
        # Clear the warnings after printing them
        warnings = []

    summary = False
    if spawn_list:
        if args.dry:
            for s in spawn_list:
                print(">\t%s" % cmd_join(s[0]))
        elif args.sge:
            gen_sge_job(spawn_list, args)
        else:
            execute(spawn_list, args, sem, mode == "cpt_sim")
            summary = True
    else:
        log("nothing to execute")

    return summary


# Main function
def main():
    global benchsuite
    global count_pids
    global count_term
    global sp_fail

    home = os.path.expanduser("~")
    bsyear = ''.join(c for c in benchsuite if c.isdigit())

    try:
        benchlist.benchmarks
        benchlist.exe_name
        benchlist.preprocessing
        benchlist.mem_size
        benchlist.subset
        benchlist.params
        benchlist.input
    except (NameError, AttributeError):
        log("error: unable to load parameters from benchlist.py")
        sys.exit(1)

    parser = argparse.ArgumentParser(description="Helper for benchmarks simulation with gem5")
    parser.add_argument("set", nargs=1, type=str,
        choices=["test","train","ref"], help="simulation set")
    parser.add_argument("benchmarks", nargs="+", type=str,
        help="list of target benchmarks")
    parser.add_argument("-b", "--bbv", action="store_true",
        help="generate basic block vectors")
    parser.add_argument("-s", "--simpoints", action="store_true",
        help="generate simulation points")
    parser.add_argument("-c", "--checkpoints", action="store_true",
        help="generate checkpoints with gem5")
    parser.add_argument("-x", "--execute", action="store_true",
        help="simulate target benchmarks from checkpoints")
    parser.add_argument("-t", "--trace", action="store_true",
        help="generate elastic trace")
    parser.add_argument("-r", "--replay", action="store_true",
        help="replay elastic trace")
    parser.add_argument("-f", "--full", action="store_true",
        help="simulate target benchmarks normally")
    parser.add_argument("-p", "--profile", action="store_true",
        help="profile benchmarks memory utilization")
    parser.add_argument("--arch", action="store", type=str, default="aarch64",
        choices=["aarch64","armhf","x86-64"], help="cpu architecture " +
        "(default: %(default)s)")
    parser.add_argument("--maxk", action="store", type=int, metavar="N",
        default=30, help="maxK parameter for simpoint (default: %(default)s)")
    parser.add_argument("--int-size", action="store", type=int, metavar="N",
        default=100000000, help="bbv interval size (default: %(default)s)")
    parser.add_argument("--warmup", action="store", type=int, metavar="N",
        default=0, help="number of warmup instructions (default: %(default)s)")
    parser.add_argument("--trace-nohint", action="store_true",
        help="do not use information from simpoint for trace generation")
    parser.add_argument("--trace-skip", action="store", type=int, metavar="N",
        default=100000000, help="instructions to skip for trace generation" +
        " (default: %(default)s)")
    parser.add_argument("--trace-insts", action="store", type=int, metavar="N",
        default=1000000000, help="instruction limit for trace generation" +
        " (default: %(default)s)")
    parser.add_argument("--trace-prefix", action="store", type=str,
        metavar="STR", default="system.switch_cpus.traceListener",
        help="trace name prefix (default: %(default)s)")
    parser.add_argument("--trace-cfg", action="store", type=str,
        metavar="STR", default="etrace_replay.py",
        help="gem5 config file for trace replay (default: %(default)s)")
    parser.add_argument("--l2-banks", action="store", type=int, metavar="N",
        default=4, help="number of banks in L2 cache (default: %(default)s)")
    parser.add_argument("--l3-banks", action="store", type=int, metavar="N",
        default=4, help="number of banks in L3 cache (default: %(default)s)")
    parser.add_argument("--l1i-hwp", action="store", type=str, default=None,
        choices=list(simparams.hwp_config), help="L1I prefetcher parameters" +
        " (default: %(default)s)")
    parser.add_argument("--l1d-hwp", action="store", type=str, default=None,
        choices=list(simparams.hwp_config), help="L1D prefetcher parameters" +
        " (default: %(default)s)")
    parser.add_argument("--l2-hwp", action="store", type=str, default=None,
        choices=list(simparams.hwp_config), help="L2 prefetcher parameters" +
        " (default: %(default)s)")
    parser.add_argument("--l3-hwp", action="store", type=str, default=None,
        choices=list(simparams.hwp_config), help="L3 prefetcher parameters" +
        " (default: %(default)s)")
    parser.add_argument("--max-proc", action="store", type=int, metavar="N",
        default=int(os.sysconf('SC_NPROCESSORS_ONLN')),
        help="number of processes that can run concurrently " +
        "(default: %(default)s)")
    parser.add_argument("--sp-dir", action="store", type=path, metavar="DIR",
        default=os.path.join(home, "simpoint"), help="path of the simpoint " +
        "utility folder (default: %(default)s)")
    parser.add_argument("--gem5-dir", action="store", type=path, metavar="DIR",
        default=os.path.join(home, "gem5-artecs"), help="path of the gem5 " +
        "simulator folder (default: %(default)s)")
    parser.add_argument("--spec-dir", action="store", type=path, metavar="DIR",
        default=os.path.join(home, "cpu" + bsyear, "benchspec", "CPU" +
                             (bsyear if benchsuite != "spec2017" else "")),
        help="path of the SPEC benchmark suite folder (default: %(default)s)")
    parser.add_argument("--data-dir", action="store", type=path, metavar="DIR",
        default=os.path.join(home, "benchmark-data", "SPECCPU", "speccpu" +
                             bsyear),
        help="path of the simulation data folder (default: %(default)s)")
    parser.add_argument("--out-dir", action="store", type=path, metavar="DIR",
        default=os.path.join(home, "out_" + benchsuite), help="path of the " +
        "output folder (default: %(default)s)")
    parser.add_argument("--cpts", action="store", type=int, metavar="N",
        default=0, help="execute N checkpoints only, in order of weight " +
        "(default: 0 = all)")
    parser.add_argument("--repl-mem", action="store", type=str, metavar="SIZE",
        help="memory size in trace replay mode (override)")
    parser.add_argument("--dry", action="store_true",
        help="dry run: only print commands without executing")
    parser.add_argument("--sss", action="store_true",
        help="use a single subset for each benchmark (the first one)")
    parser.add_argument("--mp", action="store_true",
        help="multiprocess environment (one benchmark per core)")
    parser.add_argument("--keep-tmp", action="store_true",
        help="do not remove temporary folders after the execution")
    parser.add_argument("--use-gem5", action="store_true",
        help="use gem5 for bbv generation and gz format for simpoint")
    parser.add_argument("--debug", action="store_true",
        help="use gem5.opt instead of gem5.fast")
    parser.add_argument("--rename", action="store_true",
        help="rename output files with an unique configuration id")
    parser.add_argument("--no-wd", action="store_true",
        help="disable watchdog")
    parser.add_argument("--sge", action="store_true",
        help="generate sge job scripts instead of executing")
    args = parser.parse_args()

    log("welcome to bench5!")
    notes = False
    if args.mp:
        log("note: parameter --mp implies --sss")
        args.sss = True
        notes = True
    if notes:
        print("")

    if (len(args.benchmarks) == 1 and
        args.benchmarks[0] in benchlist.bench_groups):
        args.benchmarks = list(benchlist.bench_groups[args.benchmarks[0]])
    sem = threading.Semaphore(args.max_proc)

    # Create the operation list
    ops = []
    ops.append(("bbv_gen",  args.bbv))
    ops.append(("sp_gen",   args.simpoints))
    ops.append(("cpt_gen",  args.checkpoints))
    ops.append(("cpt_sim",  args.execute))
    ops.append(("trc_gen",  args.trace))
    ops.append(("trc_sim",  args.replay))
    ops.append(("full_sim", args.full))
    ops.append(("profile",  args.profile))

    bools = [op[1] for op in ops]
    # Check if any operation has been selected
    if not True in bools:
        parser.error("no operation selected")
    # Check if ops contains non-consecutive simpoint operations
    elif ((bools[1] and not bools[2] and bools[3]) or
          (bools[0] and not bools[1] and bools[2]) or
          (bools[0] and not bools[1] and bools[3])):
        parser.error("simpoint-related operations are not consecutive")

    # Check if specified benchmarks actually exist
    for i, b_name in enumerate(args.benchmarks):
        b_found = False
        for bl_bench in benchlist.benchmarks:
            if (b_name == bl_bench or
                b_name == bl_bench.split('.')[0]):
                args.benchmarks[i] = bl_bench
                b_found = True
                break
        if b_found == False:
            log("error: unknown benchmark %s" % b_name)
            exit(1)

    for i in range(len(ops)):
        if ops[i][1]:
            ret = simulate(ops[i][0], args, sem)

            # Print failed processes and clear the list
            count_fail = len(sp_fail)
            for pid in sp_fail:
                log("pid " + str(pid) + " failed (code: " + sp_fail[pid] + ")")
            sp_fail.clear()

            if ret:
                # Print some statistics
                log("operation complete")
                log("|___ number of spawned processes\t= %d" % count_pids)
                log("|___ number of failed processes\t= %d" % count_fail)
                if count_pids != 0:
                    log("|___ success rate\t\t\t= %d%%" % (
                        (1 - float(count_fail) / count_pids) * 100))
            # Reset the counters for next phase
            count_pids = 0
            count_term = 0

            # Next operation must fetch data from generated output
            args.data_dir = args.out_dir
            # Add a new line
            print("")
    log("all done, quitting")

if __name__ == "__main__":
    main()
