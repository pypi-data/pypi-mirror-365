# texttoolkitx

**texttoolkitx** is a lightweight, developer-friendly Python package offering utility functions to streamline string manipulation and text formatting. It's perfect for developers, data engineers, and students who frequently work with raw or unstructured text.

---

## ✨ Features

- 🔤 Convert to `snake_case`, `camelCase`, and `PascalCase`
- 🔄 Reverse any string
- 🧹 Normalize and clean messy text (e.g. extra spaces, special characters)
- 🔢 Count characters, words, and lines
- 🔎 Check for palindromes or repeated characters
- ✂️ Truncate long strings with custom suffixes

---

## 📦 Installation

Install from the official PyPI index:

```bash
pip install texttoolkitx


🚀 Usage
Here are a few simple examples to get started:

1. Import the functions
from texttoolkitx import (
    clean_text,
    is_valid_email,
    to_snake_case,
    reverse_string,
    count_words,
    truncate_text
)

2. Clean messy text

text = " Hello!! This is messy??? "
cleaned = clean_text(text)
print(cleaned)  # Output: "Hello This is messy"

3. Convert string to snake_case

print(to_snake_case("HelloWorldExample"))  # Output: hello_world_example

4. Reverse a string

print(reverse_string("Python"))  # Output: nohtyP

5. Count words in a sentence

sentence = "This is a test."
print(count_words(sentence))  # Output: 4

6. Truncate text

long_text = "This sentence is too long to display completely."
print(truncate_text(long_text, max_length=20))  # Output: "This sentence is..."

🤝 Contributing
Contributions, issues, and feature requests are welcome!
Feel free to check issues and submit a pull request.

🌐 Project Links
🔗 PyPI: texttoolkitx

💻 GitHub: https://github.com/Mahdirizvi114/texttoolkitx

