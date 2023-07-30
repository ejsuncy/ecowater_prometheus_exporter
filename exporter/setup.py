import setuptools
import pathlib

here = pathlib.Path(__file__).parent.resolve()
version = (here / 'VERSION.txt').read_text(encoding='utf-8')

setuptools.setup(
    name="exporter",
    version=version.strip(),
    packages=setuptools.find_packages(),
    python_requires='>=3.11',
    install_requires=[
        'prometheus_client',
        # todo: set the correct python library name
        'template_python_library'
        'pyyaml'
    ]
)
