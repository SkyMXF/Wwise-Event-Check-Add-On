import os
import shutil

import PyInstaller.__main__

if __name__ == '__main__':

    output_dir = os.path.join(".", "packaged")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    exe_name = "check_event_inclusion"

    PyInstaller.__main__.run([
        # "--add-data=%s" % os.path.join(
        #    os.path.split(sys.executable)[0], "Lib", "site-packages", "qt_material"
        # ),
        "-F", "check_event_inclusion.py",
        "-n", exe_name,
        "--specpath", os.path.join(output_dir, "spec"),
        "--distpath", os.path.join(output_dir, "dist"),
        "--workpath", os.path.join(output_dir, "build"),
        # "--noupx",
        # *hidden_import_params
    ])

    # copy exe to root
    exe_src_path = os.path.join(output_dir, "dist", "%s.exe" % exe_name)
    exe_aim_path = "%s.exe" % exe_name
    if os.path.exists(exe_aim_path):
        os.remove(exe_aim_path)
    shutil.copy(exe_src_path, exe_aim_path)
