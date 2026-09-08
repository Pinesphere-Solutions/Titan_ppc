"""Rate limiting for auth endpoints — architecture doc Section 7.3.

Placeholder using slowapi is recommended (pip install slowapi) once the
project is further along; not wired into requirements.txt yet to keep the
initial scaffold minimal. Example usage once installed:

    from slowapi import Limiter
    from slowapi.util import get_remote_address

    limiter = Limiter(key_func=get_remote_address)
    # then: @limiter.limit("5/minute") on the /auth/login route
"""
