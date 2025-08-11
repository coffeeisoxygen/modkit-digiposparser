"""Schemas for modules configuration.

This module defines the Pydantic models for validating modules.yaml structure.
Supports hierarchical provider -> members structure with rich metadata.
"""

from pydantic import BaseModel, ConfigDict, EmailStr, Field, HttpUrl


class ModuleMember(BaseModel):
    """Individual module instance within a provider.

    Represents a specific account/connection to a provider service.
    Multiple members can exist per provider for load balancing or different environments.
    """

    model_config = ConfigDict(
        extra="forbid", str_strip_whitespace=True, validate_default=True
    )

    # Identity
    moduleid: str = Field(
        ...,
        description="Unique identifier for this module instance",
        min_length=1,
        max_length=50,
        pattern=r"^[A-Z0-9]+$",
    )
    name: str = Field(
        ...,
        description="Human-readable name for this module",
        min_length=1,
        max_length=100,
    )

    # Authentication
    username: str = Field(
        ..., description="Username for API authentication", min_length=1
    )
    pin: str | int = Field(..., description="PIN for API authentication")
    password: str = Field(
        ..., description="Password for API authentication", min_length=1
    )

    # Contact & Status
    msisdn: str | int = Field(
        ..., description="Mobile number associated with this module"
    )
    email: EmailStr = Field(..., description="Email for notifications and monitoring")
    is_active: bool = Field(
        default=True, description="Whether this module is active and available for use"
    )

    # Connection Configuration
    base_url: HttpUrl = Field(..., description="Base URL for API endpoints")
    timeout: int = Field(
        default=5, description="Request timeout in seconds", ge=1, le=300
    )
    max_retries: int = Field(
        default=3, description="Maximum number of retry attempts", ge=0, le=10
    )
    second_wait: int = Field(
        default=2, description="Seconds to wait between retries", ge=0, le=60
    )


class ModuleProvider(BaseModel):
    """Provider configuration containing multiple module instances.

    Represents a service provider (like digipos, isimple) with multiple
    accounts/instances for load balancing or different environments.
    """

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    provider: str = Field(
        ...,
        description="Provider name (digipos, isimple, etc)",
        min_length=1,
        max_length=50,
        pattern=r"^[a-z][a-z0-9_]*$",
    )
    group: str | None = Field(
        default=None,
        description="Optional grouping for future categorization",
        max_length=100,
    )
    description: str = Field(
        ...,
        description="Human-readable description of this provider",
        min_length=1,
        max_length=200,
    )
    members: list[ModuleMember] = Field(
        ..., description="List of module instances for this provider", min_length=1
    )

    def get_active_members(self) -> list[ModuleMember]:
        """Get only active module members."""
        return [member for member in self.members if member.is_active]

    def get_member_by_id(self, moduleid: str) -> ModuleMember | None:
        """Get specific member by moduleid."""
        for member in self.members:
            if member.moduleid == moduleid:
                return member
        return None


class ModulesConfig(BaseModel):
    """Root configuration for all module providers.

    Contains list of all providers with their respective module instances.
    """

    model_config = ConfigDict(extra="forbid")

    providers: list[ModuleProvider] = Field(
        ..., description="List of all module providers"
    )

    def get_provider(self, provider_name: str) -> ModuleProvider | None:
        """Get specific provider by name."""
        for provider in self.providers:
            if provider.provider == provider_name:
                return provider
        return None

    def get_member(self, provider_name: str, moduleid: str) -> ModuleMember | None:
        """Get specific member across all providers."""
        provider = self.get_provider(provider_name)
        if provider:
            return provider.get_member_by_id(moduleid)
        return None

    def get_all_active_members(
        self, provider_name: str | None = None
    ) -> list[ModuleMember]:
        """Get all active members, optionally filtered by provider."""
        active_members = []
        for provider in self.providers:
            if provider_name is None or provider.provider == provider_name:
                active_members.extend(provider.get_active_members())
        return active_members
