import shutil

with open('app.py', 'r') as f:
    src = f.read()

patch = """
import sys as _sys
import os as _os

def resource_path(rel):
    if hasattr(_sys, '_MEIPASS'):
        return _os.path.join(_sys._MEIPASS, rel)
    return _os.path.join(_os.path.abspath('.'), rel)

"""

if 'resource_path' not in src:
    src = src.replace(
        'app = Flask(__name__)',
        patch + "app = Flask(__name__, template_folder=resource_path('templates'), static_folder=resource_path('static'))"
    )
    with open('app_build.py', 'w') as f:
        f.write(src)
    print('Patched successfully -> app_build.py')
else:
    shutil.copy('app.py', 'app_build.py')
    print('Already patched -> copied to app_build.py')
