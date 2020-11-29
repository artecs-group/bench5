benchmarks = (
    "400.perlbench",
    "401.bzip2",
    "403.gcc",
    "410.bwaves",
    "416.gamess",
    "429.mcf",
    "433.milc",
    "434.zeusmp",
    "435.gromacs",
    "436.cactusADM",
    "437.leslie3d",
    "444.namd",
    "445.gobmk",
    "447.dealII",
    "450.soplex",
    "453.povray",
    "454.calculix",
    "456.hmmer",
    "458.sjeng",
    "459.GemsFDTD",
    "462.libquantum",
    "464.h264ref",
    "465.tonto",
    "470.lbm",
    "471.omnetpp",
    "473.astar",
    "481.wrf",
    "482.sphinx3",
    "483.xalancbmk",
    "998.specrand",
    "999.specrand"
)


exe_name = {
    "482.sphinx3"       : "sphinx_livepretend",
    "483.xalancbmk"     : "Xalan"
}


preprocessing = {
    "481.wrf"           : ("ln -s le/32/* .", "ln -s le/64/* .", "ln -s be/32/* .", "ln -s be/64/* ."),
    "482.sphinx3"       : ("rm *.be.raw && for file in *.le.raw; do mv \"$file\" \"${file%.le.raw}.raw\"; done && wc -c $(ls *.raw) | awk -F\".raw\" \'{print $1}\' | awk \'{print $2 \" \" $1}\' | head -n -1 > ctlfile",
                           "rm *.le.raw && for file in *.be.raw; do mv \"$file\" \"${file%.be.raw}.raw\"; done && wc -c $(ls *.raw) | awk -F\".raw\" \'{print $1}\' | awk \'{print $2 \" \" $1}\' | head -n -1 > ctlfile")
}


mem_size = {
    "train" : {
        "459.GemsFDTD"      : "4GB",
        "465.tonto"         : "4GB",
        "481.wrf"           : "4GB"
    }
}


subset = {
    "test" : {
        "400.perlbench"     : ("attrs", "gv", "makerand", "pack", "redef", "ref", "regmesg", "test"),
        "401.bzip2"         : ("dryer_2", "input_program_5"),
        "445.gobmk"         : ("capture", "connection", "connection_rot", "connect", "connect_rot", "cutstone", "dniwog")
    },
    "train" : {
        "400.perlbench"     : ("perfect", "scrabbl", "suns"),
        "401.bzip2"         : ("byoudoin_5", "input_combined_80", "input_program_10"),
        "445.gobmk"         : ("arb", "arend", "arion", "atari", "blunder", "buzco", "nicklas2", "nicklas4"),
        "450.soplex"        : ("pds-20", "train"),
        "473.astar"         : ("BigLakes1024", "rivers")
    },
    "ref" : {
        "400.perlbench"     : ("checkspam", "diffmail", "splitmail"),
        "401.bzip2"         : ("input_source_280", "chicken_30", "liberty_30", "input_program_10", "text_280", "input_combined_200"),
        "403.gcc"           : ("166", "200", "c-typeck", "cp-decl", "expr", "expr2", "g23", "s04", "scilab"),
        "416.gamess"        : ("cytosine_2", "h2ocu2+_gradient", "triazolium"),
        "445.gobmk"         : ("13x13", "nngs", "score2", "trevorc", "trevord"),
        "450.soplex"        : ("pds-50", "ref"),
        "456.hmmer"         : ("nph3", "retro"),
        "464.h264ref"       : ("foreman_ref_encoder_baseline", "foreman_ref_encoder_main", "sss_encoder_main"),
        "473.astar"         : ("BigLakes2048", "rivers")
        # Yet to fill
    }
}


params = {
    "test" : {
        "400.perlbench"     : ("-I. -I./lib attrs.pl", "-I. -I./lib gv.pl", "-I. -I./lib makerand.pl", "-I. -I./lib pack.pl", "-I. -I./lib redef.pl", "-I. -I./lib ref.pl", "-I. -I./lib regmesg.pl", "-I. -I./lib test.pl"),
        "401.bzip2"         : ("dryer.jpg 2", "input.program 5"),
        "403.gcc"           : ("cccp.in -o cccp.s"),
        "410.bwaves"        : ("bwaves.in"),
        "429.mcf"           : ("inp.in"),
        "435.gromacs"       : ("-silent -deffnm gromacs -nice 0"),
        "436.cactusADM"     : ("benchADM.par"),
        "444.namd"          : ("--input namd.input --iterations 1 --output namd.out"),
        "445.gobmk"         : ("--quiet --mode gtp", "--quiet --mode gtp", "--quiet --mode gtp", "--quiet --mode gtp", "--quiet --mode gtp", "--quiet --mode gtp", "--quiet --mode gtp"),
        "447.dealII"        : ("8"),
        "450.soplex"        : ("-m10000 test.mps"),
        "453.povray"        : ("SPEC-benchmark-test.ini"),
        "454.calculix"      : ("-i beampic"),
        "456.hmmer"         : ("--fixed 0 --mean 325 --num 45000 --sd 200 --seed 0 bombesin.hmm"),
        "458.sjeng"         : ("test.txt"),
        "462.libquantum"    : ("33 5"),
        "464.h264ref"       : ("-d foreman_test_encoder_baseline.cfg"),
        "470.lbm"           : ("20 reference.dat 0 1 100_100_130_cf_a.of"),
        "471.omnetpp"       : ("omnetpp.ini"),
        "473.astar"         : ("lake.cfg"),
        "482.sphinx3"       : ("ctlfile . args.an4"),
        "483.xalancbmk"     : ("-v test.xml xalanc.xsl"),
        "998.specrand"      : ("1 3"),
        "999.specrand"      : ("1 3")
    },
    "train" : {
        "400.perlbench"     : ("-I. -I./lib perfect.pl", "-I. -I./lib scrabbl.pl", "-I. -I./lib suns.pl"),
        "401.bzip2"         : ("byoudoin.jpg 5", "input.combined 80", "input.program 10"),
        "403.gcc"           : ("integrate.in -o integrate.s"),
        "410.bwaves"        : ("bwaves.in"),
        "429.mcf"           : ("inp.in"),
        "435.gromacs"       : ("-silent -deffnm gromacs -nice 0"),
        "436.cactusADM"     : ("benchADM.par"),
        "444.namd"          : ("--input namd.input --iterations 1 --output namd.out"),
        "445.gobmk"         : ("--quiet --mode gtp", "--quiet --mode gtp", "--quiet --mode gtp", "--quiet --mode gtp", "--quiet --mode gtp", "--quiet --mode gtp", "--quiet --mode gtp", "--quiet --mode gtp"),
        "447.dealII"        : ("10"),
        "450.soplex"        : ("-s1 -e -m5000 pds-20.mps", "-m1200 train.mps"),
        "453.povray"        : ("SPEC-benchmark-train.ini"),
        "454.calculix"      : ("-i stairs"),
        "456.hmmer"         : ("--fixed 0 --mean 425 --num 85000 --sd 300 --seed 0 leng100.hmm"),
        "458.sjeng"         : ("train.txt"),
        "462.libquantum"    : ("143 25"),
        "464.h264ref"       : ("-d foreman_train_encoder_baseline.cfg"),
        "470.lbm"           : ("300 reference.dat 0 1 100_100_130_cf_b.of"),
        "471.omnetpp"       : ("omnetpp.ini"),
        "473.astar"         : ("BigLakes1024.cfg", "rivers1.cfg"),
        "482.sphinx3"       : ("ctlfile . args.an4"),
        "483.xalancbmk"     : ("-v allbooks.xml xalanc.xsl"),
        "998.specrand"      : ("324342 24239"),
        "999.specrand"      : ("324342 24239")
    },
    "ref" : {
        "400.perlbench"     : ("-I. -I./lib checkspam.pl", "-I. -I./lib diffmail.pl", "-I. -I./lib splitmail.pl"),
        "401.bzip2"         : ("input.source 280", "chicken.jpg 30", "liberty.jpg 30", "input.program 10", "text.html 280", "input.combined 200"),
        "403.gcc"           : ("166.in -o 166.s", "200.in -o 200.s", "c-typeck.in -o c-typeck.s", "cp-decl.in -o cp-decl.s", "expr.in -o expr.s", "expr2.in -o expr2.s", "g23.in -o g23.s", "s04.in -o s04.s", "scilab.in -o scilab.s"),
        "410.bwaves"        : ("bwaves.in"),
        "429.mcf"           : ("inp.in"),
        "435.gromacs"       : ("-silent -deffnm gromacs -nice 0"),
        "436.cactusADM"     : ("benchADM.par"),
        "444.namd"          : ("--input namd.input --iterations 38 --output namd.out"),
        "445.gobmk"         : ("--quiet --mode gtp", "--quiet --mode gtp", "--quiet --mode gtp", "--quiet --mode gtp", "--quiet --mode gtp"),
        "447.dealII"        : ("23"),
        "450.soplex"        : ("-s1 -e -m4500 pds-50.mps", "-m3500 ref.mps"),
        "453.povray"        : ("SPEC-benchmark-ref.ini"),
        "454.calculix"      : ("-i hyperviscoplastic"),
        "456.hmmer"         : ("nph3.hmm swiss41", "--fixed 0 --mean 500 --num 500000 --sd 350 --seed 0 retro.hmm"),
        "458.sjeng"         : ("ref.txt"),
        "462.libquantum"    : ("1397 8"),
        "464.h264ref"       : ("-d foreman_ref_encoder_baseline.cfg", "-d foreman_ref_encoder_main.cfg", " -d sss_encoder_main.cfg"),
        "470.lbm"           : ("3000 reference.dat 0 0 100_100_130_ldc.of"),
        "471.omnetpp"       : ("omnetpp.ini"),
        "473.astar"         : ("BigLakes2048.cfg", "rivers.cfg"),
        "482.sphinx3"       : ("ctlfile . args.an4"),
        "483.xalancbmk"     : ("-v t5.xml xalanc.xsl"),
        "998.specrand"      : ("1255432124 234923"),
        "999.specrand"      : ("1255432124 234923")
    }
}


input = {
    "test" : {
        "465.tonto"         : ("stdin"),
        "416.gamess"        : ("exam29.config"),
        "433.milc"          : ("su3imp.in"),
        "437.leslie3d"      : ("leslie3d.in"),
        "445.gobmk"         : ("capture.tst", "connection.tst", "connection_rot.tst", "connect.tst", "connect_rot.tst", "cutstone.tst", "dniwog.tst")
    },
    "train" : {
        "465.tonto"         : ("stdin"),
        "416.gamess"        : ("h2ocu2+_energy.config"),
        "433.milc"          : ("su3imp.in"),
        "437.leslie3d"      : ("leslie3d.in"),
        "445.gobmk"         : ("arb.tst", "arend.tst", "arion.tst", "atari.tst", "blunder.tst", "buzco.tst", "nicklas2.tst", "nicklas4.tst")
    },
    "ref" : {
        "416.gamess"        : ("cytosine.2.config", " h2ocu2+.gradient.config", "triazolium.config"),
        "433.milc"          : ("su3imp.in"),
        "437.leslie3d"      : ("leslie3d.in"),
        "445.gobmk"         : ("13x13.tst", "nngs.tst", "score2.tst",  "trevorc.tst", "trevord.tst"),
        "465.tonto"         : ("stdin")
    }
}


def get_preprocessing(b_name, arch_bits, endianness):
    if b_name == "481.wrf":
        if endianness == "le":
            if arch_bits == 32:
                return preprocessing[b_name][0]
            else:
                return preprocessing[b_name][1]
        else:
            if arch_bits == 32:
                return preprocessing[b_name][2]
            else:
                return preprocessing[b_name][3]
    elif b_name == "482.sphinx3":
        if endianness == "le":
            return preprocessing[b_name][0]
        else:
            return preprocessing[b_name][1]

    return preprocessing.get(b_name)
