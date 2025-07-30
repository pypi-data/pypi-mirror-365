from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, RootModel, field_validator

class ProcessDSDto(BaseModel):
    case_type: str = Field(..., alias="caseType")
    files: Optional[List[str]] = None
    encrypted_data: Optional[str] = None
    public_key: Optional[str] = None


class DischargeSummaryResponse(BaseModel):
    """Represents a discharge summary response which is a dictionary."""
    id: str
    discharge_summary: Optional[dict[str, Any]] = Field(None, alias="dischargeSummary")
    extracted_data: dict[str, Any] = Field(..., alias="extractedData")
    fhir_bundle: dict[str, Any] = Field(..., alias="fhirBundle")

    @field_validator("discharge_summary", mode="before")
    @classmethod
    def handle_empty_string(cls, value):
        if value == '' or value is None:
            return None
        if isinstance(value, dict):
            return value
        raise ValueError("dischargeSummary must be a dictionary or empty string")
    
class GenerateFhirBundleDto(BaseModel):
    case_type: str = Field(..., alias="caseType")
    record_id: Optional[str] = Field(None, alias="recordId")
    extracted_data: Optional[Dict[str, Any]] = Field(None, alias="extractedData")
    encrypted_data: Optional[str] = Field(None, alias="encryptedData")
    public_key: Optional[str] = Field(None, alias="publicKey")


class FhirBundleResponse(RootModel[Dict[str, Any]]):
    """Represents a FHIR bundle response which is a dictionary."""

    pass
