# 🚀 DevAssist MCP Server

**A production-ready Python MCP Server for GitHub & Competitive Programming**

![Python](https://img.shields.io/badge/Python-3.12%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![MCP](https://img.shields.io/badge/MCP-Protocol-blueviolet?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)

---

## 📖 Overview

DevAssist MCP is a **Model Context Protocol (MCP) server** that bridges the gap between AI assistants and developer resources. It exposes two powerful tools — **GitHub Assistant** and **Competitive Programming Assistant** — that any MCP-compatible AI agent (Claude Desktop, Cursor, VS Code Copilot) can use to fetch real-time data.

### ✨ Key Features

| Feature | Description |
|---------|-------------|
| 🐙 **GitHub Integration** | User profiles, repo info, commits, PRs, issues, statistics |
| 🏆 **Codeforces Integration** | Profiles, contest history, rating tracking, submissions |
| 🧠 **Weak Topic Analysis** | AI-powered identification of competitive programming weak areas |
| 💡 **Smart Recommendations** | Personalized problem suggestions based on skill gaps |
| ⚡ **Async Architecture** | Non-blocking I/O with `httpx` for maximum performance |
| 🔒 **Production Ready** | Logging, error handling, type safety, comprehensive tests |

---

## 🏗️ Architecture

```mermaid
graph TD
    A["🤖 AI Agent<br/>(Claude / Cursor / VS Code)"] -->|MCP Protocol| B["⚙️ DevAssist MCP Server"]
    B --> C["🐙 github_assistant"]
    B --> D["🏆 cp_assistant"]
    C --> E["GitHub Service Layer"]
    D --> F["Codeforces Service Layer"]
    E -->|httpx async| G["GitHub REST API v3"]
    F -->|httpx async| H["Codeforces API"]
    
    style A fill:#4A90D9,stroke:#2C5F99,color:#fff
    style B fill:#6C3483,stroke:#4A235A,color:#fff
    style C fill:#27AE60,stroke:#1E8449,color:#fff
    style D fill:#E67E22,stroke:#CA6F1E,color:#fff
```

---

## 📋 Prerequisites

- **Python 3.12+**
- **GitHub Personal Access Token** ([Generate here](https://github.com/settings/tokens)) — for higher API rate limits
- **pip** or **uv** package manager

---

## 💻 Installation

### Option 1: Using `uv` (Recommended)

```bash
# Clone the repository
git clone https://github.com/your-username/devassist-mcp.git
cd devassist-mcp

# Create virtual environment and install dependencies
uv venv
uv pip install -r requirements.txt
```

### Option 2: Using `pip`

```bash
# Clone the repository
git clone https://github.com/your-username/devassist-mcp.git
cd devassist-mcp

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

## ⚙️ Configuration

1. Copy the environment template:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your settings:
   ```env
   GITHUB_TOKEN=ghp_your_personal_access_token_here
   LOG_LEVEL=INFO
   ```

> **Note:** The GitHub token is optional but recommended. Without it, you're limited to 60 API requests/hour. With a token, you get 5,000 requests/hour.

---

## 🚀 Usage

### Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "devassist-mcp": {
      "command": "python",
      "args": ["C:/path/to/devassist-mcp/server.py"],
      "env": {
        "GITHUB_TOKEN": "ghp_your_token_here"
      }
    }
  }
}
```

### Cursor

Add to your Cursor MCP settings (`.cursor/mcp.json`):

```json
{
  "mcpServers": {
    "devassist-mcp": {
      "command": "python",
      "args": ["C:/path/to/devassist-mcp/server.py"],
      "env": {
        "GITHUB_TOKEN": "ghp_your_token_here"
      }
    }
  }
}
```

### VS Code (with Copilot)

Add to your VS Code settings:

```json
{
  "mcp": {
    "servers": {
      "devassist-mcp": {
        "command": "python",
        "args": ["C:/path/to/devassist-mcp/server.py"],
        "env": {
          "GITHUB_TOKEN": "ghp_your_token_here"
        }
      }
    }
  }
}
```

### Running Standalone

```bash
python server.py
```

---

## 🛠️ Tool Documentation

### Tool 1: `github_assistant`

| Action | Description | Requires `repository` |
|--------|-------------|:---------------------:|
| `get_user_profile` | Get GitHub user profile | ❌ |
| `get_user_repos` | List all public repositories owned by a user | ❌ |
| `get_user_activity` | Get recent user activity (commits, PRs, stars) | ❌ |
| `get_repo_info` | Get repository details | ✅ |
| `get_latest_commits` | Get recent commits | ✅ |
| `get_repo_stats` | Get repository statistics | ✅ |
| `get_repo_languages` | Detailed programming language percentage breakdown | ✅ |
| `get_repo_contributors` | Top code contributors to a repository | ✅ |
| `get_latest_release` | Latest release version & release notes | ✅ |
| `get_pull_requests` | Get pull requests | ✅ |
| `get_issues` | Get repository issues | ✅ |

**Example — Get User Profile:**
```
"Show me the GitHub profile of octocat"
```
```json
{
  "login": "octocat",
  "name": "The Octocat",
  "public_repos": 42,
  "followers": 20000,
  "location": "San Francisco"
}
```

**Example — Get Repo Stats:**
```
"What are the stats for octocat/Hello-World?"
```
```json
{
  "repository": "octocat/Hello-World",
  "stars": 2500,
  "forks": 450,
  "language": "Python",
  "open_issues": 12
}
```

---

### Tool 2: `cp_assistant`

| Action | Description |
|--------|-------------|
| `get_user_profile` | Get Codeforces rating and rank |
| `get_contest_history` | Past contest participation |
| `get_recent_submissions` | Recent problem submissions |
| `get_rating_history` | Rating changes over time |
| `analyze_weak_topics` | Identify weak problem areas |
| `recommend_problems` | Personalized problem suggestions |

**Example — Analyze Weak Topics:**
```
"Analyze the weak topics for Codeforces user tourist"
```
```json
[
  {
    "tag": "geometry",
    "total_attempts": 15,
    "successful": 5,
    "failed": 10,
    "success_rate": 33.3
  }
]
```

**Example — Get Recommendations:**
```
"Recommend practice problems for my Codeforces handle"
```
```json
[
  {
    "name": "Theatre Square",
    "rating": 1000,
    "tags": ["math"],
    "url": "https://codeforces.com/problemset/problem/1/A"
  }
]
```

---

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=. --cov-report=term-missing

# Run specific test file
pytest tests/test_github_service.py -v

# Run specific test
pytest tests/test_codeforces_service.py::test_analyze_weak_topics -v
```

---

## 📁 Project Structure

```
devassist-mcp/
├── server.py                          # MCP server entry point
├── config.py                          # Pydantic settings
├── .env.example                       # Environment template
├── requirements.txt                   # Dependencies
├── pyproject.toml                     # Project metadata & tool configs
├── Dockerfile                         # Multi-stage Docker build
├── .dockerignore                      # Docker build exclusions
├── .gitignore                         # Git exclusions
├── README.md                          # This file
├── tools/
│   ├── github.py                      # GitHub MCP tool
│   └── cp.py                          # Codeforces MCP tool
├── services/
│   ├── github_service.py              # GitHub API client
│   └── codeforces_service.py          # Codeforces API client
├── models/
│   ├── github_models.py               # GitHub Pydantic models
│   └── cp_models.py                   # Codeforces Pydantic models
├── utils/
│   ├── logger.py                      # Structured logging
│   └── exceptions.py                  # Custom exception hierarchy
├── tests/
│   ├── conftest.py                    # Shared test fixtures
│   ├── test_github_service.py         # GitHub service tests
│   ├── test_codeforces_service.py     # Codeforces service tests
│   ├── test_github_tool.py            # GitHub tool tests
│   └── test_cp_tool.py               # Codeforces tool tests
└── logs/                              # Log files (auto-created)
```

---

## 🐳 Deployment

### Docker

```bash
# Build the image
docker build -t devassist-mcp .

# Run the container
docker run -e GITHUB_TOKEN=ghp_your_token devassist-mcp
```

### Railway

1. Connect your GitHub repository
2. Set environment variable: `GITHUB_TOKEN`
3. Deploy — Railway auto-detects the Dockerfile

### Render

1. Create a new **Background Worker**
2. Connect your repository
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `python server.py`
5. Add environment variable: `GITHUB_TOKEN`

---

## 🔮 Future Enhancements

- [ ] 🟡 LeetCode integration
- [ ] 🟠 CodeChef integration
- [ ] 🔵 Response caching with TTL
- [ ] 🟢 Request history tracking
- [ ] 🟣 WebSocket support for live updates
- [ ] ⚪ Multi-language support

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

### Code Quality

```bash
# Format code
black .

# Lint
ruff check .

# Type check
mypy .
```

---

## 📄 License

This project is licensed under the **MIT License**. See [LICENSE](LICENSE) for details.

---

<div align="center">

**Built with ❤️ using Python, FastMCP, and httpx**

</div>
