from functools import wraps
from typing import Callable

from fastapi.responses import HTMLResponse


def add_mermaid_support(func: Callable[..., HTMLResponse]):
    """在</body>标签前插入mermaid js

    https://mermaid-js.github.io/mermaid/#/n00b-gettingStarted?id=requirements-for-the-mermaid-api
    """
    mermaid_js = '''
    
    <script type="module">
      import mermaid from 'https://unpkg.com/mermaid@9/dist/mermaid.esm.min.mjs';
      mermaid.initialize({ startOnLoad: true });
    </script>

    '''

    @wraps(func)
    def decorator(*args, **kwargs) -> HTMLResponse:
        res = func(*args, **kwargs)
        content = res.body.decode(res.charset)
        index = content.find("</body>")
        if index != -1:
            content = content[:index] + mermaid_js + content[index:]
        return HTMLResponse(content)

    return decorator
