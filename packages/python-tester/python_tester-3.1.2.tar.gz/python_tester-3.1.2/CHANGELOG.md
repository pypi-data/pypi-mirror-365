# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Available types:

- `Added` for new features.
- `Changed` for changes in existing functionality.
- `Deprecated` for soon-to-be removed features.
- `Removed` for now removed features.
- `Fixed` for any bug fixes.
- `Security` in case of vulnerabilities.

## [Unreleased]

## [3.1.1]

### Fixed

- Crashed when --teacher was not added because then sentry info was missing.

## [3.1.0]

### Added

- Function for changing working dir to assignment dir. It raise custom error if dir is missing.

## [3.0.2]

### Changed

- Rewrote for python 2025
- standard is failfast. Need to use --failslow to run all tests
- using uv to manage
- added uv comman "tester" that runs tests
- Now you need to send path to specific testfile or dir that contain them, like "uv run tester <path>".

## [2.6.0]

### Added

- Support for adding an identifying user for Sentry.

## [2.5.0]

### Added

- Integration with Sentry.

## [2.4.0]

### Added

- Assert method assertNotAttribute. Check that object does not have an attribute, ex a module.

### Fixed

- Changed how the TestSuite is created because how we did it is deprecated in python3.11.
- Printing test summary to be compatible with 3.11.

## [2.3.1]

### Fixed

- Had misspelled arguments as aruments

## [2.3.0]

### Added

- CLI option "-f|--failfast", it stops execution of tests on first error or failure.
- CLI option "-s| --showtags", shows the tags for all tests, does not run the tests.
- Support for individual "what is excpected as correct" for assert calls. Docstring version is used as default which can be overriden in assert calls.

### Changed

- Traceback when error occures in test is now printed with the docstring from the test.

## [2.2.0]

### Added

- Finds test files in multiple directories instead of only one

## [2.1.3]

### Fixed

- Corrected spelling in print

## [2.1.2]

### Changed

- Changed from swedish to english in exam result text

## [2.1.1]

### Fixed

- Now ExamTestResultExam is part of imports at examiner level

## [2.1.0]

### Added

- New classes for examinations with points and limit for passing.

### Fixed

- Correct base classes for custom exceptions

## [2.0.0]

### Changed

- No longer using std buffer for output of tests.
- No longer prints 1 and 0 for passing or failing test suites.

### Added

- Exits program with exit code for passing or failing tests.

## [1.6.0]

### Added

- Can add website links to assignment in TestCase classes

## [1.5.2]

### Fixed

- Change in pythons unittest made it so tip for StopIteration wasn't showing on python38-9.

## [1.5.1]

### Fixed

- Bug caused tags-wrapped functions to have incorrect metadata.

## [1.5.0]

### Added

- Added som common functions/classes can be imported directly from examiner.

### Fixed

- --tags will not properly skip tests if they don't match.

## [1.4.0] - 2021-05-20

### Changed

- Script no longer output results if no tests are found.
- --extra only runs extra assignments

## [1.3.0] - 2021-05-20

### Added

- New assert method assertOrder

## [1.2.0] - 2021-05-20

### Added

- Support for assertCountEqual

## [1.1.0] - 2021-05-18

### Changed

- Increased max len for test name and result in output.
- --trace flag now shows entire traceback

### Added

- Support for assertRaises

## [1.0.4] - 2021-05-04

### Added

- Two new assert methods, assertModule and assertAttribute.

## [1.0.3] - 2021-04-30

### Added

- --trace option to traceback assertion errors

## [1.0.2] - 2021-04-21

### Changed

- Changed allowed naming for test classes and test functions

### Added

- assertNotIn method

## [1.0.1] - 2021-04-16

### Added

- CHANGELOG to track changes.
- CircleCI build to push releases to dbwebb-se/python repo
