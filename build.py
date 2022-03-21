import os
import subprocess as sb
import sys
from pathlib import Path
import logging
import shutil

try:
    # считаем, что python3.7 стоит и virtualenv тоже
    from virtualenv import cli_run
except BaseException:
    exit(-1)

logger = logging.getLogger("build")
package_name = "ApcResTranslator"
wd = os.path.dirname(os.path.abspath(__file__))

if __name__ == "__main__":
    try:
        # print(wd)
        # intpaths = [str(p) for p in Path("C:/").rglob("python.exe") if str(p).find("\\Python37")]
        # if not intpaths:
        #     raise FileNotFoundError("Не можем найти python3.7")
        venv_dir = str(
            Path("C:/ApcResTranslatorEnv"))  # Наш env перенесем в папку вне бранча (дабы не удалялось при каждой сборке)
        exe_dir = Path(wd).joinpath('./exe/ApcResTranslator').resolve()
        if not exe_dir.exists():
            os.makedirs(str(exe_dir))

        logger.info(venv_dir)
        # session = cli_run(["-p",str(intpaths[0]),venv_dir])

        # создаем окружение с помощью virtualenv
        session = cli_run([venv_dir])
        logger.info(str(session.creator))
        logger.info(str(session.interpreter))
        logger.info(str(session.verbosity))
        logger.info(str(session.seeder))
        pip = os.path.join(venv_dir, "Scripts", "pip.exe")
        pyinstaller = os.path.join(venv_dir, "Scripts", "pyinstaller.exe")
        if not os.path.exists(pip):
            raise FileNotFoundError(pip)

        # устанавливаем туда нужные пакеты
        sb.run([pip, "install", "-r", "requirements.txt"], check=True)
        # sb.run([pip, "uninstall", "pyinstaller"])
        sb.run([pip, "install", "pyinstaller"])  # "https://github.com/pyinstaller/pyinstaller/archive/develop.zip"])

        # когда-то нужен был специальный хук для того,
        # чтобы google-cloud-translate паковалась pyinstallerом
        # (сейчас не надо, но на всякий, оставлю)
        # os.chmod(os.path.join(venv_dir, "Lib", "site-packages", "_pyinstaller_hooks_contrib", "hooks", "stdhooks", "hook-google.cloud.py"), S_IWRITE)
        # shutil.copy(
        #   os.path.join(wd, "hooks", "hook-google.cloud.py"),
        #   os.path.join(venv_dir, "Lib", "site-packages", "_pyinstaller_hooks_contrib", "hooks", "stdhooks")
        # )

        # нужные пути в начало поиска модулей
        sys.path.insert(1, os.path.join(venv_dir, "Lib", "site-packages"))
        sys.path.insert(1, os.path.join(wd, "GUI"))

        sb.run(
            [
                pyinstaller,
                '--name=%s' % package_name,
                '-F',  # '-D' one-folder mode; '-F'  -  one-file
                "-y",  # no confirm
                '--windowed',  # without console
                '--clean',  # каждый раз чистая сборка (удаляются все кеши и тд)
                f"--add-binary={os.path.join(wd, 'GUI', 'Resources', '*.png')};{os.path.join('Resources')}",
                f"--add-binary={os.path.join(wd, 'GUI', 'Resources', '*.ico')};{os.path.join('Resources')}",
                # f"--add-data={os.path.join(wd,'abbreviations.json')};{os.path.join('.')}",  # сокращения не пакуем, отдельно таскаем
                # f"--paths={os.path.join(venv_dir, 'Lib', 'site-packages')}",
                # f'--runtime-hook={os.path.join(venv_dir, "Lib", "site-packages","PyInstaller","hooks","hook-google.cloud.translate.py")}',
                f'--additional-hooks-dir={os.path.join(wd, "hooks")}',
                f"--add-data={os.path.join(wd, 'GUI', 'Resources', '*.html')};{os.path.join('Resources')}",
                f"--icon={os.path.join(wd, 'GUI', 'Resources', 'icon.ico')}",
                f"--distpath={str(exe_dir)}",
                # "--log-level=INFO",
                os.path.join(wd, 'GUI', 'MainWindow.py'),
            ],
            check=True
        )
        if exe_dir.exists():
            if exe_dir.joinpath("abbreviations.json").exists():
                os.remove(str(exe_dir.joinpath("abbreviations.json")))
            shutil.copy(Path(wd).joinpath("abbreviations.json"), exe_dir)
    except Exception as e:
        logger.exception(e)
