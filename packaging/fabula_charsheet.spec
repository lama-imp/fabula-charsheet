# PyInstaller spec for the click-to-run build.
# Build from the repository root with:
#   uv run --with pyinstaller pyinstaller packaging/fabula_charsheet.spec --noconfirm
import sys
from pathlib import Path

from PyInstaller.utils.hooks import collect_data_files, collect_submodules, copy_metadata

ROOT = Path(SPECPATH).parent
APP = ROOT / "fabula_charsheet"
NAME = "FabulaCharsheet"

# The app's own modules are imported by main.py, which Streamlit runs as a
# script, so PyInstaller can't see them on its own.
sys.path.insert(0, str(APP))
hiddenimports = (
    ["config"]
    + collect_submodules("data")
    + collect_submodules("pages")
    + collect_submodules("streamlit")
)

datas = [
    (str(APP / "main.py"), "."),
    (str(APP / "assets"), "assets"),
]
datas += collect_data_files("streamlit")
datas += copy_metadata("streamlit")

a = Analysis(
    [str(ROOT / "packaging" / "launcher.py")],
    pathex=[str(APP)],
    datas=datas,
    hiddenimports=hiddenimports,
    excludes=["pytest", "_pytest", "tkinter"],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name=NAME,
    # Windows/Linux: the console window shows the app is running and closing
    # it stops the app. On macOS the .app runs without a terminal.
    console=sys.platform != "darwin",
    upx=False,
)

coll = COLLECT(exe, a.binaries, a.datas, name=NAME, upx=False)

if sys.platform == "darwin":
    app = BUNDLE(
        coll,
        name=f"{NAME}.app",
        bundle_identifier="io.github.lama-imp.fabula-charsheet",
        info_plist={"CFBundleDisplayName": "Fabula Charsheet"},
    )
