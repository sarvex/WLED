Import('env')
import os
import shutil
import gzip

OUTPUT_DIR = f"build_output{os.path.sep}"

def _get_cpp_define_value(env, define):
    if define_list := [
        item[-1] for item in env["CPPDEFINES"] if item[0] == define
    ]:
        return define_list[0]

    return None

def _create_dirs(dirs=["firmware", "map"]):
    # check if output directories exist and create if necessary
    if not os.path.isdir(OUTPUT_DIR):
        os.mkdir(OUTPUT_DIR)

    for d in dirs:
        if not os.path.isdir(f"{OUTPUT_DIR}{d}"):
            os.mkdir(f"{OUTPUT_DIR}{d}")

def bin_rename_copy(source, target, env):
    _create_dirs()
    variant = env["PIOENV"]

    # create string with location and file names based on variant
    map_file = f"{OUTPUT_DIR}map{os.path.sep}{variant}.map"
    bin_file = f"{OUTPUT_DIR}firmware{os.path.sep}{variant}.bin"

    if release_name := _get_cpp_define_value(env, "WLED_RELEASE_NAME"):
        _create_dirs(["release"])
        version = _get_cpp_define_value(env, "WLED_VERSION")
        release_file = f"{OUTPUT_DIR}release{os.path.sep}WLED_{version}_{release_name}.bin"
        shutil.copy(str(target[0]), release_file)

    # check if new target files exist and remove if necessary
    for f in [map_file, bin_file]:
        if os.path.isfile(f):
            os.remove(f)

    # copy firmware.bin to firmware/<variant>.bin
    shutil.copy(str(target[0]), bin_file)

    # copy firmware.map to map/<variant>.map
    if os.path.isfile("firmware.map"):
        shutil.move("firmware.map", map_file)

def bin_gzip(source, target, env):
    _create_dirs()
    variant = env["PIOENV"]

    # create string with location and file names based on variant
    bin_file = f"{OUTPUT_DIR}firmware{os.path.sep}{variant}.bin"
    gzip_file = f"{OUTPUT_DIR}firmware{os.path.sep}{variant}.bin.gz"

    # check if new target files exist and remove if necessary
    if os.path.isfile(gzip_file): os.remove(gzip_file)

    # write gzip firmware file
    with open(bin_file,"rb") as fp:
        with gzip.open(gzip_file, "wb", compresslevel = 9) as f:
            shutil.copyfileobj(fp, f)

env.AddPostAction("$BUILD_DIR/${PROGNAME}.bin", [bin_rename_copy, bin_gzip])
