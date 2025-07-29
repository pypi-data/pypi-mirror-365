## SafeHTML

A *simple* package for safely rendering HTML using the new [template string syntax (PEP 750)](https://peps.python.org/pep-0750/), in Python `3.14`.

### Example

```python
from safehtml import html

input = "Jacob <script>alert('xss')</script>"
print(html(t"<p>Hello {input}</p>"))
```

Output:
```plaintext
<p>Hello Jacob &lt;script&gt;alert(&#x27;xss&#x27;)&lt;/script&gt;</p>
```

### Install

```bash
uv init
```

```bash
uv python pin 3.14.0rc1
```

```bash
uv add safehtml
```