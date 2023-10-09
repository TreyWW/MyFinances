<!--# MyFinances -->

<img src="https://github.com/TreyWW/MyFinances/assets/73353716/685b83f4-1495-4ce6-94c7-e24c2f14a6d1" width="495" height="166">

MyFinances is an open-source web application designed to empower individuals and teams to efficiently manage their finances. Whether you're tracking personal expenses, managing client invoices, or planning your financial goals, MyFinances provides a user-friendly platform to streamline these tasks.

| PLEASE NOTE: This project is still in development, and has only just started! So none of the key features or descriptions have been fully implemented. We are beginner friendly and looking for contributors! |
|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

## Key Features

- **Expense Tracking:** Easily record and categorize your expenses, upload photos of receipts, and visualize spending patterns.

- **Invoicing:** Generate professional invoices for clients, including options for hourly rates or fixed fees. Receive payments directly through the integrated payment gateways.

- **Financial Reports:** Gain insights into your financial health with customizable reports, income summaries, and expense analyses.

- **Receipt Management** Store your old receipts, to keep as future tax deductions, or just a financial log. You can preview, download, or delete these receipts at any point! We also use parsing to auto-extract data from the receipt such as the total price.

- **Budgeting:** Set financial goals and track your progress. Keep an eye on your spending habits and make informed decisions.

## Getting Started

### Prerequisites

- Python 3.x
- Django
- Docker
- Docker Compose
- Additional requirements can be found in the `requirements.txt` file.

### Installation
Go to [SETUP.md](https://github.com/TreyWW/MyFinances/blob/main/documentation/SETUP.md)

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
4. Test your changes thoroughly
    - `python manage.py test backend`
    - run the app (`python manage.py runserver`)
    - view any changed pages in browser (`127.0.0.1`) and make sure the changes work as expected
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

#### 🌟 A very special thank you to all of our contributors 🌟

<table>
  <tr>
     <td align="center">
       <a href="https://github.com/TreyWW">
          <img src="https://github.com/TreyWW.png" width="100px;" alt=""/>
          <br />
          <sub>
             <b>
                Trey
             </b>
          </sub>
       </a>
       <br />
       <a href="https://github.com/TreyWW/MyFinances/pulls?q=user%3ATreyWW" title="Project Lead">👑</a>
       <a href="https://github.com/TreyWW/MyFinances/pulls?q=is%3Apr+author%3ATreyWW" title="Backend">🖥</a>
    </td>
      <td align="center">
           <a href="https://github.com/Z3nKrypt">
               <img src="https://github.com/Z3nKrypt.png" width="100px;" alt=""/>
               <br/>
               <sub>
                   <b>
                       Jacob
                   </b>
               </sub>
           </a>
           <br/>
           <a href="https://github.com/TreyWW/MyFinances/pulls?q=is%3Apr+author%3AZ3nKrypt" title="Documentation">📖</a>
       </td>
    <td align="center">
       <a href="https://github.com/tomkinane">
          <img src="https://github.com/tomkinane.png" width="100px;" alt=""/>
          <br />
          <sub>
             <b>
                Tom
             </b>
          </sub>
       </a>
       <br />
       <a href="https://github.com/TreyWW/MyFinances/pulls?q=is%3Apr+author%3Atomkinane" title="Frontend">🎨</a>
    </td>
       <td align="center">
           <a href="https://github.com/romana-la">
               <img src="https://github.com/romana-la.png" width="100px;" alt=""/>
               <br/>
               <sub>
                   <b>
                       romana-la
                   </b>
               </sub>
           </a>
           <br/>
           <a href="https://github.com/TreyWW/MyFinances/pulls?q=is%3Apr+author%3Aromana-la" title="Documentation">📖</a>
       </td>
       <td align="center">
           <a href="https://github.com/chavi362">
               <img src="https://github.com/chavi362.png" width="100px;" alt=""/>
               <br/>
               <sub>
                   <b>
                       chavi362
                   </b>
               </sub>
           </a>
           <br/>
           <a href="https://github.com/TreyWW/MyFinances/pulls?q=is%3Apr+author%3Achavi362" title="Documentation">📖</a>
       </td>
  </tr>
</table>

---
__Note:__ This README.md is a living document and might be updated over time. Always refer to the latest version when contributing and developing.
