# BiGLasso-Methods

This package Python provides wrappers for [TeraLasso](https://github.com/kgreenewald/teralasso/tree/master) and [DNNLasso](https://github.com/YangjingZhang/DNNLasso).  As they were originally written in Matlab, you will need Matlab on your machine to run them.  It also wraps [GmGM](https://github.com/BaileyAndrew/GmGM-python/tree/main) and Scikit-Learn's `graphical_lasso` function, to provide a consistent API for them.

These are included as "git submodules", i.e. we are just wrapping whatever happens to be in their repository.

EiGLasso is not included as it requires compilation of C++ code, which is more complicated to wrap in a PIP-installable module.  However it is not too hard to do it manually, and it is a good algorithm; if you wish to use it, check out their [github](https://github.com/SeyoungKimLab/EiGLasso).

This project has a copyleft license, as DNNLasso has a copyleft license.  Thus, if you wish to use this as part of a larger project, be aware that you will likely need a copyleft license for such a work (this is not legal advice, read the license to understand what you are entitled to do with this software).

## Installation

```
pip install biglasso-methods
```

### Installation Troubleshooting

If you do not have the latest Matlab version, the install may fail, with an error like:

```
RuntimeError: MATLAB R2024a installation not found. Install to default location, or add <matlabroot>/bin/maca64 to DYLD_LIBRARY_PATH, where <matlabroot> is the root of a MATLAB R2024a installation.
```

You can either solve this by installing the newest Matlab version, or finding out which version you have and [looking through PyPI](https://pypi.org/project/matlabengine/#history) to find which `matlabengine` version corresponds to your Matlab version.  For example, I had MATLAB R2023b, which works with `matlabengine 9.15`, so I ran:

```
pip install matlabengine==9.15.2
pip install biglasso-methods
```