class UserManager:
    """Manage user profiles (in-memory demo)."""
    users = {}

    def create_user(self, username, info):
        """Create a new user profile."""
        if username in self.users:
            return {'error': 'User already exists.'}
        self.users[username] = info
        return {'status': 'success', 'user': self.users[username]}

    def get_user(self, username):
        """Get a user profile by username."""
        return self.users.get(username, None) 