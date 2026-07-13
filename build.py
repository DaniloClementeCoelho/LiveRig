from pathlib import Path
import shutil
import subprocess
import sys
import os

from version import APP_VERSION

ROOT = Path(__file__).resolve().parent

BUILD_DIR = ROOT / "build"
DIST_DIR = ROOT / "dist"
RELEASE_DIR = ROOT / "release"

INNO_SETUP = Path(r"D:\Programas Instalados\Inno Setup 7\ISCC.exe")


def remove_if_exists(path: Path):
    if path.exists():
        print(f"Removendo {path.name}...")
        shutil.rmtree(path)


def run(command, env=None):
    result = subprocess.run(command, cwd=ROOT, env=env)
    if result.returncode != 0:
        raise SystemExit(result.returncode)


def main():

    print("=" * 60)
    print(f"LiveRig Build {APP_VERSION}")
    print("=" * 60)

    remove_if_exists(BUILD_DIR)
    remove_if_exists(DIST_DIR)
    remove_if_exists(RELEASE_DIR)

    RELEASE_DIR.mkdir(exist_ok=True)

    print("\nGerando executável...\n")

    run([
        sys.executable,
        "-m",
        "PyInstaller",
        "--clean",
        "LiveRig.spec",
    ])

    source = DIST_DIR / "LiveRig"
    target = RELEASE_DIR / "LiveRig"

    shutil.copytree(source, target)

    print("\nGerando instalador...\n")

    env = os.environ.copy()
    env["LIVERIG_VERSION"] = APP_VERSION

    run(
        [
            str(INNO_SETUP),
            "installer.iss",
        ],
        env=env,
    )

    print()
    print("=" * 60)
    print("BUILD FINALIZADO")
    print("=" * 60)
    print()
    print(f"Executável : {target}")
    print(f"Instalador : {RELEASE_DIR / f'LiveRigSetup-{APP_VERSION}.exe'}")


if __name__ == "__main__":
    main()