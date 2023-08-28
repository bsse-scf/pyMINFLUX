# Change Log

All notable changes to this project will be documented in this file.

## [0.3.0] - TBD

* Add native pyMINFLUX file format `.pmx`.
* FRC Analysis now runs in parallel over all CPU cores.
* Add new Trace Statistics Viewer.
* Add new Trace Length Viewer.
* Add all analysis tools to the main window's Analysis menu.
* Add companion ParaView reader plug-in.
* Remove 3D Plotter (in favor of using ParaView).

## [0.2.0] - 2023-07-19

### New features

* Calculate additional per-trace statistics and allow exporting all stats to csv file.
* Add Fourier Ring Correlation tool to follow resolution progression.
* Allow complete access to the API for command-line/notebook processing: https://pyminflux.ethz.ch/api/pyminflux.
  * [Example notebook](examples/processing.ipynb)
* Add menu action to check for application updates.

### Fixed

* Fix issue with the fluorophore drop-down menu not being refreshed after global reset button is pressed.

## [0.1.3] - 2023-05-26

### New features

* Implement z-scaling factor to compensate for refractive index mismatch (issue #1).
* Add context menu actions to export any plot as a `.png` image and at a user-defined DPI (issue #3).
* Add global reset button to the main-window wizard and remove the one from the Analyzer.
* Add quick help for all entries in the Options dialog.
* Add links to code repository, issues page, and mailing list to the Help menu.
* Add a few minor UI tweaks.

### Fixed

* Fix issue with applying a filter in the Time Inspector not updating the Analyzer plots.
* Fix issue with measurement lines being allowed when the plotted data was not spatial (x, y), and the reported distance would be in nm.
* Fix inconsistency in the way fluorophore IDs and colors were assigned by the various methods used.

## [0.1.2] - 2023-05-12

Bug fix release.

### Fixed

* Fix issue with exporting to `.npy` only working when the `Active Color` selector was on `All`.

## [0.1.1] - 2023-05-04

First official release.
