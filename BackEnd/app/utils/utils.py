from flask import g, session
from app.main.Models import User

def get_logged_in_user():
    if 'user' in g and g.user:
        return g.user.username, g.user.role
    
    if 'username' in session:
        user = User.query.filter_by(username=session['username']).first()
        g.user = user
        return user.username, user.role if user and user.role else (None, None)
    
    return None, None