from dataclasses import dataclass
from typing import Optional
from pydantic import BaseModel, Field, validator
from datetime import datetime


# Domain dataclass (simple, lightweight domain object)
@dataclass
class OnboardingUserDomain:
    id: str
    name: str
    role: str
    status: str = "Pending"
    created_at: datetime = datetime.utcnow()


# Pydantic model for validation and transport (API layer)
class OnboardingUserSchema(BaseModel):
    id: str = Field(..., description="Unique identifier for the user")
    name: str = Field(..., min_length=1, description="Full name of the user")
    role: str = Field(..., min_length=1, description="Role assigned to the user")
    status: Optional[str] = Field(default="Pending", description="Onboarding status")
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)

    @validator("id")
    def id_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("id must be a non-empty string")
        return v

    @validator("role")
    def role_normalize(cls, v):
        return v.strip().title()

    def to_domain(self) -> OnboardingUserDomain:
        """Convert schema to domain object."""
        return OnboardingUserDomain(
            id=self.id,
            name=self.name,
            role=self.role,
            status=self.status or "Pending",
            created_at=self.created_at or datetime.utcnow()
        )

    @classmethod
    def from_domain(cls, domain: OnboardingUserDomain) -> "OnboardingUserSchema":
        return cls(
            id=domain.id,
            name=domain.name,
            role=domain.role,
            status=domain.status,
            created_at=domain.created_at,
        )


# Small helper factory for tests / fixtures
def make_test_user(id: str = "1", name: str = "Test User", role: str = "Engineer", status: str = "Approved") -> OnboardingUserSchema:
    return OnboardingUserSchema(id=id, name=name, role=role, status=status)
