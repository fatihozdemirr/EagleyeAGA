from flask import g, session
from app.main.Models import User

def get_logged_in_user():
    if 'user' in g:
        print('User from g:', g.user)
        return g.user.username
    
    if 'username' in session:
        user = User.query.filter_by(username=session['username']).first()
        g.user = user
        print('User from session:', user)
        return user.username if user else None

    return None