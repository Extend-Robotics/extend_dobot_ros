from distutils.core import setup
from catkin_pkg.python_setup import generate_distutils_setup

d = generate_distutils_setup(
    packages=['extend_gripper_control_dobot'],
    package_dir={'': 'src'}
)

setup(**d)
