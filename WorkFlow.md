# WorkFlow
- [WorkFlow](#workflow)
  * [Branching Strategy](#branching-strategy)
  * [Naming Conventions](#naming-conventions)
    + [Files and Directories](#files-and-directories)
    + [Code Variables and Functions](#code-variables-and-functions)
    + [Class Names](#class-names)
    + [Constants](#constants)
    + [Module-level "Private" Names](#module-level-private-names)
  * [Code Review Process](#code-review-process)
  * [Version Control and Release Process](#version-control-and-release-process)
  * [Continuous Integration/Continuous Deployment (CI/CD) Process](#continuous-integrationcontinuous-deployment-cicd-process)
  * [Issue Tracking and Handling](#issue-tracking-and-handling)
  * [Documentation Updates](#documentation-updates)
  * [Security and Compliance](#security-and-compliance)

## Branching Strategy

This project adopts the **Git Flow** branching model. The main branches include:

- `main`: Stores the released versions.
- `develop`: Integrates the latest development features.
- `feature/*`: New feature development branch, branching from `develop`, and merged back into `develop` upon completion.
- `release/*`: Version ready for release, used for bug fixes and documentation generation, eventually merged into both `main` and `develop`.
- `hotfix/*`: Emergency fixes for bugs in the production environment, branching from `main`, and merged back into both `main` and `develop` after the fix.

Branch naming rule: feature/release/hotfix/branch name.

## Naming Conventions

### Files and Directories
- **Use lowercase letters**: The naming of files and directories should be as short and meaningful as possible.
- **Connect multiple words with underscores (_)**: If a file name or directory name consists of multiple words, use underscores to connect the words, such as `my_script.py` or `data_processing/`.

### Code Variables and Functions
- **Variables**: Use lowercase letters, and if the variable name consists of multiple words, connect the words with underscores (_), such as `user_id` or `login_status`. This naming method is sometimes referred to as snake_case.
- **Functions**: Function names should also follow the variable naming rules, i.e., using lowercase letters and underscores, such as `calculate_age()` or `print_hello_world()`.

### Class Names
- **Use Upper Camel Case (UpperCamelCase)**: Each word in the class name starts with a capital letter, and no underscores are used, such as `StudentInfo` or `DataProcessor`.

### Constants
- **Use all uppercase letters**: Constant names should use all uppercase letters, and if the constant name consists of multiple words, connect them with underscores, such as `MAX_OVERFLOW` or `DEFAULT_COLOR`.

### Module-level "Private" Names
- **Start with a single underscore**: In Python, a convention is to use a single underscore prefix to indicate module-level private names, such as `_internal_update()` or `_secret_token`. This indicates that these variables or functions are primarily for internal use within the module and should not be directly accessed from outside the module.

## Code Review Process

1. After completing feature development, the developer submits a Pull Request (PR) from the `feature/*` branch to the `develop` branch.
2. Assign at least one team member (Architecture Lead) to review the code.
3. The reviewer evaluates the code based on code quality, design patterns, and project standards.
4. If necessary, the developer makes modifications based on the review comments.
5. Once the review is passed, merge the PR into the `develop` branch.

## Version Control and Release Process

- **Version naming rule**: Follow semantic versioning, formatted as `MAJOR.MINOR.PATCH`.
- **Releasing a new version**: When the `develop` branch accumulates enough feature updates, create a `release/*` branch from `develop` for release preparation.
- **Tagging**: When releasing a new version on the `main` branch, use Git tags to record the version number.
- **Release steps**: After completing the final tests, merge the `release/*` branch into both `main` and `develop`, then tag on the `main` branch.

## Issue Tracking and Handling

- **Reporting issues**: Use GitHub Issues to report problems.
- **Assigning issues**: The project maintainer is responsible for assigning issues to the appropriate developer.
- **Resolving issues**: After resolving the issue, the developer updates the issue status and closes it.

## Documentation Updates

- **README file**: Update the version number and introduction of new features in the README file with each new release.
- **API documentation**: Use Swagger or other tools to automatically generate API documentation and update it with each API change.

## Security and Compliance

- **Sensitive data handling**: All sensitive data (such as user passwords) must be encrypted for storage.
- **User privacy protection**: Comply with laws and regulations such as GDPR to protect user privacy.
- **Code audit**: Regularly conduct code audits to ensure there are no security vulnerabilities.
