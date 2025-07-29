# llm-contracts

![PyPI version](https://img.shields.io/pypi/v/llm-contracts)
![Python](https://img.shields.io/badge/python-3.8+-blue)
![License](https://img.shields.io/github/license/Maxamed/llm-contract)
![Tests](https://img.shields.io/badge/tests-84%25%20coverage-brightgreen)
![Build Status](https://img.shields.io/badge/build-passing-brightgreen)

> 🛡️ **"ESLint + Pytest" for AI responses** — Catch LLM mistakes before they reach production.  
> Schema validation, content linting, and professional reports for any LLM.

---

## 📦 Install

```bash
pip install llm-contracts
```

---

## ⚡ Why `llm-contracts`?

LLMs are **fluent, confident, and totally wrong** just often enough to break your app.

- **Air Canada's chatbot** promised non-existent bereavement fares → Legal action
- **CNET's AI** published financial advice with wrong interest rates → Public corrections  
- **ChatGPT lawyer** submitted fake legal citations in court → Professional sanctions

`llm-contracts` validates every AI response **before** it causes problems.

---

## 🚀 Quick Start

### CLI
```bash
# Validate AI output against schema
llm-validate output.json --schema schema.yaml

# Generate professional reports
llm-validate output.json --schema schema.yaml --html-report report.html
```

### Python API
```python
from llm_contracts import contracts

# Validate output against schema
result = contracts.validate(data, "schema.yaml")

if not result.is_valid:
    print("AI failed validation:")
    for error in result.errors:
        print(f"  - {error}")

# Generate reports
contracts.generate_report(result, "report.html", "schema.yaml", format="html")
```

---

## ✅ Key Features

* **Schema Validation** — Ensure proper JSON/YAML structure and data types
* **Content Linting** — Check keywords, tone, word count, patterns, quality rules  
* **Professional Reports** — Beautiful HTML and Markdown validation reports
* **Framework Agnostic** — Works with OpenAI, Anthropic, local models, any LLM
* **CLI + Python API** — Use in scripts or integrate into applications
* **Zero Vendor Lock-in** — Pure validation logic, no external API calls required

---

## 📋 Example Schema

```yaml
schema:
  title:
    type: str
    min_length: 10
  description:
    type: str
    min_length: 100

rules:
  - keyword_must_include: ["quality", "premium"]
  - keyword_must_not_include: ["cheap", "defective"]
  - no_placeholder_text: "\\[YOUR_TEXT_HERE\\]"
  - word_count_min: 100
  - word_count_max: 500
```

**Result:** Every AI response gets validated before reaching your users. **No more silent failures.**

---

## 📚 Documentation & Links

* 📖 [Complete Documentation & Whitepaper](https://maxamed.github.io/llm-contract/)
* 🚀 [Getting Started Guide](https://maxamed.github.io/llm-contract/getting-started)
* 💡 [Real-World Examples](https://maxamed.github.io/llm-contract/examples)
* 🛠 [GitHub Source](https://github.com/Maxamed/llm-contract)
* 🐛 [Report Issues](https://github.com/Maxamed/llm-contract/issues)

---

## 🤝 Contributors

**Created by [Mohamed Jama](https://www.linkedin.com/in/mohamedjama/)** - Built for developers shipping AI features in production.

**Major Contributors:**
- **[Abdirahman Attila](https://github.com/Attili-sys)** - Frontend web interface, comprehensive documentation website, enhanced testing suite, and Jekyll/GitHub Pages setup

We welcome contributions! See [CONTRIBUTING.md](https://github.com/Maxamed/llm-contract/blob/main/CONTRIBUTING.md) for guidelines.

---

## 🏷 License

MIT © Mohamed Jama - see [LICENSE](https://github.com/Maxamed/llm-contract/blob/main/LICENSE) file for details.

---

**Stop hoping your AI gets it right. Start knowing it does.** 