import pathlib
from setuptools import setup, find_packages

CWD = pathlib.Path(__file__).absolute().parent

def get_version():
    path = CWD / "robust_gymnasium" / "__init__.py"
    content = path.read_text()
    for line in content.splitlines():
        if line.startswith("__version__"):
            return line.strip().split()[-1].strip().strip('"').strip("'")
    raise RuntimeError("bad version data in __init__.py")

def get_description():
    with open("README.md", encoding="utf-8") as fh:
        return fh.read()

setup(
    name="robust_gymnasium",
    version=get_version(),
    author="Safe RL Lab",
    author_email="contact@saferl.org",
    description="A standard API for robust reinforcement learning and a diverse set of reference environments (formerly Gym).",
    long_description=get_description(),
    long_description_content_type="text/markdown",
    license="MIT",
    packages=find_packages(include=["robust_gymnasium", "robust_gymnasium.*"]),
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.21.0",
        "cloudpickle>=1.2.0",
        "typing-extensions>=4.3.0",
        "farama-notifications>=0.0.1",
        "importlib-metadata>=4.8.0; python_version<'3.10'"
    ],
    include_package_data=True,
    url="https://github.com/SafeRL-Lab/Robust-Gymnasium",
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence"
    ],
    # If you want to expose extras:
    extras_require={
        "all": [
            "numba>=0.49.1",
            "scipy>=1.2.3",
            "mujoco>=2.3.0",
            "Pillow",
            "opencv-python",
            "pynput",
            "termcolor",
            "ufal.pybox2d>=2.3.10.3",
            "gymnasium[mujoco]",
            "gymnasium[box2d]",
            "gymnasium>=0.29.1",
            "dm_control>=1.0.20",
            "jax>=0.4.30",
            "pettingzoo>=1.24.3",
            "pybullet-svl>=3.1.6.4",
            "h5py",
            "open3d",
            "openai",
            "hidapi",
            "ale_py>=0.9",
            "box2d-py==2.3.5",
            "pygame>=2.1.3",
            "swig==4.*",
            "mujoco-py>=2.1,<2.2",
            "cython<3",
            "mujoco>=2.1.5",
            "imageio>=2.14.1",
            "jaxlib>=0.4.0",
            "flax>=0.5.0",
            "torch>=1.0.0",
            "matplotlib>=3.0",
            "moviepy>=1.0.0"
        ],
        "testing": [
            "pytest==7.1.3",
            "scipy>=1.7.3",
            "dill>=0.3.7"
        ]
    }
)
