# -*- encoding: utf-8 -*-
"""Flexibly manage click-back validation links.

Validation links can be used to reset passwords, verify email
addresses, invite new users, and so forth.  Each type of link is
identified by a one-letter action code, keyed to an email template and
a function to handle the click-back request."""
