from graphene import ObjectType, String, Schema, List
from services.onboarding_service import OnboardingService
from repositories.onboarding_repository import OnboardingRepository

class OnboardingUser(ObjectType):
    id = String()
    name = String()
    role = String()
    status = String()

class Query(ObjectType):
    onboarding_users = List(OnboardingUser)

    def resolve_onboarding_users(self, info):
        service = OnboardingService(OnboardingRepository())
        users = service.get_all_users()
        return [OnboardingUser(**u) for u in users]

schema = Schema(query=Query)
