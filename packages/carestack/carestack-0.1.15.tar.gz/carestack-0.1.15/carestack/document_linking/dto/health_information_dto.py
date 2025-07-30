from typing import Optional, Any
from pydantic import BaseModel, Field, ValidationInfo, field_validator

from carestack.common.enums import HealthInformationTypes
from carestack.common.error_validation import check_not_empty
from carestack.encounter.dto.encounter_dto import (
    DiagnosticReportDTO,
    DischargeSummaryDTO,
    HealthDocumentRecordDTO,
    ImmunizationRecordDTO,
    OPConsultationDTO,
    PrescriptionRecordDTO,
    WellnessRecordDTO,
)

DTO_MAPPING = {
    HealthInformationTypes.OPCONSULTATION: OPConsultationDTO,
    HealthInformationTypes.DISCHARGE_SUMMARY: DischargeSummaryDTO,
    HealthInformationTypes.PRESCRIPTION: PrescriptionRecordDTO,
    HealthInformationTypes.WELLNESS_RECORD: WellnessRecordDTO,
    HealthInformationTypes.IMMUNIZATION_RECORD: ImmunizationRecordDTO,
    HealthInformationTypes.DIAGNOSTIC_REPORT: DiagnosticReportDTO,
    HealthInformationTypes.HEALTHDOCUMENT_RECORD: HealthDocumentRecordDTO,
}


class HealthInformationDTO(BaseModel):
    """Represents health information data."""

    raw_fhir: Optional[bool] = Field(None, alias="rawFhir")
    fhir_document: dict[str, Any] = Field(None, alias="fhirDocument")
    information_type: HealthInformationTypes = Field(..., alias="informationType")

    @field_validator("fhir_document")
    @classmethod
    def _fhir_document_validate_if_raw_fhir(
        cls, v: Optional[dict], info: ValidationInfo
    ) -> Optional[dict]:
        """Validates that fhirDocument is provided if rawFhir is True."""
        if info.data.get("raw_fhir") and v is None:
            raise ValueError("fhirDocument must be provided when rawFhir is True")
        return v

    @field_validator("information_type")
    @classmethod
    def _information_type_not_empty(
        cls,
        v: HealthInformationTypes,
        info: ValidationInfo,
    ) -> HealthInformationTypes:
        """Validates that the information type is not empty."""
        return check_not_empty(v, info.field_name)
