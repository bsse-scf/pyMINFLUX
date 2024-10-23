# Change Log

All notable changes to this project will be documented in this file. Detailed information can be found in the [git log](https://github.com/bsse-scf/pyMINFLUX/commits/master/).

## [0.5.0] - 2024-10-24

### New features

* Add high-performance 3D viewer for localization plotting.
* Allow loading confocal images from MSR files to display along with the MINFLUX localizations.
* Add `pyminflux.reader.MSRReader` class to API to load both data and metadata from MSR files.
* Expand list of options (`nothing`, `tid`, `fluorophore`, `depth`, `time`) for color-coding.
* All parameters can not be color-coded. 
* Add colorbar to the 2D and 3D plots when color-coding by depth and time.
* Allow color unmixing on filtered dataset.
* Always calculate the total trace duration, not only for tracking datasets.
* Add "Export all plots" option to the context menu of the results histograms in the Analyzer.
* Add parameter "tim_tot" to the list of options in the Histogram Plotter.
* Allow exporting 3D plots and colorbars as high-resolution PNG images.

### Bug fixes

* Run global filters after updating the min trace length in the MinFluxProcessor.
* Fix the x-axis limits in the Color Unmixer for the DCR histogram to (0.0, 1.0).

## [0.4.1] - 2024-05-10

### New features

* Add Importer option to pool DCR values for all relocalized iterations weighted by their photon count.
* More efficient calculation of tracking-related statistics.
* Allow exporting all Analyzer plots in one action ([issue/13](https://github.com/bsse-scf/pyMINFLUX/issues/13)).
* When exporting plots, default to input dataset folder in the Save dialog ([issue/12](https://github.com/bsse-scf/pyMINFLUX/issues/12)).
* Allow measuring distances in the main Plotter along all spatial directions.
* Implement automatic update check (currently fixed at 1-week interval).
* Switch to new build mode ([Nuitka](https://nuitka.net/)) for faster application startup and execution.

### Bug fixes

* Fix `pyminflux_reader.py` plug-in incompatibility with ParaView 5.12 ([issue/14](https://github.com/bsse-scf/pyMINFLUX/issues/14)).
* Fix issue with fluorophore colors being reassigned at random after unmixing.
* Only calculate and export tracking statistics for tracking datasets.
* Do not allow plotting average localization of tracking datasets.
* Fix issue with application packaging that caused some `*.npy` files to fail reading ([issue/11](https://github.com/bsse-scf/pyMINFLUX/issues/11)).

## [0.4.0] - 2024-03-27

### New features 

#### Data compatibility
* Add support for custom MINFLUX sequences.
* Add initial support for single-molecule tracking datasets.
* Update the pyMINFLUX Reader ParaView plugin to read .pmx version 2.0 files.
* Add macOS M1 build of the pyMINFLUX application.

#### Analysis and filtering tools
* Merge Trace Length Viewer tool into the Analyzer.
* Implement filtering by trace length into the Analyzer.
* Add per-trace tracking stats to the Trace Stats Viewer (tracking datasets only).
* Add Histogram Plotter tool.
* Implement `Set range` context-menu action in the Time Inspector.

#### UI
* Switch to green-magenta color scheme for fluorophore IDs.
* Add a scale bar to the main data viewer (for XYZ localisations).
* Display line connecting subsequent localizations within a trace (tracking datasets only).

#### Performance improvements
* Dramatically improve the rendering of color-coded localizations.
* Speed up dataframe-based operations by upgrading to Pandas 2.2.x with PyArrow backend.

### Fixes

* Fix default axis ranges not being applied to the Analyzer plots when loading new data.
* Fix (incorrectly) forcing the aspect ratio of the Data Plotter for XYZ localizations.

## [0.3.0] - 2023-09-01

### New features

* Add native pyMINFLUX file format `.pmx`.
* FRC Analysis now runs in parallel over all CPU cores.
* Add new Trace Statistics Viewer.
* Add new Trace Length Viewer.
* Add fluorophore ID reassignment within traces by majority vote.
* Allow opening files by drag-and-drop onto the Pipeline Toolbar (left panel).
* Add all analysis tools to the main window's Analysis menu.
* Add companion [ParaView reader plug-in](https://github.com/bsse-scf/pyMINFLUX/tree/master/paraview_plugins).
* Remove 3D Plotter (in favor of using ParaView and the ParaView reader plug-in).

## [0.2.0] - 2023-07-19

### New features

* Calculate additional per-trace statistics and allow exporting all stats to csv file.
* Add Fourier Ring Correlation tool to follow resolution progression.
* Allow complete access to the API for command-line/notebook processing: https://pyminflux.ethz.ch/api/pyminflux.
  * [Example notebook](examples/processing.ipynb)
* Add menu action to check for application updates.

### Fixes

* Fix issue with the fluorophore drop-down menu not being refreshed after global reset button is pressed.

## [0.1.3] - 2023-05-26

### New features

* Implement z-scaling factor to compensate for refractive index mismatch (issue #1).
* Add context menu actions to export any plot as a `.png` image and at a user-defined DPI (issue #3).
* Add global reset button to the main-window wizard and remove the one from the Analyzer.
* Add quick help for all entries in the Options dialog.
* Add links to code repository, issues page, and mailing list to the Help menu.
* Add a few minor UI tweaks.

### Fixes

* Fix issue with applying a filter in the Time Inspector not updating the Analyzer plots.
* Fix issue with measurement lines being allowed when the plotted data was not spatial (x, y), and the reported distance would be in nm.
* Fix inconsistency in the way fluorophore IDs and colors were assigned by the various methods used.

## [0.1.2] - 2023-05-12

Bug fix release.

### Fixes

* Fix issue with exporting to `.npy` only working when the `Active Color` selector was on `All`.

## [0.1.1] - 2023-05-04

First official release.
