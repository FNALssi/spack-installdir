import os
import sys
import json

from spack import spack_version
import spack.main
import spack.spec
import spack.store
import spack.hooks
import spack.hooks.module_file_generation
import spack.environment as ev
try:
    import spack.vendor.ruamel.yaml
except:
    import _vendoring.ruamel.yaml
try:
    from spack.llnl.util import lang, tty
except:
    from llnl.util import lang, tty

from spack.cmd.install import install_with_active_env, install_without_active_env

def get_tuple():
    host_platform = spack.platforms.host()
    host_os = host_platform.operating_system("default_os")
    host_target = host_platform.target("default_target")
    generic_target = host_platform.target("fe").microarchitecture.generic.name
    return (str(host_platform), str(host_os), str(generic_target))


def run_command(s):
    tty.debug("--> running: %s" % s)
    os.system(s)


def get_compiler():
    f = os.popen("spack compiler list", "r")
    for line in f:
        comp = line
    f.close()
    return comp.strip()


def make_repo_if_needed(name):
    f = os.popen("spack repo list", "r")
    for line in f:
        if line.find(f"{name} ") >= 0:
            f.close()
            rd = line[line.rfind(" ") :].strip()
            return rd
    f.close()
    if spack_version > "1.0":
        rd = f"{os.environ['SPACK_ROOT']}/var/spack/repos/{name}/spack_repo/{name}" 
    else:
        rd = f"{os.environ['SPACK_ROOT']}/var/spack/repos/{name}"
    run_command("spack repo create %s %s" % (rd, name))
    run_command("spack repo add --scope=site %s" % rd)
    return rd


def UPPER(name):
    return name.upper().replace("-", "_")


def CamelCase(name):
    name = name[0].upper() + name[1:]
    pos = name.find("-")
    while pos != -1:
        name = name[:pos] + name[pos + 1].upper() + name[pos + 2 :]
        pos = name.find("-")
    return name


def make_recipe(namespace, name, version, tarfile, pathvar="IGNORE"):

    rd = make_repo_if_needed(namespace)

    # rewrite recipe if present with new tarfile...

    tty.debug("recipe: %s/packages/%s/package.py" % (rd, name))
    if os.path.exists("%s/packages/%s/package.py" % (rd, name)):
        tty.info("saving recipe")
        os.rename(
            "%s/packages/%s/package.py" % (rd, name),
            "%s/packages/%s/package.py.save" % (rd, name),
        )
    else:
        os.makedirs(f"{rd}/packages/{name}", exist_ok=True)

    with open(f"{rd}/packages/{name}/package.py", "w") as rout:
        rout.write(
            f"""
            # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
            # recipe created by spack-installdir
            # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

            from spack.package import *

            class {CamelCase(name)} (Package):
                '''{name} -- locally declared bundle of files'''

                homepage = 'https://nowhere.org/nosuch/'
                url = 'file:///tmp/{name}.v{version}.tgz'

                version('{version}')

                def url_for_version(self,version):
                    url = 'file:///tmp/{name}.v{{0}}.tgz'
                    return url.format(version)


                def install(self, spec, prefix):
                    install_tree(self.stage.source_path, prefix)

                def setup_run_environment(self, run_env):
                    run_env.set('{UPPER(name)}_DIR', self.prefix)

            """.replace(
                "\n" + " " * 12, "\n"
            )
        )


def make_tarfile(directory, name, version):
    if directory:
        directory = f"cd {directory} &&"
    else:
        directory = ""
    tfn = "/tmp/%s.v%s.tgz" % (name, version)
    os.system(f"{directory} tar czvf %s ." % tfn)
    return tfn


def restore_recipe(namespace, name):

    rd = make_repo_if_needed(namespace)

    # restore recipe if present with new tarfile...

    tty.debug("recipe: %s/packages/%s/package.py" % (rd, name))
    if os.path.exists("%s/packages/%s/package.py.save" % (rd, name)):
        tty.info("restoring recipe")
        os.rename(
            "%s/packages/%s/package.py.save" % (rd, name),
            "%s/packages/%s/package.py" % (rd, name),
        )


def install_directory(args):
    name, version = args.spec.replace("=", "").split("@")
    tfn = make_tarfile(args.directory, name, version)
    make_recipe(args.namespace, name, version, tfn, "PATH")
    # ===
    # was: os.system("spack install --no-checksum %s@%s" % (name, version))
    # now:
    #
    argv = [
        "-k",
        "install",
        "--no-checksum",
        "--use-buildcache", "never",
        f"{name}@={version}",
    ]

    spack.main.main(argv)

    restore_recipe(args.namespace, name)
