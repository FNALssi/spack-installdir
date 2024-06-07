

## Spack-subspack

a [Spack extension](https://spack.readthedocs.io/en/latest/extensions.html#custom-extensions) to install a directory full of files as a spack pagckage.

This includes:
* adding a recipe for the package if needed
* instaling the package

### Usage

In most cases you can just do:

  spack installdir package@version

to add the current directory tree as a version of the package.
* --directory /path/to/directory  specify a directory other then the current directory
* --namespace name specify the namespace to create the recipe in. 

You can also edit the recipe with spack edit and add a "setup_run_environment()" method if you need the package to set environment variables, etc.

### Installation

After cloning the repository somewhere, See the [Spack docs](https://spack.readthedocs.io/en/latest/extensions.html#configure-spack-to-use-extensions) on adding the path to config.yaml under 'extensions:'
