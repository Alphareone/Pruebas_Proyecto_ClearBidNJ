"""Punto único de importación de modelos para poblar Base.metadata."""
from app.models.engagement import (
    Alert,
    CoverageArea,
    SavedProperty,
    Segment,
)
from app.models.geography import County, ZipCode
from app.models.jobs import ExportJob, IngestJob
from app.models.property import (
    Property,
    PropertyDocument,
    PropertyFinancial,
    PropertyLegal,
    PropertyPhysical,
)
from app.models.rules import Rule, RuleResult, TrafficLightResult
from app.models.user import (
    AlertSetting,
    Device,
    OAuthAccount,
    OtpChallenge,
    PasswordResetToken,
    RefreshToken,
    User,
    UserPreference,
)

__all__ = [
    "User", "OAuthAccount", "RefreshToken", "OtpChallenge", "PasswordResetToken",
    "UserPreference", "Device", "AlertSetting",
    "County", "ZipCode",
    "Property", "PropertyFinancial", "PropertyLegal", "PropertyPhysical",
    "PropertyDocument",
    "Rule", "TrafficLightResult", "RuleResult",
    "SavedProperty", "CoverageArea", "Alert", "Segment",
    "IngestJob", "ExportJob",
]
