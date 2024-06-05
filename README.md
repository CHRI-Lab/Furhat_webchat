# QA-Furhat
## Docs
 [Project Overview](Documents/Project%20Overview.pdf) | [Product Requirements](Documents/Product%20requirements.pdf) | [Technical Details](Documents/Technical%20Details.pdf) | [Plan](Documents/Sprint Planning/Sprint 4 Plan Document.pdf) 

## File Guide
[src](src/README.md) | [tests](tests/README.md) | [data_sample](data_sample/project_test_case.json)

# Table of Contents

- [Project Overview](#project-overview)
  * [Background](#background)
  * [Phases](#phases)
  * [Team Roles](#team-roles)
  * [Client Goals](#client-goals)
  * [Motivation](#motivation)
  * [Goals](#goals)
  * [Scope](#scope)

[Click here to watch Project Video](https://youtu.be/93wi30PJB9A)

[Click here to watch Demo Video of Sprint 2](https://www.youtube.com/watch?v=TUybeMc36Tc)

[Click here to watch newest Demo Video of Sprint 3](https://www.youtube.com/watch?v=3pd7kKd3OR4)

# Project Overview

This project aims to create an innovative Q&A platform using a Furhat robot, driven by the need for a specialized and interactive information resource. The platform leverages web scraping and advanced language processing to build a robot that acts as a dynamic and intelligent receptionist.
### Deployment Issue
This is a project creating skills for furhat robot sdk, so we cannot deploy it on url. As client required, we will post all our code on CHRI-Lab github.

## Background

The initiative is driven by the need for a specialized and interactive information resource that leverages vast data from websites like Melbourne Connect or CIS. The core idea is to harness web scraping and advanced language processing to create a robot that serves as both an information source and a dynamic receptionist.

## Project Structure
- QA-Koala/
  - data_sample/ -- test data
  - Documents/ -- All the documents include handover page for development.
  - src/ -- Source Code, follow the instruction in [README.md](src/README.md) in src.
  - tests/ -- RAG reliable test
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

## Task Tracking

To enhance the readability and convenience of task tracking, we use Trello for task assignment and synchronize its content with Jira to improve the readability of sprint reviews. You can find our Jira issues through the Confluence document. You can access our [Trello Board](https://trello.com/b/nKf5DVec/furhat-project) through the following link.

## Client Goals

Develop a domain-specific Q&A system integrating advanced language models with robotic technology to provide accurate and engaging user assistance.

## Motivation

To advance AI and robotics integration, creating a seamless and natural human-robot interaction system.

## Functionality
![Alt text](./src/images/Structure%20of%20proj.png)

- Scrape and utilize website data include text and image.
- Retrieve question-related text and image.
- Answer the question based on the retrieved context and image.
- Our code are integrated with furhat robot, you could access its functionality through furhat SDK.

## Scope

1. **Data Collection and Preparation**
2. **Domain-Specific Language Model Development**
3. **Integration with Furhat Robot**
4. **Implementation of Receptionist Functionalities**
5. **Testing and Quality Assurance**
6. **Deployment**
