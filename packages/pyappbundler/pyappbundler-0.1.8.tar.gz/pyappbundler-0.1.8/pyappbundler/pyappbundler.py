from pathlib import Path
import shutil
import logging
import subprocess

import PyInstaller.__main__
import jinja2


def exe(
    target, *,
    app_name='', icon='', dist='dist', build='build',
    res_dirs: list = None, pyinst_flags: list = None,
    no_clean_dist=False, optimize=1,
):
    Bundler(
        target,
        app_name=app_name, icon=icon,
        dist=dist, build=build,
        res_dirs=res_dirs, pyinst_flags=pyinst_flags,
        no_clean_dist=no_clean_dist, optimize=optimize,
    ).clean_dist().build_exe()


def exe_and_setup(
    target, *,
    app_name='', icon='', app_guid, app_ver, dist='dist', build='build',
    res_dirs: list = None, pyinst_flags: list = None,
    no_clean_dist=False, optimize=1,
):
    Bundler(
        target,
        app_name=app_name, icon=icon,
        app_guid=app_guid, app_ver=app_ver,
        dist=dist, build=build,
        res_dirs=res_dirs, pyinst_flags=pyinst_flags,
        no_clean_dist=no_clean_dist, optimize=optimize,
    ).clean_dist().build_exe().build_setup()


class Bundler:
    def __init__(
        self, target, *,
        app_name='', icon='', app_guid='', app_ver='', dist='dist', build='build',
        res_dirs: list = None, pyinst_flags: list = None,
        no_clean_dist=False, optimize=1,
    ):
        self.target = Path(target).resolve()

        if app_name:
            self.app_name = app_name
        else:
            self.app_name = self.target.stem

        if icon:
            self.icon = Path(icon).resolve()
        else:
            self.icon = icon

        #
        self.app_guid, self.app_ver = app_guid, app_ver
        self.dist, self.build = Path(dist).resolve(), Path(build).resolve()

        self.res_dirs, self.pyinst_flags = res_dirs, pyinst_flags
        self.no_clean_dist, self.optimize = no_clean_dist, optimize

    def clean_dist(self):
        if self.no_clean_dist:
            logging.info(f'Cancel cleaning "{self.dist}" directory.')
            return self

        #
        logging.info(f'Cleaning "{self.dist}" directory...')

        if not self.dist.exists():
            self.dist.mkdir(parents=True)
            logging.info(
                f'"{self.dist}" directory doesn\'t exist!'
                ' The new one has been created.')
            return self

        if not self.dist.is_dir():
            raise FileNotFoundError(
                f'Directory expected, but "{self.dist}" is not!')

        for path in self.dist.iterdir():
            if path.is_file():
                path.unlink()
            elif path.is_dir():
                shutil.rmtree(path)

        logging.info(f'"{self.dist}" directory has been cleaned!\n')

        return self

    def build_exe(self):
        logging.info(f'Building exe with PyInstaller...')

        args = [
            str(self.target),
            '--name', self.app_name,
            '--distpath', str(self.dist),
            '--workpath', str(self.build),
            '--optimize', str(self.optimize),
        ]

        if self.icon:
            args.extend(['--icon', str(self.icon)])
        else:
            args.extend(['--icon', 'NONE'])

        if self.pyinst_flags:
            for flag in self.pyinst_flags:
                if len(flag) == 1:
                    args.append(f'-{flag}')
                else:
                    args.append(f'--{flag}')

        if self.res_dirs:
            for directory in self.res_dirs:
                directory_path = Path(directory).resolve()
                if not directory_path.is_dir():
                    raise FileNotFoundError(
                        f'Directory expected, but "{directory_path}" is not!')
                args.extend(['--add-data', f'{directory_path};{directory_path.name}'])

        PyInstaller.__main__.run(args)

        return self

    def build_setup(self):
        """ Inno Setup 6 required (+record in sys PATH).
            https://jrsoftware.org/isdl.php#stable
        """
        if not self.app_guid:
            raise ValueError('"app_guid" is required!')
        if not self.app_ver:
            raise ValueError('"app_ver" is required!')

        #
        iss_path = Path(f'{self.app_name}.iss').resolve()
        logging.info(f'Generating "{iss_path}" file...')

        iss_config = {
            'app_name': self.app_name,
            'app_ico': str(self.icon),
            'app_guid': self.app_guid,
            'app_ver': self.app_ver,
            'dist': str(self.dist),
            'is_onefile': ('onefile' in self.pyinst_flags),
        }

        tmpl_path = Path(__file__).parent / 'templates/iss.tmpl'
        env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(tmpl_path.parent),
            keep_trailing_newline=True,
            block_start_string='{%%',
            block_end_string='%%}',
            variable_start_string='[{{',
            variable_end_string='}}]',
            comment_start_string='{##',
            comment_end_string='##}',
        )
        template = env.get_template(tmpl_path.name)
        with open(iss_path, 'w') as f:
            f.write(template.render(iss_config))

        logging.info(f'"{iss_path}" file successfully generated!')

        #
        logging.info(f'Building setup with Inno Setup...')
        subprocess.run(['iscc', str(iss_path)], shell=True)

        return self
