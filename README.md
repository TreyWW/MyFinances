# MyFinances

MyFinances is an open-source web application designed to empower individuals and teams to efficiently manage their finances. Whether you're tracking personal expenses, managing client invoices, or planning your financial goals, MyFinances provides a user-friendly platform to streamline these tasks.

## Key Features

- **Expense Tracking:** Easily record and categorize your expenses, upload photos of receipts, and visualize spending patterns.

- **Invoicing:** Generate professional invoices for clients, including options for hourly rates or fixed fees. Receive payments directly through the integrated payment gateways.

- **Financial Reports:** Gain insights into your financial health with customizable reports, income summaries, and expense analyses.

- **Budgeting:** Set financial goals and track your progress. Keep an eye on your spending habits and make informed decisions.

## Getting Started

### Prerequisites

- Python 3.x
- Django
- Docker
- Docker Compose
- Additional requirements can be found in the `requirements.txt` file.

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/MyFinances.git
   ```
2. Move to the directory
   ```bash
   cd MyFinances
   ```
3. Create an ENV file in `coming_soon` by using:
   ```bash
   cp .env.sample /env/MyFinances.env
   ```
4. Move to the infrastructure directory
   ```bash
   cd MyFinances/infrastructure/backend
   ```
5. Build the docker image
   ```bash
   docker-compose build
   ```
6. Start the docker-compose server
   ```bash
   docker-compose up -d
   ```
7. Visit the website; `http://127.0.0.1:10012`

## Contributing

Thank you for considering contributing to the MyFinances project! Your contributions help make the project better for everyone.

### Issue Tracker

#### Reporting Issues

Before submitting a new issue, please:

- Check for existing related issues.
- Check the issue tracker for a specific upstream project that may be more appropriate.
- Check against supported versions of this project (i.e., the latest).

Use the Subscribe button to stay updated on discussions. Keep conversations on-topic and respect the opinions of others. For urgent issues or those involving confidential details, please report them directly to the maintainers.

#### Security Vulnerabilities

We take security seriously. If you discover a security vulnerability within MyFinances, please reach out to us directly via [email](mailto:security-myfinances@strelix.org). We will promptly address and resolve the issue.

#### Bug Reports

If you encounter a bug, please report it by opening an issue on the issue tracker. Include details about the issue, steps to reproduce, and relevant environment details.

#### Feature Requests

We welcome feature requests! If you have an idea for a new feature or enhancement, open an issue on the issue tracker. Describe the feature, its potential benefits, and any relevant use cases.

### Pull Requests / Merge Requests

To contribute code:

1. Fork the repository.
2. Create a new branch for your changes.
3. Make your changes, following the coding style guidelines.
4. Test your changes thoroughly.
5. Submit a pull request to the main repository's `main` branch.

We'll review your pull request, provide feedback, and work with you to get your changes merged.

### Code Style and Quality

Adhere to the coding style guidelines of the Django project. Find the Django coding style guide [here](https://docs.djangoproject.com/en/4.2/internals/contributing/writing-code/coding-style/).

### Version Control

We use Git. Make sure your commits are clear, concise, and well-documented. Follow conventional commit message style.

### Development

#### Prerequisites

Make sure you have the necessary prerequisites for development. These are detailed above in this README.md file.

#### Getting Started

Refer to the "Getting Started" section in this README.md for setting up the development environment and running the application locally.

Thank you for your contributions!

---
__Note:__ This README.md is a living document and might be updated over time. Always refer to the latest version when contributing and developing.
