# Changelog

The versioning scheme is compliant with the [PEP 440] specification.

[PEP 440]: https://peps.python.org/pep-0440/#public-version-identifiers

## 2.3.2 (2025-07-26)

**FINAL DEPRECATION RELEASE**

- Package now automatically installs `hijridate==2.3.0`
- Added prominent deprecation warnings on import
- All functionality redirected to `hijridate` package  
- Simplified README and metadata to focus on migration
- This is the last release - use `hijridate` for future updates

## 2.3.1 (2023-04-24)

- Updated the package classifiers.

## 2.3.0 (2023-04-24)

- Deprecated the package in favor of the new `hijridate` package.
- Dropped support for Python 3.6 and added support for Python 3.11.
- Updated documentation and removed badges from the package description.
- Changed GitHub username back to @dralshehri and updated related links.

## 2.2.4 (2022-05-23)

- Added more classifiers to package configuration.
- Fixed location of type-checking marker file. (By [@dimbleby] in [#10])
- Updated development and build requirements.

[#10]: https://github.com/dralshehri/hijri-converter/pull/10
[@dimbleby]: https://github.com/dimbleby

## 2.2.3 (2022-02-12)

- Changed package docstrings to Google style and updated documentation.
- Updated development workflows and configurations.
- Other minor fixes and enhancements.
- Changed GitHub username to @mhalshehri and updated related links.

## 2.2.2 (2021-09-25)

- Added some missing variable annotations to `ummalqura` module.
- Fixed an issue when generating documentation.
- Fixed some typos in docstrings and improved documentation.
- Other minor fixes and enhancements.

## 2.2.1 (2021-09-04)

- Fixed calculation of month 12 of the year 1354 AH.
- Fixed an issue when generating documentation without the package being
  installed. ([#7])
- Refactored internal helper functions.
- Updated and improved tests and documentation.
- Fixed some typos.

[#7]: https://github.com/dralshehri/hijri-converter/issues/7

## 2.2.0 (2021-08-16)

- Added `today()` classmethod to Hijri class to get the Hijri Object of today's
  date.
- Added `separator` and `padding` parameters to `dmyformat()` method to have
  more control over formatting.
- Refactored locales for better management and testing. (Inspired by [Arrow]
  localization)
- Updated main classes to be conveniently imported into the package level e.g.
  `from hijri_converter import Hijri, Gregorian`.
- Removed deprecated method `slashformat()` from Hijri and Gregorian classes.
- Updated tests and documentation.
- Other minor fixes and internal enhancements.

[arrow]: https://github.com/arrow-py/arrow

## 2.1.3 (2021-06-22)

- Minor fixes and enhancements for docstrings and documentation.

## 2.1.2 (2021-05-30)

- Added Bangla translation. (By [@nokibsarkar] in [#4])
- Changed `Hijri` rich comparison to return `NotImplemented` when the second
  operand is not `Hijri` class.
- Changed `ummalqura` constants to be in capital letters adhering to PEP8.
- Updated packaging configuration files and local development workflow.
- Other minor fixes and documentation enhancements.

[#4]: https://github.com/dralshehri/hijri-converter/pull/4
[@nokibsarkar]: https://github.com/nokibsarkar

## 2.1.1 (2020-05-21)

- Added `dmyformat()` to return dates in `DD/MM/YYYY` format.
- Deprecated `slashformat()` method to be replaced by `dmyformat()` method.
- Fixed PyPI package not including some required files. ([#3])
- Fixed some typos.
- Updated tests.

[#3]: https://github.com/dralshehri/hijri-converter/issues/3

## 2.1.0 (2019-06-16)

This version has more accurate conversion and better internal code. Details are
as follows:

- Dropped support for the years before 1343 AH because the Umm al-Qura calendar
  was not established then.
- Added `validate` parameter to Hijri class for optional disabling of Hijri date
  validation and improving performance. However, disabling validation will
  decrease the conversion accuracy silently.
- Verified conversion against original references and updated the `month_starts`
  tuple for more accurate conversion.
- Improved `Hijri` class rich comparison methods.
- Improved date validation methods for better performance and readability.
- Made the `Hijri` class hashable by adding a custom `__hash__` method.
- Refactored many internal methods (not affecting the API).
- Other minor fixes, enhancements and performance boost.

## 2.0.0 (2019-06-05)

In short, this version supports only lunar Hijri calendar on Python 3.6+, and
the conversion is in complete agreement with the official Umm al-Qura calendar.
Details are as follows:

- Renamed the package to `hijri-converter`.
- Dropped support for the solar Hijri calendar.
- Dropped support for Python 3.5.
- Refactored localization and `ummalqura.py` module.
- Updated `month_starts` tuple in alignment with the Umm al-Qura calendar.
- Added `fromdate()` classmethod to `Gregorian` class.
- Added `notation()` method to `Hijri` and `Gregorian` classes.
- Added more methods to `Gregorian` class including `slashformat()`,
  `month_name()`, `day_name()` and `to_julian()`.
- Renamed `month_days()` method of `Hijri` class to `month_length()`.
- Changed formatted string to use f-strings.
- Improved documentation and examples.
- Updated unit tests.
- Fixed other minor issues and typos.

## 1.5.0 (2018-12-27)

- Added `fromisoformat()` classmethod to `Hijri` class.
- Added support for rich comparison between Hijri dates.
- Updated documentation and testing code.
- Other minor fixes and enhancements.

## 1.4.0 (2018-11-26)

- Refactored conversion methods to improve performance.
- Changed date validation back to be the default and removed optional parameter.
- Added `to_julian()` method to `Hijri` class.
- Updated documentation and testing code.
- Other minor fixes and enhancements.

## 1.3.3 (2018-11-21)

- Fixed a bug in range validation for the Gregorian date.
- Changed generic typing to built-in types.
- Added more tests to cover the solar calendar.
- Improved code structure and documentation.

## 1.3.2 (2018-11-16)

- Improved documentation and changelog.

## 1.3.1 (2018-11-16)

- Fixed README file.

## 1.3.0 (2018-11-16)

- Added documentation directory with an online version.
- Changed date input validation to be optional and disabled by default.
- Improved code readability and performance.
- Other minor fixes and enhancements.

## 1.2.0 (2018-11-09)

- Added `slashformat()` method to `Hijri` class.
- Improved date validation code.
- Fixed some typos in documentation and docstrings.

## 1.0.1 (2018-10-28)

- Improved examples and documentation.

## 1.0.0 (2018-10-28)

- First release.
