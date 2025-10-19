from repositories.onboarding_repository import OnboardingRepository

class OnboardingService:
    def __init__(self, repo: OnboardingRepository):
        self.repo = repo

    def get_all_users(self):
        return self.repo.get_users()

    def generate_workflow(self, user_id: str, role: str):
        users = self.repo.get_users()
        user = next((u for u in users if u["id"] == user_id and u["role"] == role), None)
        if not user:
            return None

        workflow = f"AI onboarding for {role}: assign tools, schedule training."
        if role == "Engineer":
            workflow += " Include dev environment setup and code review session."
        return {"user": user, "workflow_plan": workflow}
