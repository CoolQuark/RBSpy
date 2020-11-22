
![logo](https://github.com/CoolQuark/RBSpy/blob/main/logo/logo.jpg)

RBSpy is a python library developed with the propose of loading, manipulating and plotting Rutherford Backscattering Spectrometry data. Its main classes are:
1. the *rbsSpectra*, suitable to work with single align-random measurements;
2. the *multi_rbs*, suitable to work with multiple sets of align-random measurements.

Both classes include methods to perform routine tasks such as do the energy-channel calibration and charge renormalisation. Besides these more experimental oriented methods, RBSpy also include methods specifically introduced for RBS simulation data. The experimental side of the library is demonstrate in the jupyter notebook [Example.ipynb]( https://github.com/CoolQuark/RBSpy/blob/main/Example.ipynb) while the simulation part will be explained elsewhere.
