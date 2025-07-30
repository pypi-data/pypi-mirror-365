from setuptools import setup, find_packages

setup(
    name="realtimeCanvas",
    version="0.1.0",
    description="A Python package for real-time image display and manipulation with Tkinter and PIL.",
    author="Charles Chaotic (Volburaal)",
    author_email="muzammilnoor897@gmail.com",
    url="https://github.com/Volburaal/realtimeCanvas",
    packages=find_packages(),
    install_requires=[
        "Pillow>=8.0.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)