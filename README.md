<!--# MyFinances -->

<img src="https://github.com/TreyWW/MyFinances/assets/73353716/685b83f4-1495-4ce6-94c7-e24c2f14a6d1" width="400">

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**MyFinances** is an open-source web-based application designed to simplify invoicing and financial management for individuals and teams. Whether you're a freelancer or a small business, MyFinances provides an intuitive platform to help you stay organized.

| PLEASE NOTE: This project is under active development. We welcome contributors! |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |

## Key Features

- **One-Time Invoices**: Create and send professional one-time invoices to your clients.
- **Recurring Invoices**: Automate your invoicing with recurring invoices that can be scheduled and sent periodically.
- **Invoice Reminders**: Ensure timely payments by sending reminder emails for outstanding invoices.
- **Emailing**: Email invoices and payment reminders directly from the platform.

### Table of Contents
- [Getting Started](#Getting-started)
- [Contribution](#Contribution)
- [Pull Requests / Merge Request](#Pull-Requests/Merge-Requests)
- [Code Style and Quality](#Code-Style-and-Quality)
- [Development](#Development)
- [Credits](#Credits)
- [Star History](#Star-History)

## Getting Started

### Prerequisites

- Python 3.10+
- Additional requirements can be found in the `pyproject.toml` file (or by using `poetry show`).

Please be aware some features **require** AWS features such as Eventbridge, however you can host the site locally or any other
usual hosting platform, we have a docker setup.

### Installation

For detailed setup instructions please refer to our documentation: [https://docs.strelix.org/MyFinances](https://docs.strelix.org/MyFinances)

## Contributing

We appreciate your interest in contributing to MyFinances! Whether you're a seasoned developer or just getting started, we have something for you.

### Issue Tracker

#### Reporting Issues

Before submitting a new issue, please:

- Search for existing issues that might cover your topic.
- Ensure your issue pertains to the current version of the project.

For urgent issues or those involving confidential details, please report them directly to us on the details below.

#### Security Vulnerabilities

We take security seriously. If you discover a security vulnerability within MyFinances, please reach out to us directly
via [email](mailto:security-myfinances@strelix.org). We will promptly address and resolve the issue.

#### Bug Reports

If you encounter a bug, please report it by opening an issue on the issue tracker. Include details about the issue, steps to
reproduce, and relevant environment details.

#### Feature Requests

We welcome feature requests! If you have an idea for a new feature or enhancement, open an issue on the issue tracker. Describe
the feature, its potential benefits, and any relevant use cases.

We have a step system for features:
- idea: suggested
- idea: deciding
- idea: accepted

Once an idea is accepted this can be worked on. Only if there is no assigned person to the issue, the issue is inactive or the
issue is marked as "group issue"/"needs help" you may work on it.


### Pull Requests / Merge Requests

To contribute code:

1. Fork the repository.
2. Install pre-commit hooks (do it once, whenever you clone the repository) [optional but tests may fail without it]
   - `pre-commit install`
3. Create a new branch for your changes.
4. Implement your changes, following the coding standards.
5. Run the test suite
    - `python3 manage.py test`
    - run the app (`python3 manage.py runserver`)
    - view any changed pages in browser (`http://127.0.0.1:8000`) and make sure the changes work as expected
6. Submit a pull request to the main repository's `main` branch.

We'll review your pull request, provide feedback, and work with you to get your changes merged.

### Code Style and Quality

Adhere to the coding style guidelines of the Django project. Find the Django coding style
guide [here](https://docs.djangoproject.com/en/4.2/internals/contributing/writing-code/coding-style/). Please install our pre-commit hooks using following command:

We now also use the [python black formatter](https://black.readthedocs.io/). Code tests will be run before PRs can be merged, they
will fail if you haven't ran the command below:

```
pip install black
black ./
```

For static type checking we are using [mypy](https://mypy-lang.org/). Code tests will be run before PRs can be merged, they will fail if types in you code will be incorrect. You can run check with this command:

```
mypy .
```

### Development

#### Prerequisites

Make sure you have the necessary prerequisites for development. These are detailed above in this README.md file.

#### Getting Started

View our documentation for further instruction [https://docs.strelix.org/MyFinances](https://docs.strelix.org/MyFinances)

Thank you for your contributions!

---

#### 🌟 A very special thank you to all of our contributors 🌟

##### View a full list <a href="https://github.com/TreyWW/MyFinances/graphs/contributors">here</a>

<!-- CONTRIBUTORS TABLE START -->
<table>
<tr><td>
                <td align="center">
                    <a href="https://github.com/TreyWW" title="TreyWW">
                        <img title="Project Lead" src="https://github.com/TreyWW.png" width="100px;" alt="" />
                        <br />
                        <sub>
                            <b>Trey</b>
                        </sub>
                    </a>
                    <br />
                    <a href="https://github.com/TreyWW/MyFinances/pulls?q=user%3ATreyWW" title="Project Lead">👑</a><a href="https://github.com/TreyWW/MyFinances/pulls?q=is%3Apr+author%3ATreyWW" title="Backend">🖥</a>
                </td>
                </td><td>
                <td align="center">
                    <a href="https://github.com/Domejko" title="Domejko">
                        <img title="Development & CI & Bug Fixing" src="https://github.com/Domejko.png" width="100px;" alt="" />
                        <br />
                        <sub>
                            <b>Slawek Bierwiaczonek</b>
                        </sub>
                    </a>
                    <br />
                    <a href="https://github.com/TreyWW/MyFinances/pulls?q=is%3Apr+author%3ADomejko" title="Backend">🖥</a><a href="https://github.com/TreyWW/MyFinances/pulls?q=is%3Apr+author%3ADomejko" title="Bug Fixes">🐞</a><a href="https://github.com/TreyWW/MyFinances/pulls?q=is%3Apr+author%3ADomejko" title="Added Tests">🧪</a>
                </td>
                </td><td>
                <td align="center">
                    <a href="https://github.com/introkun" title="introkun">
                        <img title="Development & CI" src="https://github.com/introkun.png" width="100px;" alt="" />
                        <br />
                        <sub>
                            <b>Sergey G</b>
                        </sub>
                    </a>
                    <br />
                    <a href="https://github.com/TreyWW/MyFinances/pulls?q=is%3Apr+author%3Aintrokun" title="Backend">🖥</a><a href="https://github.com/TreyWW/MyFinances/pulls?q=is%3Apr+author%3Aintrokun" title="Frontend">🎨</a><a href="https://github.com/TreyWW/MyFinances/pulls?q=is%3Apr+author%3Aintrokun" title="Added Tests">🧪</a><a href="https://github.com/TreyWW/MyFinances/pulls?q=is%3Apr+author%3Aintrokun" title="Refactored Files">♻</a>
                </td>
                </td><td>
                <td align="center">
                    <a href="https://github.com/Z3nKrypt" title="Z3nKrypt">
                        <img title="Documentation" src="https://github.com/Z3nKrypt.png" width="100px;" alt="" />
                        <br />
                        <sub>
                            <b>Jacob</b>
                        </sub>
                    </a>
                    <br />
                    <a href="https://github.com/TreyWW/MyFinances/pulls?q=is%3Apr+author%3AZ3nKrypt" title="Documentation">📖</a>
                </td>
                </td><td>
                <td align="center">
                    <a href="https://github.com/tomkinane" title="tomkinane">
                        <img title="Design" src="https://github.com/tomkinane.png" width="100px;" alt="" />
                        <br />
                        <sub>
                            <b>Tom</b>
                        </sub>
                    </a>
                    <br />
                    <a href="https://github.com/TreyWW/MyFinances/pulls?q=is%3Apr+author%3Atomkinane" title="Frontend">🎨</a>
                </td>
                </td></tr><tr><td>
                <td align="center">
                    <a href="https://github.com/SharonAliyas5573" title="SharonAliyas5573">
                        <img title="Development" src="https://github.com/SharonAliyas5573.png" width="100px;" alt="" />
                        <br />
                        <sub>
                            <b>SharonAliyas5573</b>
                        </sub>
                    </a>
                    <br />
                    <a href="https://github.com/TreyWW/MyFinances/pulls?q=is%3Apr+author%3ASharonAliyas5573" title="Backend">🖥</a>
                </td>
                </td><td>
                <td align="center">
                    <a href="https://github.com/romana-la" title="romana-la">
                        <img title="Documentation" src="https://github.com/romana-la.png" width="100px;" alt="" />
                        <br />
                        <sub>
                            <b>romana-la</b>
                        </sub>
                    </a>
                    <br />
                    <a href="https://github.com/TreyWW/MyFinances/pulls?q=is%3Apr+author%3Aromana-la" title="Documentation">📖</a>
                </td>
                </td><td>
                <td align="center">
                    <a href="https://github.com/flyingdev" title="flyingdev">
                        <img title="CI" src="https://github.com/flyingdev.png" width="100px;" alt="" />
                        <br />
                        <sub>
                            <b>flyingdev</b>
                        </sub>
                    </a>
                    <br />
                    <a href="https://github.com/TreyWW/MyFinances/pulls?q=is%3Apr+author%3Aflyingdev" title="Added Tests">🧪</a>
                </td>
                </td><td>
                <td align="center">
                    <a href="https://github.com/chavi362" title="chavi362">
                        <img title="Documentation" src="https://github.com/chavi362.png" width="100px;" alt="" />
                        <br />
                        <sub>
                            <b>chavi362</b>
                        </sub>
                    </a>
                    <br />
                    <a href="https://github.com/TreyWW/MyFinances/pulls?q=is%3Apr+author%3Achavi362" title="Documentation">📖</a>
                </td>
                </td><td>
                <td align="center">
                    <a href="https://github.com/bermr" title="bermr">
                        <img title="CI" src="https://github.com/bermr.png" width="100px;" alt="" />
                        <br />
                        <sub>
                            <b>bermr</b>
                        </sub>
                    </a>
                    <br />
                    <a href="https://github.com/TreyWW/MyFinances/pulls?q=is%3Apr+author%3Abermr" title="Added Tests">🧪</a>
                </td>
                </td></tr><tr><td>
                <td align="center">
                    <a href="https://github.com/PhilipZara" title="PhilipZara">
                        <img title="Design" src="https://github.com/PhilipZara.png" width="100px;" alt="" />
                        <br />
                        <sub>
                            <b>PhilipZara</b>
                        </sub>
                    </a>
                    <br />
                    <a href="https://github.com/TreyWW/MyFinances/pulls?q=is%3Apr+author%3APhilipZara" title="Frontend">🎨</a>
                </td>
                </td><td>
                <td align="center">
                    <a href="https://github.com/Tianrui-Luo" title="Tianrui-Luo">
                        <img title="Development" src="https://github.com/Tianrui-Luo.png" width="100px;" alt="" />
                        <br />
                        <sub>
                            <b>Tianrui-Luo</b>
                        </sub>
                    </a>
                    <br />
                    <a href="https://github.com/TreyWW/MyFinances/pulls?q=is%3Apr+author%3ATianrui-Luo" title="Backend">🖥</a>
                </td>
                </td><td>
                <td align="center">
                    <a href="https://github.com/HarryHuCodes" title="HarryHuCodes">
                        <img title="Development" src="https://github.com/HarryHuCodes.png" width="100px;" alt="" />
                        <br />
                        <sub>
                            <b>HarryHuCodes</b>
                        </sub>
                    </a>
                    <br />
                    <a href="https://github.com/TreyWW/MyFinances/pulls?q=is%3Apr+author%3AHarryHuCodes" title="Backend">🖥</a>
                </td>
                </td><td>
                <td align="center">
                    <a href="https://github.com/Nuovaxu" title="Nuovaxu">
                        <img title="Development" src="https://github.com/Nuovaxu.png" width="100px;" alt="" />
                        <br />
                        <sub>
                            <b>Nuova</b>
                        </sub>
                    </a>
                    <br />
                    <a href="https://github.com/TreyWW/MyFinances/pulls?q=is%3Apr+author%3ANuovaxu" title="Backend">🖥</a>
                </td>
                </td><td>
                <td align="center">
                    <a href="https://github.com/HessTaha" title="HessTaha">
                        <img title="CI-CD" src="https://github.com/HessTaha.png" width="100px;" alt="" />
                        <br />
                        <sub>
                            <b>HessTaha</b>
                        </sub>
                    </a>
                    <br />
                    <a href="https://github.com/TreyWW/MyFinances/pulls?q=is%3Apr+author%3AHessTaha" title="Docker">🐳</a>
                </td>
                </td></tr><tr><td>
                <td align="center">
                    <a href="https://github.com/wnm210" title="wnm210">
                        <img title="Design" src="https://github.com/wnm210.png" width="100px;" alt="" />
                        <br />
                        <sub>
                            <b>wnm210</b>
                        </sub>
                    </a>
                    <br />
                    <a href="https://github.com/TreyWW/MyFinances/pulls?q=is%3Apr+author%3Awnm210" title="Frontend">🎨</a>
                </td>
                </td><td>
                <td align="center">
                    <a href="https://github.com/matthewjuarez1" title="matthewjuarez1">
                        <img title="Full Stack" src="https://github.com/matthewjuarez1.png" width="100px;" alt="" />
                        <br />
                        <sub>
                            <b>Matt</b>
                        </sub>
                    </a>
                    <br />
                    <a href="https://github.com/TreyWW/MyFinances/pulls?q=is%3Apr+author%3Amatthewjuarez1" title="Backend">🖥</a><a href="https://github.com/TreyWW/MyFinances/pulls?q=is%3Apr+author%3Amatthewjuarez1" title="Frontend">🎨</a>
                </td>
                </td><td>
                <td align="center">
                    <a href="https://github.com/SBMOYO" title="SBMOYO">
                        <img title="CI" src="https://github.com/SBMOYO.png" width="100px;" alt="" />
                        <br />
                        <sub>
                            <b>SBMOYO</b>
                        </sub>
                    </a>
                    <br />
                    <a href="https://github.com/TreyWW/MyFinances/pulls?q=is%3Apr+author%3ASBMOYO" title="Added Tests">🧪</a>
                </td>
                </td><td>
                <td align="center">
                    <a href="https://github.com/kliu6151" title="kliu6151">
                        <img title="Development" src="https://github.com/kliu6151.png" width="100px;" alt="" />
                        <br />
                        <sub>
                            <b>Kevin Liu</b>
                        </sub>
                    </a>
                    <br />
                    <a href="https://github.com/TreyWW/MyFinances/pulls?q=is%3Apr+author%3Akliu6151" title="Backend">🖥</a>
                </td>
                </td><td>
                <td align="center">
                    <a href="https://github.com/HappyLife2" title="HappyLife2">
                        <img title="Design" src="https://github.com/HappyLife2.png" width="100px;" alt="" />
                        <br />
                        <sub>
                            <b>Jehad Altoutou</b>
                        </sub>
                    </a>
                    <br />
                    <a href="https://github.com/TreyWW/MyFinances/pulls?q=is%3Apr+author%3AHappyLife2" title="Frontend">🎨</a>
                </td>
                </td></tr><tr><td>
                <td align="center">
                    <a href="https://github.com/spalominor" title="spalominor">
                        <img title="Design" src="https://github.com/spalominor.png" width="100px;" alt="" />
                        <br />
                        <sub>
                            <b>Samuel P</b>
                        </sub>
                    </a>
                    <br />
                    <a href="https://github.com/TreyWW/MyFinances/pulls?q=is%3Apr+author%3Aspalominor" title="Frontend">🎨</a>
                </td>
                </td><td>
                <td align="center">
                    <a href="https://github.com/CKsabari2001" title="CKsabari2001">
                        <img title="Layout" src="https://github.com/CKsabari2001.png" width="100px;" alt="" />
                        <br />
                        <sub>
                            <b>Sabari Ragavendra CK</b>
                        </sub>
                    </a>
                    <br />
                    <a href="https://github.com/TreyWW/MyFinances/pulls?q=is%3Apr+author%3ACKsabari2001" title="Frontend">🎨</a>
                </td>
                </td><td>
                <td align="center">
                    <a href="https://github.com/atulanand25" title="atulanand25">
                        <img title="Full Stack" src="https://github.com/atulanand25.png" width="100px;" alt="" />
                        <br />
                        <sub>
                            <b>atulanand25</b>
                        </sub>
                    </a>
                    <br />
                    <a href="https://github.com/TreyWW/MyFinances/pulls?q=is%3Apr+author%3Aatulanand25" title="Backend">🖥</a><a href="https://github.com/TreyWW/MyFinances/pulls?q=is%3Apr+author%3Aatulanand25" title="Frontend">🎨</a><a href="https://github.com/TreyWW/MyFinances/pulls?q=is%3Apr+author%3Aatulanand25" title="Bug Fixes">🐞</a>
                </td>
                </td><td>
                <td align="center">
                    <a href="https://github.com/ryansurf" title="ryansurf">
                        <img title="Bug Fixes" src="https://github.com/ryansurf.png" width="100px;" alt="" />
                        <br />
                        <sub>
                            <b>ryansurf</b>
                        </sub>
                    </a>
                    <br />
                    <a href="https://github.com/TreyWW/MyFinances/pulls?q=is%3Apr+author%3Aryansurf" title="Bug Fixes">🐞</a>
                </td>
                </td><td>
                <td align="center">
                    <a href="https://github.com/blocage" title="blocage">
                        <img title="Refactoring" src="https://github.com/blocage.png" width="100px;" alt="" />
                        <br />
                        <sub>
                            <b>David</b>
                        </sub>
                    </a>
                    <br />
                    <a href="https://github.com/TreyWW/MyFinances/pulls?q=is%3Apr+author%3Ablocage" title="Refactored Files">♻</a>
                </td>
                </td></tr><tr><td>
                <td align="center">
                    <a href="https://github.com/glizondo" title="glizondo">
                        <img title="Bug Fixes" src="https://github.com/glizondo.png" width="100px;" alt="" />
                        <br />
                        <sub>
                            <b>Guillermo</b>
                        </sub>
                    </a>
                    <br />
                    <a href="https://github.com/TreyWW/MyFinances/pulls?q=is%3Apr+author%3Aglizondo" title="Bug Fixes">🐞</a>
                </td>
                </td><td>
                <td align="center">
                    <a href="https://github.com/marvinl803" title="marvinl803">
                        <img title="Full Stack" src="https://github.com/marvinl803.png" width="100px;" alt="" />
                        <br />
                        <sub>
                            <b>Marvin Lopez</b>
                        </sub>
                    </a>
                    <br />
                    <a href="https://github.com/TreyWW/MyFinances/pulls?q=is%3Apr+author%3Amarvinl803" title="Backend">🖥</a><a href="https://github.com/TreyWW/MyFinances/pulls?q=is%3Apr+author%3Amarvinl803" title="Frontend">🎨</a>
                </td>
                </td><td>
                <td align="center">
                    <a href="https://github.com/artkolpakov" title="artkolpakov">
                        <img title="Bug Fixes" src="https://github.com/artkolpakov.png" width="100px;" alt="" />
                        <br />
                        <sub>
                            <b>Artem Kolpakov</b>
                        </sub>
                    </a>
                    <br />
                    <a href="https://github.com/TreyWW/MyFinances/pulls?q=is%3Apr+author%3Aartkolpakov" title="Bug Fixes">🐞</a>
                </td>
                </td><td>
                <td align="center">
                    <a href="https://github.com/Yadu-M" title="Yadu-M">
                        <img title="Development" src="https://github.com/Yadu-M.png" width="100px;" alt="" />
                        <br />
                        <sub>
                            <b>Yadu</b>
                        </sub>
                    </a>
                    <br />
                    <a href="https://github.com/TreyWW/MyFinances/pulls?q=is%3Apr+author%3AYadu-M" title="Backend">🖥</a>
                </td>
                </td><td>
                <td align="center">
                    <a href="https://github.com/vatsaaaal" title="vatsaaaal">
                        <img title="Development" src="https://github.com/vatsaaaal.png" width="100px;" alt="" />
                        <br />
                        <sub>
                            <b>Vatsal</b>
                        </sub>
                    </a>
                    <br />
                    <a href="https://github.com/TreyWW/MyFinances/pulls?q=is%3Apr+author%3Avatsaaaal" title="Backend">🖥</a>
                </td>
                </td></tr><tr><td>
                <td align="center">
                    <a href="https://github.com/hussein-mamane" title="hussein-mamane">
                        <img title="Development" src="https://github.com/hussein-mamane.png" width="100px;" alt="" />
                        <br />
                        <sub>
                            <b>Hussein</b>
                        </sub>
                    </a>
                    <br />
                    <a href="https://github.com/TreyWW/MyFinances/pulls?q=is%3Apr+author%3Ahussein-mamane" title="Backend">🖥</a>
                </td>
                </td><td>
                <td align="center">
                    <a href="https://github.com/pvvramakrishnarao234" title="pvvramakrishnarao234">
                        <img title="Development" src="https://github.com/pvvramakrishnarao234.png" width="100px;" alt="" />
                        <br />
                        <sub>
                            <b>pvvramakrishnarao234</b>
                        </sub>
                    </a>
                    <br />
                    <a href="https://github.com/TreyWW/MyFinances/pulls?q=is%3Apr+author%3Apvvramakrishnarao234" title="Backend">🖥</a>
                </td>
                </td></tr></table>
<!-- CONTRIBUTORS TABLE END -->

If any information is incorrect above, or you would like anything removed, feel free to open an issue, email our team, or
manually edit with the details below.

### How to edit the contributors table?

- Updated any info using `python3 manage.py contriubtors`
- Run `python3 manage.py contributors sync`
- Make a PR to request these changes in
- Done :)

---
__Note:__ This README.md is a living document and might be updated over time. Always refer to the latest version when contributing
and developing.

## Star History

<a href="https://star-history.com/#TreyWW/MyFinances&Timeline">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=TreyWW/MyFinances&type=Timeline&theme=dark" />
    <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=TreyWW/MyFinances&type=Timeline" />
    <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=TreyWW/MyFinances&type=Timeline" />
  </picture>
</a>
