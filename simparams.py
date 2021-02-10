# CPU MODELS
# ----------
# Tuple: (core type, configuration file, voltage, frequency, out-of-order)

cpu_models = {
    "aarch64" : {
        "sc-a53-odn2"   : ("HPI", "se.py", "0.82V", "1.895GHz", False)
    },
    "x86-64" : {
        "sc-i7-6700"    : ("DerivO3CPU", "se.py", "1.32V", "4.0GHz", True)
    }
}


# PREFETCHER PARAMETERS
# ---------------------
# Tuple: (type, degree, latency, queue size)

hwp_config = {
    "stride1"   : ("StridePrefetcher", 1, 1, 0),
    "stride4q"  : ("StridePrefetcher", 4, 0, 4),
    "stride8"   : ("StridePrefetcher", 8, 1, 0)
}


# MEMORY TECHNOLOGIES
# -------------------
# Tuple: (L1I, L1D, L2, L3)

mem_technologies = {
    "default": {
        "sram-only"     : ("sram", "sram", "sram", "none")
    },
    "sc-i7-6700": {
        "sram-only"     : ("sram", "sram", "sram", "sram")
    }
}


# MEMORY CASE SCENARIOS
# ---------------------

mem_cases = {
    "default": {
        "typical"
    }
}


# MEMORY CONFIGURATIONS
# ---------------------
# Subtuples:
# - L1I {read, write, tag, resp} latency, size, associativity
# - L1D {read, write, tag, resp} latency, size, associativity
# - L2  {read, write, tag, resp} latency, size, associativity
# - L3  {read, write, tag, resp} latency, size, associativity (optional)

mem_configs = {
    "sc-i7-6700" : {    # L3 size is the average per-core (2MB x 4 = 8MB total)
        "sram" : {
            "typical"   : ((4, 4, 2, 2, '32kB', 8), (4, 4, 2, 2, '32kB', 8), (10, 10, 2, 2, '256kB', 4), (38, 38, 2, 2, '2MB', 16))
        }
    },
    "sc-a53-odn2" : {
        "sram" : {
            "typical"   : ((4, 4, 2, 2, '32kB', 2), (4, 4, 2, 2, '32kB', 4), (11, 11, 2, 2, '512kB', 16))
        }
    }
}
