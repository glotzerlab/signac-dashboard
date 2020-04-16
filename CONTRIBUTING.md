# How to contribute to the project

## Feedback

Issue reports and feature proposals are very welcome.
Please use the [GitHub issue page](https://github.com/glotzerlab/signac-dashboard/issues/) for this.

## Contributing code

Code contributions to the signac-dashboard open-source project are welcomed via pull requests on GitHub.
Prior to any work you should contact the signac developers to ensure that the planned development meshes well with the directions and standards of the project.
All contributors must agree to the Contributor Agreement ([ContributorAgreement.md](ContributorAgreement.md)) before their pull request can be merged.

### General guidelines

  * Use the [OneFlow](https://www.endoflineblog.com/oneflow-a-git-branching-model-and-workflow) model of development:
    - Both new features and bug fixes should be developed in branches based on `master`.
    - Hotfixes (critical bugs that need to be released *fast*) should be developed in a branch based on the latest tagged release.
  * Write code that is compatible with all supported versions of Python (listed in [setup.py](https://github.com/glotzerlab/signac-dashboard/blob/master/setup.py)).
  * Avoid introducing dependencies -- especially those that might be harder to install in high-performance computing environments.
  * Create [unit tests](https://en.wikipedia.org/wiki/Unit_testing) and [integration tests](https://en.wikipedia.org/wiki/Integration_testing) that cover the common cases and the corner cases of the code.
  * Preserve backwards-compatibility whenever possible, and make clear if something must change.
  * Document any portions of the code that might be less clear to others, especially to new developers.
  * Write API documentation in this package, and put usage information, guides, and concept overviews in the [framework documentation](https://docs.signac.io/) ([source](https://github.com/glotzerlab/signac-docs/)).

Please see the [Support](https://docs.signac.io/projects/signac-dashboard/en/latest/support.html) section as part of the documentation for detailed development guidelines.

### Code Style

Code submitted to the signac-dashboard project must adhere to the [PEP8 style guide](https://www.python.org/dev/peps/pep-0008/).

We recommend to use [flake8](http://flake8.pycqa.org/en/latest/) and [autopep8](https://pypi.org/project/autopep8/) to find and fix any code style issues prior to committing and pushing.
