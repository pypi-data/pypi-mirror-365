# 🔗 short-url-cli

Make your links short and sweet! 🍬✨
A fun and easy command-line tool for shrinking (and unshrinking!) your URLs. Because who has time for long links? 😎

---

## 🚀 Installation

Ready to get started?
Just run this in your terminal (Python 3.9+ required):

```sh
pip install short-url-cli
```

That’s it! You’re all set. 🎉

---

## 🕹️ Usage

After installation, you'll have a brand new superpower: the `short-url-cli` command! 🦸

### ✂️ Shorten a single URL

```sh
short-url-cli https://example.com
```

Sample output:

```
Short URL: http://tinyurl.com/abc123
```

### 🔗 Shorten multiple URLs at once

Want to shorten multiple URLs? Use the `--multi` flag with comma-separated URLs:

```sh
short-url-cli --multi https://example.com,https://google.com,https://github.com
```

Sample output:

```
                    Shortened URLs
┏━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━┓
┃ Source URL          ┃ Short URL                     ┃ Warning ┃
┡━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━┩
│ https://example.com │ http://tinyurl.com/abc123     │         │
│ https://google.com  │ http://tinyurl.com/def456     │         │
│ https://github.com  │ http://tinyurl.com/ghi789     │         │
└─────────────────────┴───────────────────────────────┴─────────┘
```

### 📋 Important notes

- URLs must include a scheme (http:// or https://)
- For multiple URLs, use commas only (no spaces!)
- Uses TinyURL service for shortening
- Invalid URLs will be marked in the output table

---

## 🤔 Why use short-url-cli?

- Tired of copy-pasting long, ugly links? 😩
- Want to look cool in your group chat? 😎
- Need to save precious characters on social media? 🐦

short-url-cli has you covered! 🎯

---

## 🧑‍💻 Requirements

- Python 3.9 or higher

---

## 📜 License

MIT License.
Go wild, but don’t blame us if your links get too short to find! 😜
