<div align="center">

![MyFinances Banner](https://github.com/TreyWW/MyFinances/assets/73353716/685b83f4-1495-4ce6-94c7-e24c2f14a6d1)

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![Contributors](https://img.shields.io/github/contributors/TreyWW/MyFinances)](https://github.com/TreyWW/MyFinances/graphs/contributors)
[![Stars](https://img.shields.io/github/stars/TreyWW/MyFinances)](https://github.com/TreyWW/MyFinances/stargazers)

### 💰 Streamline your financial management with ease

**MyFinances** is an open-source invoicing and financial management platform designed for freelancers, small businesses, and teams. Create professional invoices, automate reminders, and stay organized.

[📚 **Documentation**](https://docs.strelix.org/MyFinances) • [🚀 **Get Started**](#-getting-started) • [🤝 **Contributing**](#-contributing) • [⭐ **Star us**](https://github.com/TreyWW/MyFinances)

</div>

---

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| 📄 **Professional Invoices** | Create and send stunning one-time invoices |
| 🔄 **Recurring Invoices** | Automate periodic billing with scheduled invoices |
| ⏰ **Smart Reminders** | Never miss a payment with automated email reminders |
| 📧 **Email Integration** | Send invoices and reminders directly from the platform |
| 👥 **Team Collaboration** | Manage finances collaboratively with team features |
| 🎨 **Modern UI** | Clean, intuitive interface built with Django + Tailwind CSS |

## 🚀 Getting Started

### Prerequisites
- **Python 3.10+**
- Additional dependencies listed in `pyproject.toml`
- Optional: Docker for containerized deployment
- Optional: AWS services (EventBridge) for advanced features

### Quick Installation

```bash
# Clone the repository
git clone https://github.com/TreyWW/MyFinances.git
cd MyFinances

# Install dependencies
pip install -r requirements.txt
# OR using Poetry
poetry install

# Run migrations and start the server
python manage.py migrate
python manage.py runserver
```

📖 **Need detailed setup instructions?** Check our [comprehensive documentation](https://docs.strelix.org/MyFinances)

## 🤝 Contributing

We love contributions! Whether you're fixing bugs, adding features, or improving documentation, your help is welcome.

### Quick Contributing Guide

1. **Fork** this repository
2. **Create** a new branch for your changes
3. **Make** your changes following our coding standards
4. **Test** your changes (`python manage.py test`)
5. **Submit** a pull request

### Development Setup

```bash
# Install pre-commit hooks (optional but recommended)
pre-commit install

# Format code with Black
black ./

# Type checking with mypy
mypy .

# Run tests
python manage.py test
```

**🏷️ Looking for your first contribution?** Check out issues labeled [`good first issue`](https://github.com/TreyWW/MyFinances/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22) and [`help wanted`](https://github.com/TreyWW/MyFinances/issues?q=is%3Aissue+is%3Aopen+label%3A%22help+wanted%22).

## 📋 Project Status

> **⚠️ Active Development**: This project is under active development. Features may change and new functionality is being added regularly.

### Feature Pipeline Status
- ✅ **idea: accepted** - Ready for implementation
- 🔄 **idea: deciding** - Under review
- 💡 **idea: suggested** - Proposed by community

## 🛡️ Security

Found a security vulnerability? Please **don't** open a public issue. Instead, email us directly at the address listed in our [security policy](https://github.com/TreyWW/MyFinances/security/policy).

## 🌟 Contributors

A huge thank you to all our amazing contributors! 🎉

<div align="center">
  <a href="https://github.com/TreyWW/MyFinances/graphs/contributors">
    <img src="https://contrib.rocks/image?repo=TreyWW/MyFinances" alt="Contributors" />
  </a>
</div>

**Want to see your name here?** [Start contributing today!](https://github.com/TreyWW/MyFinances/issues)

## 📄 License

This project is licensed under the **AGPL-3.0 License** - see the [LICENSE](LICENSE) file for details.

## 📈 Star History

<div align="center">
  
[![Star History Chart](https://api.star-history.com/svg?repos=TreyWW/MyFinances&type=Date)](https://star-history.com/#TreyWW/MyFinances&Date)

</div>

---

<div align="center">

**Made with ❤️ by the MyFinances team**

[📚 Docs](https://docs.strelix.org/MyFinances) • [🐛 Report Bug](https://github.com/TreyWW/MyFinances/issues/new) • [💡 Request Feature](https://github.com/TreyWW/MyFinances/issues/new) • [💬 Discussions](https://github.com/TreyWW/MyFinances/discussions)

</div>
