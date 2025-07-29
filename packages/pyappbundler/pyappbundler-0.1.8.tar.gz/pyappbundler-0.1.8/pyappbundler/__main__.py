import argparse
import logging

from .pyappbundler import exe, exe_and_setup


parser = argparse.ArgumentParser(
    prog='pyappbundler',
    description="""Automate bundle a Python application and all its
        dependencies into a single package with PyInstaller
        (https://pyinstaller.org/en/stable). And then (for Windows), put it all into
        a setup file with Inno Setup (https://jrsoftware.org/isdl.php#stable).""",
)

parser.add_argument(
    'target', help='target python script')
parser.add_argument(
    '-a', '--app-name', default='',
    help="""Application name.
        If not specified, then it calculates from "target" value.""")
parser.add_argument(
    '-i', '--icon', default='', help='application icon')
parser.add_argument(
    '-g', '--app-guid', default='',
    help='Application GUID. Required for setup building!')
parser.add_argument(
    '-v', '--app-ver', default='',
    help='Application version. Required for setup building!')

parser.add_argument(
    '-r', '--res-dir', action="extend", nargs=1,
    help="""Directory with additional files to be added to the executable.
        Multiple definitions are allowed.""")
parser.add_argument(
    '-f', '--pyinst-flag', action="extend", nargs=1,
    help=f"""FLAG-argument (without "--" prefix) for PyInstaller.
        Multiple definitions are allowed.
        Example: "... -f windowed -f clean ..." will pass "--windowed"
        and "--clean" flags to PyInstaller during application bundling.""")

parser.add_argument(
    '--dist-dir', default='dist',
    help='Distribution directory path. "dist" byte default.')
parser.add_argument(
    '--build-dir', default='build',
    help='Where PyInstaller put all the temporary work files. "build" by default.')
parser.add_argument(
    '--no-clean-dist', action='store_true',
    help='cancel cleaning dist directory before building')
parser.add_argument(
    '--no-setup', action='store_true',
    help='build exe without setup-file')

args = parser.parse_args()

#
logging.basicConfig(
    format='%(levelname)s: %(message)s',
    level=logging.INFO,
)

#
bundler_args = {
    'target': args.target, 'app_name': args.app_name, 'icon': args.icon,
    'dist': args.dist_dir, 'build': args.build_dir,
    'res_dirs': args.res_dir, 'pyinst_flags': args.pyinst_flag,
    'no_clean_dist': args.no_clean_dist,
}

if args.no_setup:
    exe(**bundler_args)
else:
    bundler_args['app_guid'] = args.app_guid
    bundler_args['app_ver'] = args.app_ver

    exe_and_setup(**bundler_args)
