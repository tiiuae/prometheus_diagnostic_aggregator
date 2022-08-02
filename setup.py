from setuptools import setup

package_name = 'prometheus_diagnostic_aggregator'

setup(
    name=package_name,
    version='0.1.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    author='Mehmet Killioglu',
    author_email='mehmet.killioglu@unikie.com',
    maintainer='Mehmet Killioglu',
    maintainer_email='mehmet.killioglu@unikie.com',
    keywords=['ROS'],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Topic :: Software Development',
    ],
    description='Prometheus diagnostics aggregator.',
    license='Apache License, Version 2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'prometheus_diagnostic_aggregator ='
            ' prometheus_diagnostic_aggregator.prometheus_diagnostic_aggregator:main',
        ],
    },
)
