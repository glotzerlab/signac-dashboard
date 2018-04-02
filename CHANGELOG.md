# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## 0.1.3 - 2018-04-02
### Added
- README documentation on searching
- Added support for signac cache
- Added LRU cache for job details
- Added pagination support for much faster loading
- Added VideoViewer module

### Changed
- Error handling is cleaner
- Refactored job views
- Job titles show statepoint booleans as True/False
- Added job id prefix to downloaded filenames so they can be distinguished

### Fixed
- Heterogeneous schemas can generate job titles

## 0.1.2 - 2018-02-08
### Added
- Search jobs with a document filter with `doc:{"key":"value"}`
- Unit tests for job search
- README documentation is much more complete
- flake8 checked in Bitbucket Pipelines
- Added this CHANGELOG!

## 0.1.1 - 2017-09-25
### Added
- Bitbucket Pipelines support for continuous integration
- Added first unit test
- Mobile support is significantly improved

### Fixed
- Flask package was incorrectly configured in the previous release
- Corrected menu activation script to trigger on turbolinks:load event

## 0.1.0 - 2017-09-17
### Added
- First release
