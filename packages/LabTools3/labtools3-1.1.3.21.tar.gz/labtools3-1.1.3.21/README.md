# LabTools3
Set of Python analysis tools for physics labs. It contains the "package" directory which is the Python package with a setup.py script for installation and
a "doc" directory containing the Sphinx documentation. The repository starts with version 0.2.9 of LabTools.
Version 1.0.2:  has mostly some big fixes.

Version 1.1.0:  now includes 2D-histograms and some bug fixes.

Version 1.1.1:  includes 3D lego plot for *histo2d*. Note that at the moment surface and lego plots are only in linear scale possible.

Version 1.1.2:  non-linear fitting is now based on *scipy.optimize.least_squares* so parameter bounds can be used.

Version 1.1.3.1:  (same as 1.1.3) updated the *rebin* function for 1D histograms, by default it now returns a new histogram (*replace = False*). Also added the options to have the mean calculated for combined bins instead of the sum (*use_mean = True*). Fixed a bug in *project_x* and *project_y* functions for 2D histograms.

Version 1.1.3.2: minor bug fixes

Version 1.1.3.3: histogram axis labels are preserved in rebinning and projection actions (for 2d histogram)

Version 1.1.3.4: minor bug fixes

Version 1.1.3.5: corrected problen with *add_data*

Version 1.1.3.6: added features to fitting: *plot* attribute to plot the fit, the fit results is plotted by default (controlled with the *plot_fit* kwarg). The fit object are callable, returning the value of the fit function using the current values of the fit parameters. New attribute to datafile: *adata\_comment\_index*, a list of indices pointing to comment lines.
 
Version 1.1.3.7: updated documentation

Version 1.1.3.8: datafile can be initialized with a list of strings correponding to the regular syntax

Version 1.1.3.9: Fixed a bug in *histo* where histogram window variable was not initialized when loading from file (required a *clear_window* call).

Version 1.1.3.10: 2d histo now accepts axes as keywords. Make sure for 3d display the axes is a Axes3DSubplot.

Version 1.1.3.11: new control on title and axes labels for plotting

Version 1.1.3.12: bug fixes, peak and background functions are available for histogram fits.

Version 1.1.3.13: fitting of only one parameters enabled for linear fits

Version 1.1.3.14: error calcualtion for filling histograms with weights include sum of weight**2 

Version 1.1.3.15: contination lines enabled in parameter file by endine line with "\" or ","" 

Version 1.1.3.16: Corrected bug in histo.rebin. gen_fit allows control of relative step size using the diff_step keyword. It is also possible to supply a list of functions to calculate the parameter derivatives. This helps with numerical accuracy in the minimization process (see gen_fit documentation) 

Version 1.1.3.17: Histogram window settings are now also saved to data file. Replace equal sign with colon in histogram title in get_spectrum. 

Version 1.1.3.18: Added plot_guess function to histo. This makes it easy to plot fit functions with guessed parameters. 

Version 1.1.3.19: Fixed but when using using the fill function in 1d histograms with weights multiple times.

Version 1.1.3.20: Added show_header to datafile and the full_precision key word to write_csv.

Version 1.1.3.21: Fixed bug in histo2d operations