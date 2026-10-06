import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'handover_realsense'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/handover_realsense']),
        ('share/handover_realsense', ['package.xml']),
        (os.path.join('share', 'handover_realsense', 'launch'), glob('launch/*.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='ubuntu',
    maintainer_email='ryan.donen@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'raw_monitor = handover_realsense.raw_monitor:main'
        ],
    },
)
