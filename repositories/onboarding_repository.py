class OnboardingRepository:
    """Handles data persistence or integration with other services."""

    def get_users(self):
        # In production, replace this with DB query
        return [
            {"id": "1", "name": "Test User", "role": "Engineer", "status": "Approved"}
        ]
