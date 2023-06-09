# Change Log

All notable changes to this project will be documented in this file.

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
