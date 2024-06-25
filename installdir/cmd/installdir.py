import sys
import spack.config
from spack.extensions import installdir as sext

description = "package up a directory as a spack package"
section = "basic"
level = "short"


def setup_parser(subparser):

    scopes = spack.config.scopes()

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
    sext.install_directory(args)
