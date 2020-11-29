#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = "Tommaso Marinelli"
__email__  = "tommarin@ucm.es"

import errno
import os
import shutil
import sys
# Local modules
import simparams

python_version = float(".".join(map(str, sys.version_info[:2])))
if python_version < 3.2:
    import subprocess32 as subprocess
else:
    import subprocess

# Ignore errors when a symlink is already present
def force_symlink(orig, dest):
    try:
        os.symlink(orig, dest)
    except OSError as e:
        if e.errno == errno.EEXIST:
            os.remove(dest)
            os.symlink(orig, dest)
    return

# Create a clone of the origin folder with symlinks to all the files
def mirror_dir(orig, dest):
    for root, dirs, files in os.walk(orig):
        subroot = root.split(orig + "/")[1] if root != orig else ""
        for name in dirs:
            os.mkdir(os.path.join(dest, subroot, name), 0o755)
        for name in files:
            force_symlink(os.path.join(root, name),
                os.path.join(dest, subroot, name))
    return

# Helper function to add a parameter only if the value is valid
def add_if_valid(struct, param, value):
    if value:
        struct[param] = value
    return

# Helper function to add a flag only if the test is true
def cond_append(struct, test, flag):
    if test:
        struct.append(flag)


# Base class, cannot be used as it is but must be inherited
class Simulation(object):
    def __init__(self, args):
        if self.__class__ == Simulation:
            raise Exception("You have to use a child class")
        self._debug_flags  = []
        self._flags        = []
        self._workloads    = []
        self._params       = {}
        self._target_dir   = None
        self._trailing_dir = None
        self._bin_path     = None
        self._cfg_path     = None
        self._out_path     = None
        self._prereq_dir   = None
        self._det_conf     = None
        self._detailed     = False
        self._env_prep     = False
        return

    def isDetailed(self):
        return self._detailed

    def setSimPath(self, bin_path):
        if not os.path.isfile(bin_path):
            raise Exception("Simulator executable not found: %s" % bin_path)
        self._bin_path = bin_path

    def _setCpuSysParams(self, model, args):
        # CPU parameters
        model_cpu, model_conf, model_volt, model_freq = model[1][:4]
        self._params["cpu-type"]    = model_cpu
        self._params["cpu-clock"]   = model_freq
        self._params["cpu-voltage"] = model_volt
        # System parameters
        self._params["sys-clock"]   = "1.2GHz"
        self._params["sys-voltage"] = "1.2V"
        # gem5 configuration script
        self._cfg_path = os.path.join(args.gem5_dir, "configs", "example",
            model_conf)

    def setDetailedParams(self, model, tech, case, args):
        if not self._detailed:
            raise Exception("Detailed parameters are not needed in this mode")
        # CPU and system parameters
        self._setCpuSysParams(model, args)
        # Cache parameters
        model_name = model[0]
        dict_mn = (model_name
            if model_name in simparams.mem_technologies else "default")
        hier  = simparams.mem_technologies[dict_mn][tech]
        cache = simparams.mem_configs[model_name]
        l1ip = simparams.hwp_config.get(args.l1i_hwp, "")
        l1dp = simparams.hwp_config.get(args.l1d_hwp, "")
        l2p = simparams.hwp_config.get(args.l2_hwp, "")
        l3p = simparams.hwp_config.get(args.l3_hwp, "")
        self._flags.append("hwp-override")
        self._flags.append("caches")
        if l1dp:
            add_if_valid(self._params, "l1d-hwp-type", l1dp[0])
            add_if_valid(self._params, "l1d-hwp-deg",  l1dp[1])
            add_if_valid(self._params, "l1d-hwp-lat",  l1dp[2])
            add_if_valid(self._params, "l1d-hwp-qs",   l1dp[3])
        self._params["l1d-data-lat"]  = cache[hier[0]][case][0][0]
        self._params["l1d-write-lat"] = cache[hier[0]][case][0][1]
        self._params["l1d-tag-lat"]   = cache[hier[0]][case][0][2]
        self._params["l1d-resp-lat"]  = cache[hier[0]][case][0][3]
        self._params["l1d_size"]      = cache[hier[0]][case][0][4]
        self._params["l1d_assoc"]     = cache[hier[0]][case][0][5]
        if l1ip:
            add_if_valid(self._params, "l1i-hwp-type", l1ip[0])
            add_if_valid(self._params, "l1i-hwp-deg",  l1ip[1])
            add_if_valid(self._params, "l1i-hwp-lat",  l1ip[2])
            add_if_valid(self._params, "l1i-hwp-qs",   l1ip[3])
        self._params["l1i-data-lat"]  = cache[hier[1]][case][1][0]
        self._params["l1i-write-lat"] = cache[hier[1]][case][1][1]
        self._params["l1i-tag-lat"]   = cache[hier[1]][case][1][2]
        self._params["l1i-resp-lat"]  = cache[hier[1]][case][1][3]
        self._params["l1i_size"]      = cache[hier[1]][case][1][4]
        self._params["l1i_assoc"]     = cache[hier[1]][case][1][5]
        self._flags.append("l2cache")
        if args.l2_banks:
            self._flags.append("l2-enable-banks")
            self._params["l2-num-banks"] = args.l2_banks
        if l2p:
            add_if_valid(self._params, "l2-hwp-type", l2p[0])
            add_if_valid(self._params, "l2-hwp-deg",  l2p[1])
            add_if_valid(self._params, "l2-hwp-lat",  l2p[2])
            add_if_valid(self._params, "l2-hwp-qs",   l2p[3])
        self._params["l2-data-lat"]   = cache[hier[2]][case][2][0]
        self._params["l2-write-lat"]  = cache[hier[2]][case][2][1]
        self._params["l2-tag-lat"]    = cache[hier[2]][case][2][2]
        self._params["l2-resp-lat"]   = cache[hier[2]][case][2][3]
        self._params["l2_size"]       = cache[hier[2]][case][2][4]
        self._params["l2_assoc"]      = cache[hier[2]][case][2][5]
        if hier[3] != "none":
            self._flags.append("l3cache")
            if args.l3_banks:
                self._flags.append("l3-enable-banks")
                self._params["l3-num-banks"] = args.l3_banks
            if l3p:
                add_if_valid(self._params, "l3-hwp-type", l3p[0])
                add_if_valid(self._params, "l3-hwp-deg",  l3p[1])
                add_if_valid(self._params, "l3-hwp-lat",  l3p[2])
                add_if_valid(self._params, "l3-hwp-qs",   l3p[3])
            self._params["l3-data-lat"]   = cache[hier[3]][case][3][0]
            self._params["l3-write-lat"]  = cache[hier[3]][case][3][1]
            self._params["l3-tag-lat"]    = cache[hier[3]][case][3][2]
            self._params["l3-resp-lat"]   = cache[hier[3]][case][3][3]
            self._params["l3_size"]       = cache[hier[3]][case][3][4]
            self._params["l3_assoc"]      = cache[hier[3]][case][3][5]
        self._det_conf = (model, tech, case)
        return

    def _setOutputParam(self):
        if not self._workloads:
            raise Exception("No workload has been set")
        b_spl_0 = self._workloads[0][0].split(".")
        b_abbr_0 = b_spl_0[0] + b_spl_0[1]
        self._params["output"] = os.path.join(self._out_path, "%s.%s.out" % (
            b_abbr_0, self._workloads[0][2]))
        if len(self._workloads) > 1:
            for w in self._workloads[1:]:
                b_spl = self._workloads[0][0].split(".")
                b_abbr = b_spl_0[0] + b_spl_0[1]
                self._params["output"] += ";%s" % os.path.join(self._out_path,
                    "%s.%s.out" % (b_abbr, w[2]))

    def addWorkload(self, b_name, b_params, subset, args):
        if not self._target_dir:
            raise Exception("Target directory is not set")
        if self._detailed and not self._det_conf:
            raise Exception("Detailed parameters must be set first")
        if self._env_prep:
            raise Exception("The environment has already been prepared")
        if not self._workloads:
            # Single workload
            self._params["cmd"] = "./%s" % b_params[0]
            self._params["mem-size"] = b_params[2]
            if subset[1]:
                self._params["options"] = subset[1]
            if subset[2]:
                self._params["input"] = subset[2]
            self._params["num-cpus"] = 1
            # Set workload-related variables and paths
            self._wl_id   = b_name.split(".")[0]
            self._wl_ss   = subset[0]
            self._base_sf = os.path.join(args.arch, b_name)
            self._out_path = os.path.join(args.out_dir, self._base_sf,
                self._target_dir, self._wl_ss)
        else:
            self._params["cmd"] += (";./%s" % b_params[0])
            if bytes(b_params[2]) > bytes(self._params["mem-size"]):
                self._params["mem-size"] = b_params[2]
            self._params["options"] = ("%s;%s" % (self._params["options"],
                subset[1]) if "options" in self._params
                else ";%s" % subset[1])
            self._params["input"] = ("%s;%s" % (
                self._params["input"], subset[2]) if "input" in self._params
                else ";%s" % subset[2])
            self._params["num-cpus"] += 1
            # Set workload-related variables and paths
            self._wl_id += "_%s" % b_name.split(".")[0]
            self._wl_ss += "_%s" % subset[0]
            self._base_sf = os.path.join(args.arch, self._wl_id)
            self._out_path = os.path.join(args.out_dir, self._base_sf,
                self._target_dir, self._wl_ss)
        # Update output folder with detailed parameters, if needed
        if self._detailed:
            self._out_path = os.path.join(self._out_path, self._det_conf[0][0],
                self._det_conf[1], self._det_conf[2])
        # Add trailing directory, if set
        if self._trailing_dir:
            self._out_path = os.path.join(self._out_path, self._trailing_dir)
        # Set data path, if needed
        if self._prereq_dir:
            self._data_path = os.path.join(args.data_dir, self._base_sf,
                self._prereq_dir, self._wl_ss)
        # Append workload to the list
        self._workloads.append((b_name, b_params, subset[0]))
        # Set/update output parameter
        self._setOutputParam()
        return

    def _prepareFolder(self, out_path, benchsuite, args):
        if not self._workloads:
            raise Exception("No workload has been set")
        tmp_path = os.path.join(out_path, "tmp")
        # Remove the temporary folder if it already exists
        if os.path.isdir(tmp_path):
            shutil.rmtree(tmp_path)
        # Create the temporary folder and consequently the output folder
        os.makedirs(tmp_path, mode=0o755)
        for w in self._workloads:
            b_name, b_params = w[:2]
            spec_b_folder = os.path.join(args.spec_dir, b_name)
            # Make a symlink to the executable in the temporary directory
            b_exe_path = os.path.join(spec_b_folder, "exe", b_params[0])
            force_symlink(b_exe_path, os.path.join(tmp_path, b_params[0]))
            # Prepare the temporary directory with symlinks to input data
            b_set = args.set[0]
            if benchsuite == "spec2017":
                # If there's no data folder check in the rate benchmark folder
                if not os.path.isdir(os.path.join(spec_b_folder, "data")):
                    rate_b_name = "5" + b_name[1:len(b_name)-1] + "r"
                    spec_b_folder = os.path.join(args.spec_dir, rate_b_name)
                if b_set == "ref":
                    if "_s" in b_name:
                        # If there's no refspeed folder try with refrate
                        b_set = ("refspeed" if os.path.isdir(os.path.join(
                            spec_b_folder, "data", "refspeed")) else "refrate")
                    else:
                        b_set = "refrate"
            in_folders = [os.path.join(spec_b_folder, "data", b_set, "input"),
                os.path.join(spec_b_folder, "data", "all", "input")]
            for d in in_folders:
                # Any invalid path will be ignored
                if os.path.isdir(d):
                    mirror_dir(d, tmp_path)
            # Do preprocessing of input data if necessary
            if b_params[1] != None:
                proc = subprocess.Popen(b_params[1], shell=True, cwd=tmp_path)
                proc.wait()
        return tmp_path

    def prepareEnvironment(self, benchsuite, args):
        if not self._workloads:
            raise Exception("No workload has been set")
        if self._prereq_dir:
            assert os.path.isdir(self._data_path), "missing folder %s" % (
                self._data_path)
        tmp_path = self._prepareFolder(self._out_path, benchsuite, args)
        if not self._trailing_dir:
            log_path = os.path.join(self._out_path, "%s_%s.log" % (
                self._wl_id, self._target_dir))
        else:
            log_path = os.path.join(self._out_path, "%s_%s_%s.log" % (
                self._wl_id, self._target_dir, self._trailing_dir))
        self._env_prep = True
        return tmp_path, log_path

    def generateCommand(self, args):
        if not self._bin_path:
            raise Exception("Simulator path has not been set")
        if not self._env_prep:
            raise Exception("Environment has not been prepared")
        # Use default config path if not set
        if not self._cfg_path:
            self._cfg_path = os.path.join(args.gem5_dir, "configs",
                "example", "se.py")
        if not os.path.isfile(self._cfg_path):
            raise Exception("Config file does not exist: %s" % self._cfg_path)
        # Generate the command
        command = "%s --outdir=%s " % (self._bin_path, self._out_path)
        if self._debug_flags:
            command += "--debug-flags="
            for i, d in enumerate(self._debug_flags):
                command += "%s" % d
                command += ("," if i != len(self._debug_flags) - 1 else " ")
        command += "%s " % self._cfg_path
        for f in sorted(self._flags):
            command += "--%s " % f
        for p in sorted(self._params):
            command += "--%s=\"%s\" " % (p, str(self._params[p]))
        return command


""" Some other applications than the gem5 simulator may need to
operate on SPEC. With a DummySimulation object it is still possible
to prepare the environment, then leave the command generation to
someone else. """
class DummySimulation(Simulation):
    def __init__(self, args):
        if self.__class__ == DummySimulation:
            raise Exception("You have to use a child class")
        super(DummySimulation, self).__init__(args)

    def setSimPath(self, bin_path):
        raise Exception("Too much for a dummy simulation")

    def setDetailedParams(self, model, tech, case, args):
        raise Exception("Too much for a dummy simulation")

    def generateCommand(self, args):
        raise Exception("Too much for a dummy simulation")

    def getOutPath(self):
        if not self._env_prep:
            raise Exception("Environment has not been prepared")
        return self._out_path


# Basic Block Vectors (BBVs) generation class
class BBVGeneration(Simulation):
    def __init__(self, args):
        super(BBVGeneration, self).__init__(args)
        self._params["cpu-type"] = "NonCachingSimpleCPU"
        self._flags.append("simpoint-profile")
        self._params["simpoint-interval"] = args.int_size
        self._target_dir = "bbv"
        return

    def addWorkload(self, b_name, b_params, subset, args):
        if self._workloads:
            raise Exception("Cannot use this mode with multiple workloads")
        super(BBVGeneration, self).addWorkload(b_name, b_params, subset, args)
        return

    """ BBVs generation can be done with or without gem5.
    In this latter case we need a way to get the output path. """
    def getOutPath(self):
        if not self._env_prep:
            raise Exception("Environment has not been prepared")
        return self._out_path


# Simpoints generation class
class SPGeneration(DummySimulation):
    def __init__(self, args):
        super(SPGeneration, self).__init__(args)
        self._target_dir = "simpoint"
        self._prereq_dir = "bbv"
        return

    def addWorkload(self, b_name, b_params, subset, args):
        if self._workloads:
            raise Exception("Cannot use this mode with multiple workloads")
        super(SPGeneration, self).addWorkload(b_name, b_params, subset, args)
        return

    def prepareEnvironment(self, benchsuite, args):
        if not self._workloads:
            raise Exception("No workload has been set")
        assert os.path.isdir(self._data_path), "missing folder %s" % (
            self._data_path)
        b_spl = self._workloads[0][0].split('.')
        b_abbr = b_spl[0] + b_spl[1]
        bbv_filename = "bb.out." + b_abbr + "." + self._workloads[0][2]
        bbv_filepath = os.path.join(self._data_path, bbv_filename)
        assert os.path.isfile(bbv_filepath), "missing file %s" % bbv_filepath
        # Check if the BBVs file contains any interval
        rgx = subprocess.check_output("sed '/^[[:blank:]]*#/d;s/#.*//' " +
            bbv_filepath + " | wc -w", shell=True)
        result = int(rgx)
        assert result != 0, "%s does not contain any interval" % bbv_filename
        tmp_path, log_path = super(
            SPGeneration, self).prepareEnvironment(benchsuite, args)
        self._bbv_filepath = bbv_filepath
        return tmp_path, log_path

    def getBBVFilePath(self):
        if not self._env_prep:
            raise Exception("Environment has not been prepared")
        return self._bbv_filepath


# gem5 checkpoints from simpoints generation class
class CptGeneration(Simulation):
    def __init__(self, args):
        super(CptGeneration, self).__init__(args)
        self._params["cpu-type"] = "AtomicSimpleCPU"
        self._target_dir = "checkpoint"
        self._prereq_dir = "simpoint"
        return

    def addWorkload(self, b_name, b_params, subset, args):
        if self._workloads:
            raise Exception("Cannot use this mode with multiple workloads")
        super(CptGeneration, self).addWorkload(b_name, b_params, subset, args)
        return

    def prepareEnvironment(self, benchsuite, args):
        if not self._workloads:
            raise Exception("No workload has been set")
        assert os.path.isdir(self._data_path), "missing folder %s" % (
            self._data_path)
        sp_fname  = "simpoint_%s" % self._wl_ss
        wgt_fname = "weight_%s" % self._wl_ss
        sp_fpath  = os.path.join(self._data_path, sp_fname)
        wgt_fpath = os.path.join(self._data_path, wgt_fname)
        assert os.path.isfile(sp_fpath),  "missing file %s" % sp_fpath
        assert os.path.isfile(wgt_fpath), "missing file %s" % wgt_fpath
        tmp_path, log_path = super(
            CptGeneration, self).prepareEnvironment(benchsuite, args)
        self._params["take-simpoint-checkpoint"] = ("%s,%s,%d,%d" % (
            sp_fpath, wgt_fpath, args.int_size, args.warmup))
        return tmp_path, log_path


# gem5 simulation from simpoints/checkpoints class
class CptSimulation(Simulation):
    def __init__(self, args):
        super(CptSimulation, self).__init__(args)
        self._detailed = True
        self._target_dir = "simulation"
        self._prereq_dir = "checkpoint"
        cond_append(self._debug_flags, args.atrace, "AccessTrace")
        cond_append(self._debug_flags, args.ctrace, "ConflictTrace")
        return

    def prepareEnvironment(self, benchsuite, args):
        if not self._workloads:
            raise Exception("No workload has been set")
        assert os.path.isdir(self._data_path), "missing folder %s" % (
            self._data_path)
        cpt_prefix = "cpt.simpoint_"
        cpt_folders = sorted([d for d in os.listdir(self._data_path)
            if cpt_prefix in d])
        assert any(cpt_folders), "missing checkpoints in %s" % self._data_path
        cpt_indexed = zip(range(1, len(cpt_folders) + 1), cpt_folders)
        cpt_sorted  = sorted(cpt_indexed,
            key=lambda x: float(x[1].split('_')[5]), reverse=True)
        if args.cpts and args.cpts < len(cpt_sorted):
            cpt_sorted = cpt_sorted[:args.cpts]
        cpt_paths = []
        self.cpt_info = []
        for idx, cpt in cpt_sorted:
            cpt_out_path = os.path.join(self._out_path, cpt)
            cpt_log_path = os.path.join(cpt_out_path, "%s.log" % self._wl_id)
            cpt_tmp_path = super(CptSimulation, self)._prepareFolder(
                cpt_out_path, benchsuite, args)
            cpt_paths.append((cpt_tmp_path, cpt_log_path))
            self.cpt_info.append((idx, cpt_out_path))
        self._flags.append("restore-simpoint-checkpoint")
        self._params["checkpoint-dir"] = self._data_path
        self._env_prep = True
        return cpt_paths

    def generateCommand(self, args):
        cmd_list = []
        for idx, path in self.cpt_info:
            self._out_path = path
            self._setOutputParam()
            self._params["checkpoint-restore"] = idx
            cmd_list.append(super(CptSimulation, self).generateCommand(args))
        return cmd_list


# gem5 standard simulation class
class FullSimulation(Simulation):
    def __init__(self, args):
        super(FullSimulation, self).__init__(args)
        self._detailed = True
        self._target_dir   = "simulation"
        self._trailing_dir = "full"
        cond_append(self._debug_flags, args.atrace, "AccessTrace")
        cond_append(self._debug_flags, args.ctrace, "ConflictTrace")
        return


# gem5 elastic trace generation class
class TraceGeneration(Simulation):
    def __init__(self, args):
        super(TraceGeneration, self).__init__(args)
        self._detailed = True
        self._flags.append("hwp-override")
        self._flags.append("caches")
        self._flags.append("elastic-trace-en")
        self._params["mem-type"] = "SimpleMemory"
        """ Note: if using se.py, remember to not apply
            CpuConfig.config_etrace() to the first CPU
            (since fast-forward is used) """
        self._params["fast-forward"] = args.trace_skip
        self._params["maxinsts"] = args.trace_insts
        self._params["data-trace-file"] = "deptrace.proto.gz"
        self._params["inst-trace-file"] = "fetchtrace.proto.gz"
        self._target_dir = "trace"
        if not args.trace_nohint:
            self._prereq_dir = "simpoint"
        return

    # Tech and case arguments are just ignored
    def setDetailedParams(self, model, tech, case, args):
        self._setCpuSysParams(model, args)
        self._det_conf = (model, "", "")
        return

    def prepareEnvironment(self, benchsuite, args):
        if not self._workloads:
            raise Exception("No workload has been set")
        cpu_type = self._det_conf[0][1][0]
        cpu_o3   = self._det_conf[0][1][4]
        assert cpu_o3, "%s is not out-of-order" % cpu_type
        if self._prereq_dir:
            assert os.path.isdir(self._data_path), "missing folder %s" % (
                self._data_path)
            sp_fname  = "simpoint_%s" % self._wl_ss
            wgt_fname = "weight_%s" % self._wl_ss
            sp_fpath  = os.path.join(self._data_path, sp_fname)
            wgt_fpath = os.path.join(self._data_path, wgt_fname)
            assert os.path.isfile(sp_fpath),  "missing file %s" % sp_fpath
            assert os.path.isfile(wgt_fpath), "missing file %s" % wgt_fpath
            # WARNING: should be read from file, for now assume it is the same
            int_size = args.int_size
            weights = {}
            with open(wgt_fpath, 'r') as wgt_file:
                for l in wgt_file:
                    value, idx = l.split()
                    weights[idx] = value
            # Get the index of the most relevant checkpoint
            sp_index = max(weights, key=weights.get)
            sp_bbv = None
            with open(sp_fpath, 'r') as sp_file:
                for l in sp_file:
                    value, idx = l.split()
                    if idx == sp_index:
                        sp_bbv = int(value)
                        break
            if not sp_bbv:
                raise Exception("Unexpected error: invalid simpoint index")
            offset = int(args.trace_insts / 2)
            ff_point = sp_bbv * int_size - offset
            # Check if enough instructions would be skipped (for warmup)
            if ff_point < args.trace_skip:
                # Revert to fixed value
                ff_point = args.trace_skip
            self._params["fast-forward"] = ff_point
        tmp_path, log_path = super(
            TraceGeneration, self).prepareEnvironment(benchsuite, args)
        return tmp_path, log_path


# gem5 elastic trace simulation class
class TraceReplay(Simulation):
    def __init__(self, args):
        super(TraceReplay, self).__init__(args)
        self._detailed = True
        self._target_dir   = "simulation"
        self._trailing_dir = "trace_replay"
        self._prereq_dir   = "trace"
        cond_append(self._debug_flags, args.atrace, "AccessTrace")
        cond_append(self._debug_flags, args.ctrace, "ConflictTrace")
        return

    def setDetailedParams(self, model, tech, case, args):
        super(TraceReplay, self).setDetailedParams(model, tech, case, args)
        self._params["cpu-type"] = "TraceCPU"
        self._cfg_path = os.path.join(args.gem5_dir, "configs", "example",
            args.trace_cfg)
        return

    # Stripped copy of the original addWorkload method
    def addWorkload(self, b_name, b_params, subset, args):
        if not self._det_conf:
            raise Exception("Detailed parameters must be set first")
        if self._env_prep:
            raise Exception("The environment has already been prepared")
        if not self._workloads:
            # Single workload
            self._params["mem-size"] = b_params[2]
            self._params["num-cpus"] = 1
            # Set workload-related variables and paths
            self._wl_id    = b_name.split(".")[0]
            self._wl_ss    = subset[0]
            self._base_sf  = os.path.join(args.arch, b_name)
            self._out_path = os.path.join(args.out_dir, self._base_sf,
                self._target_dir, self._wl_ss)
            self._data_path = os.path.join(args.data_dir, args.arch, b_name,
                self._prereq_dir, subset[0], self._det_conf[0][0])
        else:
            if bytes(b_params[2]) > bytes(self._params["mem-size"]):
                self._params["mem-size"] = b_params[2]
            self._params["num-cpus"] += 1
            # Set workload-related variables and paths
            self._wl_id += "_%s" % b_name.split(".")[0]
            self._wl_ss += "_%s" % subset[0]
            self._base_sf = os.path.join(args.arch, self._wl_id)
            self._out_path = os.path.join(args.out_dir, self._base_sf,
                self._target_dir, self._wl_ss)
            self._data_path += ";%s" % os.path.join(args.data_dir, args.arch,
                b_name, self._prereq_dir, subset[0], self._det_conf[0][0])
        # Update output folder with detailed parameters
        self._out_path = os.path.join(self._out_path, self._det_conf[0][0],
            self._det_conf[1], self._det_conf[2])
        # Add trailing directory
        self._out_path = os.path.join(self._out_path, self._trailing_dir)
        # Append workload to the list
        self._workloads.append((b_name, b_params, subset[0]))
        return

    def prepareEnvironment(self, benchsuite, args):
        if not self._workloads:
            raise Exception("No workload has been set")
        cpu_type = self._det_conf[0][1][0]
        cpu_o3   = self._det_conf[0][1][4]
        assert cpu_o3, "%s is not out-of-order" % cpu_type
        for i, d in enumerate(self._data_path.split(';')):
            assert os.path.isdir(d), "missing folder %s" % d
            itrace_fname = "%s.%s" % (args.trace_prefix, "fetchtrace.proto")
            dtrace_fname = "%s.%s" % (args.trace_prefix, "deptrace.proto")
            itrace_fpath = os.path.join(d, itrace_fname)
            dtrace_fpath = os.path.join(d, dtrace_fname)
            # If the uncompressed trace is not present try with the gzipped one
            if not os.path.isfile(itrace_fpath):
                itrace_fpath = itrace_fpath + ".gz"
            if not os.path.isfile(dtrace_fpath):
                dtrace_fpath = dtrace_fpath + ".gz"
            assert os.path.isfile(itrace_fpath), "missing file %s(.%s)" % (
                tuple(itrace_fpath.rsplit('.', 1)))
            assert os.path.isfile(dtrace_fpath), "missing file %s(.%s)" % (
                tuple(dtrace_fpath.rsplit('.', 1)))
            if i == 0:
                self._params["inst-trace-file"] = itrace_fpath
                self._params["data-trace-file"] = dtrace_fpath
            else:
                self._params["inst-trace-file"] += ";%s" % itrace_fpath
                self._params["data-trace-file"] += ";%s" % dtrace_fpath
        # No need to really prepare the tmp folder here
        tmp_path = self._out_path
        if not os.path.isdir(tmp_path):
            os.makedirs(tmp_path, mode=0o755)
        log_path = os.path.join(self._out_path, "%s_%s_%s.log" % (
            self._wl_id, self._target_dir, self._trailing_dir))
        self._env_prep = True
        return tmp_path, log_path


# Memory profiling class
class MemProfile(DummySimulation):
    def __init__(self, args):
        super(MemProfile, self).__init__(args)
        self._target_dir = "profile"
        return
