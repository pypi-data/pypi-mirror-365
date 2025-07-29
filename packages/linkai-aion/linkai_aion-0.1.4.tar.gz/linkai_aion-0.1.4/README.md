# linkai-aion

**🚀 LinkAI-Aion v0.1.3 — Smarter AI Utilities, Simplified**

**linkai-aion** is a comprehensive Python utility library created by [LinkAI](https://linkaiapps.com), designed to empower AI projects, automation tools, and productivity workflows. With this new version, we're bringing smarter tools, better performance, and more developer-friendly features than ever.

It's designed for developers who want clean, reusable functions to speed up their workflow — and it's just the beginning. Future versions will introduce AI features built on top of this solid foundation.

---

## ✨ Features

- 🌍 **Language Detection**  
  Multi-language keyword recognition for fast and accurate language identification

- 🛡️ **Sensitive Data Scanning**  
  Detects patterns such as emails, passwords, phone numbers, and API keys — keeping your data safer

- 🧠 **Text Intelligence**  
  Handy utilities to detect questions, palindromes, emojis, and even visual symbols in your text

- 🧰 **Expanded Utilities**  
  Now includes hashers, validators, data formatters, random generators, and many more helpful tools

- 📝 **Text Utilities**  
  `count_words()`, `extract_emails()`, `summarize_text()`, `highlight_keywords()` and more

- 📂 **File Handling**  
  `read_file()`, `write_file()`, `append_file()` — simple and clean

- 🧾 **Parser Tools**  
  `extract_numbers()` from messy strings

- 🔄 **Future-Proof**  
  Built to integrate with LinkAI APIs and models in upcoming versions

---

## 📦 Installation

```bash
pip install linkai-aion
```

## 🚀 Quick Start

```python
from aion import text, files, parser, ai_utils

# Text processing
text.count_words("Hello world!")  # 2
emails = text.extract_emails("Contact us at info@linkai.com")

# AI-powered features
language = ai_utils.detect_language("Bonjour le monde")  # 'french'
sensitive_data = ai_utils.scan_sensitive_data("My password is secret123")  # ['secret123']
is_question = ai_utils.is_question("What is your name?")  # True

# File operations
content = files.read_file("data.txt")
files.write_file("output.txt", "Hello World!")

# Parsing
numbers = parser.extract_numbers("Price: $99.99 and $149.99")
```

## 🆕 What's New in v0.1.3

### 🌍 Language Detection
Now supports basic multi-language keyword recognition for fast and accurate language identification.

### 🛡️ Sensitive Data Scanning
Detects patterns such as emails, passwords, phone numbers, and API keys — keeping your data safer.

### 🧠 Text Intelligence
Handy utilities to detect questions, palindromes, emojis, and even visual symbols in your text.

### 🧰 Expanded Utilities
Now includes hashers, validators, data formatters, random generators, and many more helpful tools.
