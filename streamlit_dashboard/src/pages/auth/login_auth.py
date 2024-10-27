# login_auth.py

def authenticate(username, password):
    
    valid_users = {
        "admin": "password",  # Example credentials
        "user": "user123"     
    }

    if username in valid_users and valid_users[username] == password:
        return True
    return False
