from datetime import datetime

class ReminderManager:
    """Manage medication reminders for users (in-memory demo)."""
    reminders = {}

    def set_reminder(self, user, medicine, time):
        """Set a medication reminder for a user."""
        if user not in self.reminders:
            self.reminders[user] = []
        self.reminders[user].append({'medicine': medicine, 'time': time, 'set_at': datetime.now().isoformat()})
        return {'status': 'success', 'reminders': self.reminders[user]}

    def get_reminders(self, user):
        """Get all reminders for a user."""
        return self.reminders.get(user, []) 