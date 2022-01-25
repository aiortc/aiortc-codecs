import os
import platform
import shutil
import subprocess
import sys

if len(sys.argv) < 2:
    sys.stderr.write("Usage: build-codecs.py <prefix>\n")
    sys.exit(1)

dest_dir = sys.argv[1]
build_dir = os.path.abspath("build")
patch_dir = os.path.abspath("patches")
source_dir = os.path.abspath("source")

for d in [build_dir, dest_dir]:
    if os.path.exists(d):
        shutil.rmtree(d)


def build(package, configure_args=[]):
    path = os.path.join(build_dir, package)
    os.chdir(path)
    run(["./configure"] + configure_args + ["--prefix=" + dest_dir])
    run(["make", "-j"])
    run(["make", "install"])
    os.chdir(build_dir)


def prepend_env(name, new, separator=" "):
    old = os.environ.get(name)
    if old:
        os.environ[name] = new + separator + old
    else:
        os.environ[name] = new


def extract(package, url, *, strip_components=1):
    path = os.path.join(build_dir, package)
    patch = os.path.join(patch_dir, package + ".patch")
    tarball = os.path.join(source_dir, url.split("/")[-1])

    # download tarball
    if not os.path.exists(tarball):
        run(["curl", "-L", "-o", tarball, url])

    # extract tarball
    os.mkdir(path)
    run(["tar", "xf", tarball, "-C", path, "--strip-components", str(strip_components)])

    # apply patch
    if os.path.exists(patch):
        run(["patch", "-d", path, "-i", patch, "-p1"])


def run(cmd):
    sys.stdout.write(f"- Running: {cmd}")
    subprocess.run(cmd, check=True, stderr=sys.stderr.buffer, stdout=sys.stdout.buffer)


system = platform.system()
if system == "Linux":
    machine = platform.machine()
    output_dir = "/output"
    output_tarball = os.path.join(output_dir, f"codecs-manylinux_{machine}.tar.gz")
elif system == "Darwin":
    # cibuildwheel sets ARCHFLAGS:
    # https://github.com/pypa/cibuildwheel/blob/5255155bc57eb6224354356df648dc42e31a0028/cibuildwheel/macos.py#L207-L220
    machine = os.environ["ARCHFLAGS"].split()[1]
    output_dir = os.path.abspath("output")
    output_tarball = os.path.join(output_dir, f"codecs-macos_{machine}.tar.gz")
else:
    raise Exception("Unsupported system: %s" % system)

for d in [build_dir, output_dir, source_dir]:
    if not os.path.exists(d):
        os.mkdir(d)
if not os.path.exists(output_tarball):
    os.chdir(build_dir)

    prepend_env("CPPFLAGS", "-I" + os.path.join(dest_dir, "include"))
    prepend_env("LDFLAGS", "-L" + os.path.join(dest_dir, "lib"))
    prepend_env("PATH", os.path.join(dest_dir, "bin"), separator=":")
    prepend_env(
        "PKG_CONFIG_PATH", os.path.join(dest_dir, "lib", "pkgconfig"), separator=":"
    )

    #### BUILD TOOLS ####

    # install nasm
    extract(
        "nasm",
        "https://www.nasm.us/pub/nasm/releasebuilds/2.14.02/nasm-2.14.02.tar.bz2",
    )
    build("nasm")

    #### CODECS ###

    # build opus
    extract("opus", "https://archive.mozilla.org/pub/opus/opus-1.3.1.tar.gz", )
    build("opus", ["--disable-shared", "--enable-static", "--with-pic"])

    # build vpx
    extract("vpx", "https://github.com/webmproject/libvpx/archive/v1.10.0.tar.gz")
    build("vpx", ["--disable-examples", "--disable-tools", "--disable-unit-tests", "--enable-pic"])

    run(["tar", "czvf", output_tarball, "-C", dest_dir, "include", "lib"])
