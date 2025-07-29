# gitlab-wrapper

A Python-based toolkit to interact with GitLab APIs on Swecha's self-hosted GitLab instance [code.swecha.org](https://code.swecha.org). `gitlab-wrapper` streamlines GitLab workflows by offering tools to track and summarize contributions, Automate merge request pipelines, Generate issue reports and activity logs and Ensure development standards and reproducibility across projects.

## 🚀 Features

- Onboarding users to specific groups
- Generates commit summaries and member-wise contribution stats
- Generates Daily reports based on the Issues created and contributions done
- Get specific information of a individual user

## 🛠️ Installation Setup

Using `pip`

```bash
pip install gitlab-wrapper-sdk
```

Using `uv`

```bash
uv pip install gitlab-wrapper-sdk
```

## 🚀 Initial Client Setup

To start using the SDK, initialize the `GitLabClient` with your GitLab instance URL and a valid private token:

```python
from gitlab_wrapper.client import GitLabClient

client = GitLabClient(
    base_url="gitlab_instance_url",
    private_token="your_gitlab_token/admin_token"
)
```

**Example: base_url="https://code.swecha.org"**

## 📁 Project Structure

```
gitlab-wrapper/
├── .gitlab/
│   ├── templates/
│   │    ├──MR_template.md
│   │    └──issue_template.md
│   └── workflow/
│        └── lint.yml
├── gitlab-wrapper/
│   ├── __init__.py
│   ├── client.py                 # Main wrapper logic
│   └── apis/                     # Modular API handlers
│        ├── __init__.py
│        └── users.py
├── tests/                        # Unit tests for client
│   ├── __init__.py
│   ├── confest.py
│   ├── test_client.py
│   └── test_users.py
│
├── .env.example
├── .gitignore
├── .gitlab-ci.yml                # GitLab CI pipeline config
├── .pre-comit-config.yaml
├── LICENSE                       # GNU GPL v3 License
├── CHANGELOG.md
├── README.md                     # Project overview and usage
├── CONTRIBUTING.md               # Contribution guidelines
├── CODE_OF_CONDUCT.md            # Community standards
├── pyproject.toml                # Project configuration
└── uv.lock
```

## 💬 Support

Need help or have a question about gitlab-wrapper?  
E-Mail the maintainers at ranjithraj@swecha.net

- 🐛 **Found a bug?**  
  If you encounter any bugs in the codebase, please create an issue with label `bug`

- 💡 **Have a feature request or idea?**  
  Feel free to create a new issue labeled `feature-request` availabe in tags.

Make sure to follow the provided [ISSUE BOARD TEMPLATE](.gitlab/templates/issue_template.md)

# Contributing to gitlab-wrapper

🎉 Thank you for considering contributing to gitlab-wrapper

We welcome all kinds of contributions: code, documentation, bug reports, feature requests, ideas, and feedback, refer this [DOCUMENTATION](CONTRIBUTING.md).

## Realtime Applications of Wrapper

Several applications have integrated Gitlab-wrapper into their codebase.

- [SoAI - Dashboard](https://soai-accounts-dashboard.streamlit.app/)
- [BITS - Dashboard](https://bits-ps1-dashboard.streamlit.app)
- [ICFAI - Dashboard](https://progress4icfai-ogwz5b4zbt2bg2chbbtf46.streamlit.app/)

## 📝 License

This project is licensed under the GNU General Public License v3.0.

You are free to use, modify, and distribute this software for any purpose, provided that:

The original license and copyright notice are included.
Any derivative work must also be distributed under the same license. See the [LICENSE](LICENSE)
