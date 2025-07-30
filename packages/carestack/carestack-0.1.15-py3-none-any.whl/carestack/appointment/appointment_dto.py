from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, Field, ValidationInfo, field_validator

from carestack.common.enums import AppointmentPriority
from carestack.common.error_validation import check_not_empty


class AppointmentDTO(BaseModel):
    """Represents an appointment."""

    practitioner_reference: str = Field(..., alias="practitionerReference")
    patient_reference: str = Field(..., alias="patientReference")
    appointment_start_time: datetime = Field(..., alias="start")
    appointment_end_time: datetime = Field(..., alias="end")
    priority: Optional[AppointmentPriority] = Field(
        AppointmentPriority.EMERGENCY, alias="priority"
    )
    organization_id: Optional[str] = Field(None, alias="organizationId")
    slot: Optional[str] = Field(None, alias="slot")
    appointment_reference: Optional[str] = Field(None, alias="reference")

    @field_validator("practitioner_reference", "patient_reference", "appointment_start_time", "appointment_end_time")
    @classmethod
    def _validate_fields(cls, v: str, info: ValidationInfo) -> str:
        """Validates that required fields are not empty."""
        return check_not_empty(v, info.field_name)


class ResourceType(BaseModel):
    appointment_reference: str = Field(..., alias="reference")
    practitioner_reference: str = Field(..., alias="practitionerReference")
    patientReference: str = Field(..., alias="patientReference")
    slot: str = Field(..., alias="slot")
    priority: str = Field(..., alias="priority")
    appointment_start_time: str = Field(..., alias="start")
    appointment_end_time: str = Field(..., alias="end")
    organization_id: str = Field(..., alias="organizationId")


class CreateAppointmentResponeType(BaseModel):
    type: str
    message: str
    # resourceId: str
    validationErrors: Optional[list[Any]] = None
    resource: ResourceType
    fhirProfileId: Optional[str] = Field(default=None, exclude=True)

    class Config:
        orm_mode = True

class GetAppointmentResponse(BaseModel):
    type: str
    message: str
    request_resource: Optional[list[ResourceType]] = Field(None, alias="requestResource")
    total_records: Optional[int] = Field(None, alias="totaNumberOfRecords")
    next_page: Optional[str] = Field(None, alias="nextPageLink")


class AppointmentResponse(BaseModel):
    type: str
    message: str
    request_resource: Optional[ResourceType] = Field(None, alias="requestResource")
    total_records: Optional[int] = Field(None, alias="totaNumberOfRecords")
    next_page: Optional[str] = Field(None, alias="nextPageLink")

    class Config:
        orm_mode = True

class UpdateAppointmentDTO(BaseModel):
    appointment_start_time: Optional[datetime] = Field(None, alias="start")
    appointment_end_time: Optional[datetime] = Field(None, alias="end")
    priority: Optional[AppointmentPriority] = Field(None)
    slot: Optional[str] = Field(None, alias="slot")

