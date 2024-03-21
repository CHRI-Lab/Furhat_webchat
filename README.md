# QA-Furhat
# Docs
 [Project Overview](Documents/Project%20Overview.pdf) | [Product Requirements](Documents/Product%20requirements.pdf) | [Meetings](Documents/Meeting%20Notes) | [Technical Details](Documents/Technical%20Details.pdf) | [Plan](Documents/Plan%20for%20Sprint%202%20&%203.pdf) 
# Table of Contents

- [Project Overview](#project-overview)
  * [Background](#background)
  * [Phases](#phases)
  * [Team Roles](#team-roles)
  * [Client Goals](#client-goals)
  * [Motivation](#motivation)
  * [Goals](#goals)
  * [Scope](#scope)
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

# Project Overview

This project aims to create an innovative Q&A platform using a Furhat robot, driven by the need for a specialized and interactive information resource. The platform leverages web scraping and advanced language processing to build a robot that acts as a dynamic and intelligent receptionist.

## Background

The initiative is driven by the need for a specialized and interactive information resource that leverages vast data from websites like Melbourne Connect or CIS. The core idea is to harness web scraping and advanced language processing to create a robot that serves as both an information source and a dynamic receptionist.

## Phases

- **Data Collection and Preparation:** Web scraping to build a knowledge foundation.
- **Language Model Development:** Creating a domain-specific LLM for accurate responses.
- **Robot Integration:** Implementing the LLM in the Furhat robot for interactive conversations.
- **Receptionist Functionalities:** Enhancing the platform with various receptionist duties.

## Team Roles

- Product Manager: Zhuowen Zheng
- Scrum Master: Xi Luo
- Architecture Lead: Shaohui Wang
- Quality Assurance Lead: Chengjia Zhou
- Development Environment Lead: Jiyuan Chen
- Deployment Lead: Peng Tang

## Client Goals

Develop a domain-specific Q&A system integrating advanced language models with robotic technology to provide accurate and engaging user assistance.

## Motivation

To advance AI and robotics integration, creating a seamless and natural human-robot interaction system.

## Goals

- Successfully scrape and utilize website data.
- Develop a domain-specific LLM.
- Integrate the LLM with the Furhat robot, creating a sophisticated Q&A and receptionist platform.

## Scope

1. **Data Collection and Preparation**
2. **Domain-Specific Language Model Development**
3. **Integration with Furhat Robot**
4. **Implementation of Receptionist Functionalities**
5. **Testing and Quality Assurance**
6. **Deployment**

# WorkFlow

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

## Continuous Integration/Continuous Deployment (CI/CD) Process

This project uses GitHub Actions for CI/CD, which includes:

- **Automated testing**: Automatically run unit tests and integration tests with each commit to `develop` or `feature/*` branches.
- **Automated build**: Automatically build the project when merged into the `main` branch.
- **Automated deployment**: Automatically deploy to the production environment after a successful build.

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
