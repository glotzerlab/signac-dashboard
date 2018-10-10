# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## 0.1.5 - 2018-10-09
### Added
- Example dashboards are in the `examples` folder.
- Console entry point, `signac-dashboard run` will launch a simple dashboard. This will be extended in a future release.
- Better support for custom module assets.

### Changed
- Modules are now part of the user session and are saved to the project document. This requires all module arguments to be JSON-encodable.
- Restructured module design and how modules provide assets.
- Documentation has been updated, with instructions for port forwarding.
- Split views into a separate file.

### Fixed
- Browsers will no longer cache dynamic content.
- Pagination rendering bug squashed.

## 0.1.4 - 2018-07-23
### Fixed
- Removed `flask_cache` and replaced with `lru_cache` to fix compatibility with Flask 1.0.

## 0.1.3 - 2018-04-02
### Added
- README documentation on searching.
- Added support for signac cache.
- Added LRU cache for job details.
- Added pagination support for much faster loading.
- Added VideoViewer module.

### Changed
- Error handling is cleaner.
- Refactored job views.
- Job titles show statepoint booleans as True/False.
- Added job id prefix to downloaded filenames so they can be distinguished.

### Fixed
- Heterogeneous schemas can generate job titles.

## 0.1.2 - 2018-02-08
### Added
- Search jobs with a document filter with `doc:{"key":"value"}`.
- Unit tests for job search.
- README documentation is much more complete.
- flake8 checked in Bitbucket Pipelines.
- Added this CHANGELOG!

## 0.1.1 - 2017-09-25
### Added
- Bitbucket Pipelines support for continuous integration.
- Added first unit test.
- Mobile support is significantly improved.

### Fixed
- Flask package was incorrectly configured in the previous release.
- Corrected menu activation script to trigger on turbolinks:load event.

## 0.1.0 - 2017-09-17
### Added
- First release.
