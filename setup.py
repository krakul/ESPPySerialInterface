from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='ESPPySerialInterface',
    version='v1.0.0',
    description='SerialInterface script to communicate with ESP32 devices over UART',
    long_description=long_description,
    url='https://github.com/krakul/ESPPySerialInterface',
    packages=['ESPPySerialInterface'],
    install_requires=['dataclasses', 'dataclasses-json',
                      'parse', 'pyserial',
                      'PySerialInterface @ git+https://github.com/krakul/PySerialInterface.git@main'],
    license='MIT',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
