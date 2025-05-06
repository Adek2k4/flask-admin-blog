from functools import wraps
from flask import g, abort

def admin_required(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if not g.user or not g.user["is_admin"]:
            abort(403)

        return view(**kwargs)
    return wrapped_view
