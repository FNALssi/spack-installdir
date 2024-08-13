import sys
import spack.config
from spack.extensions import installdir as idir

description = "package up a directory as a spack package"
section = "packaging"
level = "short"


def setup_parser(subparser):

    subparser.add_argument(
        "--directory",
        default = None,
        help="directory with files to install, defaults to $PWD"
    )
    subparser.add_argument(
        "--namespace",
        default = "local",
        help="namespace in which to (re)write package recipe"
    )
    subparser.add_argument(
        "spec",
        help="simplified spec: package@version",
    )

    
def installdir(parser, args):
    #print("parser is " + repr(parser) + "args: " + repr(args))
    idir.install_directory(args)
