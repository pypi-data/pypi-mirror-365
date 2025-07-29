"""Cloudstile, the easy to use Cloudflare Turnstile client.

This library provides easy-to-use synchronous and asynchronous clients for Cloudflare's Turnstile service.

Example usage:

    >>> from cloudstile import SyncTurnstile

    >>> client = SyncTurnstile(token="...")

    >>> response = client.validate("...")
    >>> print(response.success)
    True

---

MIT License

Copyright (c) 2024-2025 NotAussie

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from .asyncturnstile import AsyncTurnstile
from .syncturnstile import SyncTurnstile
from .models import Response

__all__ = [
    "AsyncTurnstile",
    "SyncTurnstile",
    "Response",
]
