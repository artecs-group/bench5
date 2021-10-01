# Name of individual benchmarks
benchmarks = (
    "500.perlbench_r",
    "502.gcc_r",
    "503.bwaves_r",
    "505.mcf_r",
    "507.cactuBSSN_r",
    "508.namd_r",
    "510.parest_r",
    "511.povray_r",
    "519.lbm_r",
    "520.omnetpp_r",
    "521.wrf_r",
    "523.xalancbmk_r",
    "525.x264_r",
    "526.blender_r",
    "527.cam4_r",
    "531.deepsjeng_r",
    "538.imagick_r",
    "541.leela_r",
    "544.nab_r",
    "548.exchange2_r",
    "549.fotonik3d_r",
    "554.roms_r",
    "557.xz_r",
    "600.perlbench_s",
    "602.gcc_s",
    "603.bwaves_s",
    "605.mcf_s",
    "607.cactuBSSN_s",
    "619.lbm_s",
    "620.omnetpp_s",
    "621.wrf_s",
    "623.xalancbmk_s",
    "625.x264_s",
    "627.cam4_s",
    "628.pop2_s",
    "631.deepsjeng_s",
    "638.imagick_s",
    "641.leela_s",
    "644.nab_s",
    "648.exchange2_s",
    "649.fotonik3d_s",
    "654.roms_s",
    "657.xz_s",
    "996.specrand_fs",
    "997.specrand_fr",
    "998.specrand_is",
    "999.specrand_ir"
)

bench_groups = {
    "all_rate"          : (b for b in benchmarks if b[0] == '5'),
    "all_speed"         : (b for b in benchmarks if b[0] == '6'),
    "exp17"             : ("602", "605", "607", "623", "625", "628", "638", "641", "649", "654")
}

# If the executable binary name differs from the benchmark, note it here
exe_name = {
    "502.gcc_r"         : "cpugcc_r",
    "507.cactuBSSN_r"   : "cactusBSSN_r",
    "523.xalancbmk_r"   : "cpuxalan_r",
    "602.gcc_s"         : "sgcc",
    "603.bwaves_s"      : "speed_bwaves",
    "628.pop2_s"        : "speed_pop2",
    "654.roms_s"        : "sroms"
}

# Specify actions to take before launching benchmarks (from the perl (object.pm) script)
preprocessing = {
    # 525 needs preprocessing (yuv file generation), but better doing it before and leaving the file in the data folder
    # 549 needs preprocessing (OBJ.dat.xz extraction with specxz), but better doing it before and leaving the file in the data folder
    # 628 renaming .in files is just fine as long as we don't need multithreading
    "628.pop2_s"        : "for i in $(find . -name '*.in'); do mv $i ${i%.in}; done"
}

# Memory size limit for gem5 (default: 2GB)
# Based for x86-64. Under aarch64 no need to increase under test dataset
#TODO update with the new profiling values as they are ready
mem_size = {
    "test" : {
        "619.lbm_s"         : "4GB",
        "631.deepsjeng_s"   : "8GB"
    },

    "train" : {
        "619.lbm_s"         : "4GB",
        "631.deepsjeng_s"   : "8GB"
    },

    "ref" : {
        "602.gcc_s"         : "8GB",
        "603.bwaves_s"      : "12GB",
        "605.mcf_s"         : "6GB",
        "607.cactuBSSN_s"   : "8GB",
        "619.lbm_s"         : "4GB",
        "631.deepsjeng_s"   : "8GB",
        "638.imagick_s"     : "4GB",
        "649.fotonik3d_s"   : "10GB",
        "654.roms_s"        : "12GB",
        "657.xx_s"          : "16GB"
    }
}

# Define if there are several inputs for any benchmarks
subset = {
    "test" : {
        "500.perlbench_r"    : ("makerand", "test"),
        "503.bwaves_r"       : ("bwaves1", "bwaves2"),
        "557.xz_r"           : ("1_0", "1_1", "1_2", "1_3e", "1_4", "1_4e", "4_0", "4_1", "4_2", "4_3e", "4_4", "4_4e"),
        "600.perlbench_s"    : ("makerand", "test"),
        "603.bwaves_s"       : ("bwaves1", "bwaves2"),
        "657.xz_s"           : ("1_0", "1_1", "1_2", "1_3e", "1_4", "1_4e", "4_0", "4_1", "4_2", "4_3e", "4_4", "4_4e")

    },
    "train" : {
        "500.perlbench_r"    : ("diffmail", "perfect", "scrabbl", "splitmail", "suns"),
        "502.gcc_r"          : ("200", "scilab", "train01"),
        "503.bwaves_r"       : ("bwaves1", "bwaves2"),
        "544.nab_r"          : ("aminos", "gcn4dna"),
        "557.xz_r"           : ("combined", "IMG_2560"),
        "600.perlbench_s"    : ("diffmail", "perfect", "scrabbl", "splitmail", "suns"),
        "602.gcc_s"          : ("200", "scilab", "train01"),
        "603.bwaves_s"       : ("bwaves1", "bwaves2"),
        "644.nab_s"          : ("aminos", "gcn4dna"),
        "657.xz_s"           : ("combined", "IMG_2560")
    },
    "ref" : {
        "500.perlbench_r"    : ("checkspam", "diffmail", "splitmail"),
        "502.gcc_r"          : ("gcc-ppo3", "gcc-ppo2", "gcc-smaller", "ref32o5", "ref32o3"),
        "503.bwaves_r"       : ("bwaves1", "bwaves2", "bwaves3", "bwaves4"),
        "525.x264_r"         : ("pass1", "pass2", "seek"),
        "557.xz_r"           : ("cld", "cpu2006docs", "combined"),
        "600.perlbench_s"    : ("checkspam", "diffmail", "splitmail"),
        "602.gcc_s"          : ("noil", "il1000", "il24000"),
        "603.bwaves_s"       : ("bwaves1", "bwaves2"),
        "625.x264_s"         : ("pass1", "pass2", "seek"),
        "657.xz_s"           : ("cld", "cpu2006docs")
    }
}

# Provide all the parameters needed for each execution
params = {
    # Test runs
    "test" : {
        "500.perlbench_r" : ("-I. -I./lib makerand.pl", "-I. -I./lib test.pl"),
        "502.gcc_r"       : ("t1.c -O3 -finline-limit=50000 -o t1.opts-O3_-finline-limit_50000.s"),
        "503.bwaves_r"    : ("bwaves_1", "bwaves_2"),
        "505.mcf_r"       : ("inp.in"),
        "507.cactuBSSN_r" : ("spec_test.par"),
        "508.namd_r"      : ("--input apoa1.input --iterations 1 --output apoa1.test.output"),
        "510.parest_r"    : ("test.prm"),
        "511.povray_r"    : ("SPEC-benchmark-test.ini"),
        "519.lbm_r"       : ("20 reference.dat 0 1 100_100_130_cf_a.of"),
        "520.omnetpp_r"   : ("-c General -r 0"), 
##        "520.omnetpp_r"   : ("omnetpp.ini"), TODO this file exists as in spec2006
        "523.xalancbmk_r" : ("-v test.xml xalanc.xsl"),
        "525.x264_r"      : ("--dumpyuv 50 --frames 156 -o BuckBunny_New.264 BuckBunny.yuv 1280x720"),
        "526.blender_r"   : ("cube.blend --render-output cube_ --threads 1 -b -F RAWTGA -s 1 -e 1 -a"),
        "531.deepsjeng_r" : ("test.txt"),
        "538.imagick_r"   : ("-limit disk 0 test_input.tga -shear 25 -resize 640x480 -negate -alpha Off test_output.tga"),
        "541.leela_r"     : ("test.sgf"),
        "544.nab_r"       : ("hkrdenq 1930344093 1000"),
        "548.exchange2_r" : ("0"),
        "557.xz_r"        : ("cpu2006docs.tar.xz 1 055ce243071129412e9dd0b3b69a21654033a9b723d874b2015c774fac1553d9713be561ca86f74e4f16f22e664fc17a79f30caa5ad2c04fbc447549c2810fae 650156 -1 0",
                             "cpu2006docs.tar.xz 1 055ce243071129412e9dd0b3b69a21654033a9b723d874b2015c774fac1553d9713be561ca86f74e4f16f22e664fc17a79f30caa5ad2c04fbc447549c2810fae 639996 -1 1",
                             "cpu2006docs.tar.xz 1 055ce243071129412e9dd0b3b69a21654033a9b723d874b2015c774fac1553d9713be561ca86f74e4f16f22e664fc17a79f30caa5ad2c04fbc447549c2810fae 637616 -1 2",
                             "cpu2006docs.tar.xz 1 055ce243071129412e9dd0b3b69a21654033a9b723d874b2015c774fac1553d9713be561ca86f74e4f16f22e664fc17a79f30caa5ad2c04fbc447549c2810fae 628996 -1 3e",
                             "cpu2006docs.tar.xz 1 055ce243071129412e9dd0b3b69a21654033a9b723d874b2015c774fac1553d9713be561ca86f74e4f16f22e664fc17a79f30caa5ad2c04fbc447549c2810fae 631912 -1 4",
                             "cpu2006docs.tar.xz 1 055ce243071129412e9dd0b3b69a21654033a9b723d874b2015c774fac1553d9713be561ca86f74e4f16f22e664fc17a79f30caa5ad2c04fbc447549c2810fae 629064 -1 4e",
                             "cpu2006docs.tar.xz 4 055ce243071129412e9dd0b3b69a21654033a9b723d874b2015c774fac1553d9713be561ca86f74e4f16f22e664fc17a79f30caa5ad2c04fbc447549c2810fae 1548636 1555348 0",
                             "cpu2006docs.tar.xz 4 055ce243071129412e9dd0b3b69a21654033a9b723d874b2015c774fac1553d9713be561ca86f74e4f16f22e664fc17a79f30caa5ad2c04fbc447549c2810fae 1462248 -1 1",
                             "cpu2006docs.tar.xz 4 055ce243071129412e9dd0b3b69a21654033a9b723d874b2015c774fac1553d9713be561ca86f74e4f16f22e664fc17a79f30caa5ad2c04fbc447549c2810fae 1428548 -1 2",
                             "cpu2006docs.tar.xz 4 055ce243071129412e9dd0b3b69a21654033a9b723d874b2015c774fac1553d9713be561ca86f74e4f16f22e664fc17a79f30caa5ad2c04fbc447549c2810fae 1034828 -1 3e",
                             "cpu2006docs.tar.xz 4 055ce243071129412e9dd0b3b69a21654033a9b723d874b2015c774fac1553d9713be561ca86f74e4f16f22e664fc17a79f30caa5ad2c04fbc447549c2810fae 1061968 -1 4",
                             "cpu2006docs.tar.xz 4 055ce243071129412e9dd0b3b69a21654033a9b723d874b2015c774fac1553d9713be561ca86f74e4f16f22e664fc17a79f30caa5ad2c04fbc447549c2810fae 1034588 -1 4e"),
        "600.perlbench_s" : ("-I. -I./lib makerand.pl", "-I. -I./lib test.pl"),
        "602.gcc_s"       : ("t1.c -O3 -finline-limit=50000 -o t1.opts-O3_-finline-limit_50000.s"),
        "603.bwaves_s"    : ("bwaves_1", "bwaves_2"),
        "605.mcf_s"       : ("inp.in"),
        "607.cactuBSSN_s" : ("spec_test.par"),
        "619.lbm_s"       : ("20 reference.dat 0 1 200_200_260_ldc.of"),
        "620.omnetpp_s"   : ("-c General -r 0"), 
##        "620.omnetpp_s"   : ("omnetpp.ini"), TODO this file exists as in spec2006
        "623.xalancbmk_s" : ("-v test.xml xalanc.xsl"),
        "625.x264_s"      : ("--dumpyuv 50 --frames 156 -o BuckBunny_New.264 BuckBunny.yuv 1280x720"),
        "631.deepsjeng_s" : ("test.txt"),
        "638.imagick_s"   : ("-limit disk 0 test_input.tga -shear 25 -resize 640x480 -negate -alpha Off test_output.tga"),
        "641.leela_s"     : ("test.sgf"),
        "644.nab_s"       : ("hkrdenq 1930344093 1000"),
        "648.exchange2_s" : ("0"),
        "657.xz_s"        : ("cpu2006docs.tar.xz 1 055ce243071129412e9dd0b3b69a21654033a9b723d874b2015c774fac1553d9713be561ca86f74e4f16f22e664fc17a79f30caa5ad2c04fbc447549c2810fae 650156 -1 0",
                             "cpu2006docs.tar.xz 1 055ce243071129412e9dd0b3b69a21654033a9b723d874b2015c774fac1553d9713be561ca86f74e4f16f22e664fc17a79f30caa5ad2c04fbc447549c2810fae 639996 -1 1",
                             "cpu2006docs.tar.xz 1 055ce243071129412e9dd0b3b69a21654033a9b723d874b2015c774fac1553d9713be561ca86f74e4f16f22e664fc17a79f30caa5ad2c04fbc447549c2810fae 637616 -1 2",
                             "cpu2006docs.tar.xz 1 055ce243071129412e9dd0b3b69a21654033a9b723d874b2015c774fac1553d9713be561ca86f74e4f16f22e664fc17a79f30caa5ad2c04fbc447549c2810fae 628996 -1 3e",
                             "cpu2006docs.tar.xz 1 055ce243071129412e9dd0b3b69a21654033a9b723d874b2015c774fac1553d9713be561ca86f74e4f16f22e664fc17a79f30caa5ad2c04fbc447549c2810fae 631912 -1 4",
                             "cpu2006docs.tar.xz 1 055ce243071129412e9dd0b3b69a21654033a9b723d874b2015c774fac1553d9713be561ca86f74e4f16f22e664fc17a79f30caa5ad2c04fbc447549c2810fae 629064 -1 4e",
                             "cpu2006docs.tar.xz 4 055ce243071129412e9dd0b3b69a21654033a9b723d874b2015c774fac1553d9713be561ca86f74e4f16f22e664fc17a79f30caa5ad2c04fbc447549c2810fae 1548636 1555348 0",
                             "cpu2006docs.tar.xz 4 055ce243071129412e9dd0b3b69a21654033a9b723d874b2015c774fac1553d9713be561ca86f74e4f16f22e664fc17a79f30caa5ad2c04fbc447549c2810fae 1462248 -1 1",
                             "cpu2006docs.tar.xz 4 055ce243071129412e9dd0b3b69a21654033a9b723d874b2015c774fac1553d9713be561ca86f74e4f16f22e664fc17a79f30caa5ad2c04fbc447549c2810fae 1428548 -1 2",
                             "cpu2006docs.tar.xz 4 055ce243071129412e9dd0b3b69a21654033a9b723d874b2015c774fac1553d9713be561ca86f74e4f16f22e664fc17a79f30caa5ad2c04fbc447549c2810fae 1034828 -1 3e",
                             "cpu2006docs.tar.xz 4 055ce243071129412e9dd0b3b69a21654033a9b723d874b2015c774fac1553d9713be561ca86f74e4f16f22e664fc17a79f30caa5ad2c04fbc447549c2810fae 1061968 -1 4",
                             "cpu2006docs.tar.xz 4 055ce243071129412e9dd0b3b69a21654033a9b723d874b2015c774fac1553d9713be561ca86f74e4f16f22e664fc17a79f30caa5ad2c04fbc447549c2810fae 1034588 -1 4e"),
        "996.specrand_fs" : ("324342 24239"),
        "997.specrand_fr" : ("324342 24239"),
        "998.specrand_is" : ("324342 24239"),
        "999.specrand_ir" : ("324342 24239")
    },

    # Train runs
    "train" : {
        "500.perlbench_r" : ("-I./lib diffmail.pl 2 550 15 24 23 100", "-I./lib perfect.pl b 3", "-I. -I./lib scrabbl.pl scrabbl.in", "-I./lib splitmail.pl 535 13 25 24 1091 1", "-I. -I./lib suns.pl"),
        "502.gcc_r"       : ("200.c -O3 -finline-limit=50000 -o 200.opts-O3_-finline-limit_50000.s",
                             "scilab.c -O3 -finline-limit=50000 -o scilab.opts-O3_-finline-limit_50000.s",
                             "train01.c -O3 -finline-limit=50000 -o train01.opts-O3_-finline-limit_50000.s"
                            ),
        "503.bwaves_r"    : ("bwaves_1", "bwaves_2"),
        "505.mcf_r"       : ("inp.in"),
        "507.cactuBSSN_r" : ("spec_train.par"),
        "508.namd_r"      : ("--input apoa1.input --iterations 7 --output apoa1.train.output"),
        "510.parest_r"    : ("train.prm"),
        "511.povray_r"    : ("SPEC-benchmark-train.ini"),
        "519.lbm_r"       : ("300 reference.dat 0 1 100_100_130_cf_b.of"),
        "520.omnetpp_r"   : ("-c General -r 0"),
##        "520.omnetpp_r"   : ("omnetpp.ini"), TODO this file exists as in spec2006
        "523.xalancbmk_r" : ("-v allbooks.xml xalanc.xsl "),
        "525.x264_r"      : ("--dumpyuv 50 --frames 142 -o BuckBunny_New.264 BuckBunny.yuv 1280x720"),
        "526.blender_r"   : ("sh5_reduced.blend --render-output sh5_reduced_ --threads 1 -b -F RAWTGA -s 234 -e 234 -a"),
        "531.deepsjeng_r" : ("train.txt"),
        "538.imagick_r"   : ("-limit disk 0 train_input.tga -resize 320x240 -shear 31 -edge 140 -negate -flop -resize 900x900 -edge 10 train_output.tga"),
        "541.leela_r"     : ("train.sgf"),
        "544.nab_r"       : ("aminos 391519156 1000", "gcn4dna 1850041461 300"),
        "548.exchange2_r" : ("1"),
        "557.xz_r"        : ("input.combined.xz 40 a841f68f38572a49d86226b7ff5baeb31bd19dc637a922a972b2e6d1257a890f6a544ecab967c313e370478c74f760eb229d4eef8a8d2836d233d3e9dd1430bf 6356684 -1 8",
                             "IMG_2560.cr2.xz 40 ec03e53b02deae89b6650f1de4bed76a012366fb3d4bdc791e8633d1a5964e03004523752ab008eff0d9e693689c53056533a05fc4b277f0086544c6c3cbbbf6 40822692 40824404 4",
                            ),
        "600.perlbench_s" : ("-I./lib diffmail.pl 2 550 15 24 23 100", "-I./lib perfect.pl b 3", "-I. -I./lib scrabbl.pl scrabbl.in", "-I./lib splitmail.pl 535 13 25 24 1091 1", "-I. -I./lib suns.pl"),
        "602.gcc_s"       : ("200.c -O3 -finline-limit=50000 -o 200.opts-O3_-finline-limit_50000.s",
                             "scilab.c -O3 -finline-limit=50000 -o scilab.opts-O3_-finline-limit_50000.s",
                             "train01.c -O3 -finline-limit=50000 -o train01.opts-O3_-finline-limit_50000.s"
                            ),
        "603.bwaves_s"    : ("bwaves_1", "bwaves_2"),
        "605.mcf_s"       : ("inp.in"),
        "607.cactuBSSN_s" : ("spec_train.par"),
        "619.lbm_s"       : ("300 reference.dat 0 1 200_200_260_ldc.of"),
        "620.omnetpp_s"   : ("-c General -r 0"),
##        "620.omnetpp_s"   : ("omnetpp.ini"), TODO this file exists as in spec2006
        "623.xalancbmk_s" : ("-v allbooks.xml xalanc.xsl "),
        "625.x264_s"      : ("--dumpyuv 50 --frames 142 -o BuckBunny_New.264 BuckBunny.yuv 1280x720"),
        "631.deepsjeng_s" : ("train.txt"),
        "638.imagick_s"   : ("-limit disk 0 train_input.tga -resize 320x240 -shear 31 -edge 140 -negate -flop -resize 900x900 -edge 10 train_output.tga"),
        "641.leela_s"     : ("train.sgf"),
        "644.nab_s"       : ("aminos 391519156 1000", "gcn4dna 1850041461 300"),
        "648.exchange2_s" : ("1"),
        "657.xz_s"        : ("input.combined.xz 40 a841f68f38572a49d86226b7ff5baeb31bd19dc637a922a972b2e6d1257a890f6a544ecab967c313e370478c74f760eb229d4eef8a8d2836d233d3e9dd1430bf 6356684 -1 8",
                             "IMG_2560.cr2.xz 40 ec03e53b02deae89b6650f1de4bed76a012366fb3d4bdc791e8633d1a5964e03004523752ab008eff0d9e693689c53056533a05fc4b277f0086544c6c3cbbbf6 40822692 40824404 4",
                            ),
         "996.specrand_fs": ("1 11"),
         "997.specrand_fr": ("1 11"),
         "998.specrand_is": ("1 11"),
         "999.specrand_ir": ("1 11")
    },

    # Reference runs
    "ref" : {
        "500.perlbench_r" : ("-I./lib checkspam.pl 2500 5 25 11 150 1 1 1 1", "-I./lib diffmail.pl 4 800 10 17 19 300", "-I./lib splitmail.pl 6400 12 26 16 100 0"),
        "502.gcc_r"       : ("gcc-pp.c -O3 -finline-limit=0 -fif-conversion -fif-conversion2 -o gcc-pp.opts-O3_-finline-limit_0_-fif-conversion_-fif-conversion2.s",
                             "gcc-pp.c -O2 -finline-limit=36000 -fpic -o gcc-pp.opts-O2_-finline-limit_36000_-fpic.s",
                             "gcc-smaller.c -O3 -fipa-pta -o gcc-smaller.opts-O3_-fipa-pta.s > gcc-smaller.opts-O3_-fipa-pta.out",
                             "ref32.c -O5 -o ref32.opts-O5.s",
                             "ref32.c -O3 -fselective-scheduling -fselective-scheduling2 -o ref32.opts-O3_-fselective-scheduling_-fselective-scheduling2.s"
                            ),
        "503.bwaves_r"    : ("bwaves_1", "bwaves_2", "bwaves_3", "bwaves_4"),
        "505.mcf_r"       : ("inp.in"),
        "507.cactuBSSN_r" : ("spec_ref.par"),
        "508.namd_r"      : ("--input apoa1.input --output apoa1.ref.output --iterations 65"),
        "510.parest_r"    : ("ref.prm"),
        "511.povray_r"    : ("SPEC-benchmark-ref.ini"),
        "519.lbm_r"       : ("3000 reference.dat 0 0 100_100_130_ldc.of"),
        "520.omnetpp_r"   : ("-c General -r 0"),
##        "520.omnetpp_r"   : ("omnetpp.ini"), TODO this file exists as in spec2006
        "523.xalancbmk_r" : ("-v t5.xml xalanc.xsl"),
        "525.x264_r"      : ("--pass 1 --stats x264_stats.log --bitrate 1000 --frames 1000 -o BuckBunny_New.264 BuckBunny.yuv 1280x720",
                             "--pass 2 --stats x264_stats.log --bitrate 1000 --dumpyuv 200 --frames 1000 -o BuckBunny_New.264 BuckBunny.yuv 1280x720",
                             "--seek 500 --dumpyuv 200 --frames 1250 -o BuckBunny_New.264 BuckBunny.yuv 1280x720"
                            ),
        "526.blender_r"   : ("sh3_no_char.blend --render-output sh3_no_char_ --threads 1 -b -F RAWTGA -s 849 -e 849 -a"),
        "531.deepsjeng_r" : ("ref.txt"),
        "538.imagick_r"   : ("-limit disk 0 refrate_input.tga -edge 41 -resample 181% -emboss 31 -colorspace YUV -mean-shift 19x19+15% -resize 30% refrate_output.tga"),
        "541.leela_r"     : ("ref.sgf"),
        "544.nab_r"       : ("1am0 1122214447 122"),
        "548.exchange2_r" : ("6"),
        "557.xz_r"        : ("cld.tar.xz 160 19cf30ae51eddcbefda78dd06014b4b96281456e078ca7c13e1c0c9e6aaea8dff3efb4ad6b0456697718cede6bd5454852652806a657bb56e07d61128434b474 59796407 61004416 6",
                             "cpu2006docs.tar.xz 250 055ce243071129412e9dd0b3b69a21654033a9b723d874b2015c774fac1553d9713be561ca86f74e4f16f22e664fc17a79f30caa5ad2c04fbc447549c2810fae 23047774 23513385 6e",
                             "input.combined.xz 250 a841f68f38572a49d86226b7ff5baeb31bd19dc637a922a972b2e6d1257a890f6a544ecab967c313e370478c74f760eb229d4eef8a8d2836d233d3e9dd1430bf 40401484 41217675 7"
                            ),
        "600.perlbench_s" : ("-I./lib checkspam.pl 2500 5 25 11 150 1 1 1 1", "-I./lib diffmail.pl 4 800 10 17 19 300", "-I./lib splitmail.pl 6400 12 26 16 100 0"),
        "602.gcc_s"       : ("gcc-pp.c -O5 -fipa-pta -o gcc-pp.opts-O5_-fipa-pta.s",
                             "gcc-pp.c -O5 -finline-limit=1000 -fselective-scheduling -fselective-scheduling2 -o gcc-pp.opts-O5_-finline-limit_1000_-fselective-scheduling_-fselective-scheduling2.s",
                             "gcc-pp.c -O5 -finline-limit=24000 -fgcse -fgcse-las -fgcse-lm -fgcse-sm -o gcc-pp.opts-O5_-finline-limit_24000_-fgcse_-fgcse-las_-fgcse-lm_-fgcse-sm.s"),
        "603.bwaves_s"    : ("bwaves_1", "bwaves_2"),
        "605.mcf_s"       : ("inp.in"),
        "607.cactuBSSN_s" : ("spec_ref.par"),
        "619.lbm_s"       : ("2000 reference.dat 0 0 200_200_260_ldc.of"),
        "620.omnetpp_s"   : ("-c General -r 0"),
##        "620.omnetpp_s"   : ("omnetpp.ini"), TODO this file exists as in spec2006
        "623.xalancbmk_s" : ("-v t5.xml xalanc.xsl"),
        "625.x264_s"      : ("--pass 1 --stats x264_stats.log --bitrate 1000 --frames 1000 -o BuckBunny_New.264 BuckBunny.yuv 1280x720",
                             "--pass 2 --stats x264_stats.log --bitrate 1000 --dumpyuv 200 --frames 1000 -o BuckBunny_New.264 BuckBunny.yuv 1280x720",
                             "--seek 500 --dumpyuv 200 --frames 1250 -o BuckBunny_New.264 BuckBunny.yuv 1280x720"
                            ),
        "631.deepsjeng_s" : ("ref.txt"),
        "638.imagick_s"   : ("-limit disk 0 refspeed_input.tga -resize 817% -rotate -2.76 -shave 540x375 -alpha remove -auto-level -contrast-stretch 1x1% -colorspace Lab -channel R -equalize +channel -colorspace sRGB -define histogram:unique-colors=false -adaptive-blur 0x5 -despeckle -auto-gamma -adaptive-sharpen 55 -enhance -brightness-contrast 10x10 -resize 30% refspeed_output.tga"),
        "641.leela_s"     : ("ref.sgf"),
        "644.nab_s"       : ("3j1n 20140317 220"),
        "648.exchange2_s" : ("6"),
        "657.xz_s"        : ("cld.tar.xz 1400 19cf30ae51eddcbefda78dd06014b4b96281456e078ca7c13e1c0c9e6aaea8dff3efb4ad6b0456697718cede6bd5454852652806a657bb56e07d61128434b474 536995164 539938872 8",
                             "cpu2006docs.tar.xz 6643 055ce243071129412e9dd0b3b69a21654033a9b723d874b2015c774fac1553d9713be561ca86f74e4f16f22e664fc17a79f30caa5ad2c04fbc447549c2810fae 1036078272 1111795472 4"),
        "996.specrand_fs" : ("1255432124 234923"),
        "997.specrand_fr" : ("1255432124 234923"),
        "998.specrand_is" : ("1255432124 234923"),
        "999.specrand_ir" : ("1255432124 234923")
    }
}

# Parameters provided via redirection command: : "/.[benchmark] < param "
input = {
    "test" : {
        "503.bwaves_r"    : ("bwaves_1.in", "bwaves_2.in"),
        "554.roms_r"      : ("ocean_benchmark0.in.x"),
        "603.bwaves_s"    : ("bwaves_1.in", "bwaves_2.in"),
        "654.roms_s"      : ("ocean_benchmark0.in.x")
    },
    "train" : {
#        "500.perlbench_r" : ("", "", "scrabbl.in", "", ""),
        "503.bwaves_r"    : ("bwaves_1.in", "bwaves_2.in"),
        "554.roms_r"      : ("ocean_benchmark1.in.x"),
#        "600.perlbench_s" : ("", "", "scrabbl.in", "", ""),
        "603.bwaves_s"    : ("bwaves_1.in", "bwaves_2.in"),
        "654.roms_s"      : ("ocean_benchmark1.in.x")
    },
    "ref" : {
        "503.bwaves_r"    : ("bwaves_1.in", "bwaves_2.in", "bwaves_3.in", "bwaves_4.in"),
        "554.roms_r"      : ("ocean_benchmark2.in.x"),
        "603.bwaves_s"    : ("bwaves_1.in", "bwaves_2.in"),
        "654.roms_s"      : ("ocean_benchmark3.in.x")
    }
}

# Helper function for benchmark preprocessing (not always needed)
def get_preprocessing(b_name, arch_bits, endianness):
    # Nothing here yet
    return preprocessing.get(b_name)
