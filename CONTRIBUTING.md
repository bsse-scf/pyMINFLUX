# Contributing to pyMINFLUX
Thank you for your interest in contributing to pyMINFLUX! We value the contributions of our community members and are pleased you're here. This document provides guidelines and instructions for contributing to this project.

## Code of Conduct
pyMINFLUX is dedicated to providing a welcoming and harassment-free experience for everyone. We expect all contributors to uphold our [Code of Conduct](CODE_OF_CONDUCT.md). By participating in this project, you agree to abide by its terms.

## Getting Started
Before you begin, make sure you have a GitHub account and are familiar with GitHub pull requests and issues. Knowledge of Git for version control is also necessary.

### Installing Pre-requisites
To ensure code quality and consistency, we require all contributors to use `pre-commit` for automatic code formatting and checks. Please set up the complete development environment on your local machine by following these steps:

1. Clone the repository to your local machine and install all necessary dependencies:
```sh
$ conda create -n pyminflux-env python=3.11  # or 3.10
$ conda activate pyminflux-env
$ git clone https://github.com/bsse-scf/pyMINFLUX /path/to/pyminflux
$ cd /path/to/pyminflux
$ python -m pip install -e .
$ pip install -r dev-requirements.txt
```
2. Navigate to the repository directory and run `pre-commit install` to set up the git hook scripts.
3. Now `pre-commit` will run automatically on `git commit` for files you've staged.

## Making Contributions
When you're ready to contribute, follow these steps:
1. **Fork the repository**: Create your own fork of the repository to make your changes.
2. **Create a new branch**: Make a new branch for your changes. Name it appropriately.
3. **Make your changes**: Add your changes to your branch. Use meaningful commit messages that clearly describe the changes made.
4. **Use pre-commit**: Ensure all `pre-commit` checks pass. If any checks fail, make the necessary adjustments to your code.
5. **Write and run tests**: Add new tests for the functionality you're adding and ensure they pass along with existing tests. New code should not break existing tests.
6. **Submit a pull request (PR)**: Push your changes to your fork and then submit a pull request to the main repository. Provide a clear description of the problem and solution, including any relevant issue numbers.

## Pull Request Guidelines
- **Do not submit PRs for minor typos or cosmetic changes** that do not add significant value to the project.
- **Discuss big changes** in an issue before working on them to ensure they align with the project's direction and avoid duplication of effort.
- **Keep PRs focused** on a single issue or feature. Split large changes into multiple PRs if necessary.

## Review Process
After you submit a PR, the project maintainers will review your changes. We may suggest changes or ask for further details. This is a collaborative process, so please be patient and receptive to feedback. Once your PR is approved, a maintainer will merge it.

## Collaborations
If you are interested in a (scientific) collaboration with us that goes beyond the scope of standard open source contributions, feel free to get in touch with us at pyminflux *at* ethz *dot* ch!

## Questions?
If you have any questions or need further clarification on the contribution process, please open an issue, and we'll be happy to help.
Thank you for contributing to pyMINFLUX! Your efforts help make this project better for everyone.
