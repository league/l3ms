# l3ms.utils    -*- coding: utf-8 -*-
# Copyright ©2011 by Christopher League <league@contrapunctus.net>
#
# This is free software but comes with ABSOLUTELY NO WARRANTY.
# See the GNU General Public License version 3 for details.

from django.http import Http404

def except404(exceptions=[]):
    """Decorator that converts selected exception types to Http404."""
    def wrap(f):
        def new_f(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except Exception as x:
                raise Http404 if type(x) in exceptions else x
        return new_f
    return wrap
