from typing import Any, Optional, Union
from pydantic import BaseModel, Field, ValidationInfo, field_validator, model_validator
from carestack.common.enums import CaseType
from carestack.common.error_validation import check_not_empty


class VitalSign(BaseModel):
    value: str = Field(..., description="The value of the vital sign.")
    unit: str = Field(..., description="The unit of the vital sign.")

    @field_validator("value", "unit")
    @classmethod
    def _validate_fields(cls, v: str, info: ValidationInfo) -> str:
        """Validates that required fields are not empty."""
        return check_not_empty(v, info.field_name)


class PhysicalExamination(BaseModel):
    blood_pressure: VitalSign = Field(
        ..., alias="bloodPressure", description="Blood pressure reading."
    )
    heart_rate: VitalSign = Field(
        ..., alias="heartRate", description="Heart rate reading."
    )
    respiratory_rate: VitalSign = Field(
        ..., alias="respiratoryRate", description="Respiratory rate reading."
    )
    temperature: VitalSign = Field(..., description="Temperature reading.")
    oxygen_saturation: VitalSign = Field(
        ..., alias="oxygenSaturation", description="Oxygen saturation reading."
    )
    height: VitalSign = Field(..., description="Height measurement.")
    weight: VitalSign = Field(..., description="Weight measurement.")


class MedicalHistoryItem(BaseModel):
    condition: Optional[str] = Field(
        None, description="A medical condition in the patient's history."
    )
    procedure: Optional[str] = Field(
        None, description="A medical procedure in the patient's history."
    )

    @field_validator("condition", "procedure")
    @classmethod
    def _validate_fields(cls, v: Optional[str], info: ValidationInfo) -> Optional[str]:
        """Validates that condition and procedure is not empty if provided."""
        if v is not None:
            return check_not_empty(v, info.field_name)
        return v


class FamilyHistoryItem(BaseModel):
    relation: str = Field(..., description="The relation to the patient.")
    condition: str = Field(..., description="The medical condition of the relative.")

    @field_validator("relation", "condition")
    @classmethod
    def _validate_fields(cls, v: str, info: ValidationInfo) -> str:
        """Validates that required fields are not empty."""
        return check_not_empty(v, info.field_name)


class ProcedureItem(BaseModel):
    description: str = Field(..., description="Description of the procedure.")
    complications: Optional[str] = Field(
        None, description="Any complications during the procedure."
    )

    @field_validator("description", "complications")
    @classmethod
    def _validate_fields(cls, v: str, info: ValidationInfo) -> str:
        """Validates that required fields are not empty."""
        return check_not_empty(v, info.field_name)


class InvestigationItem(BaseModel):
    observations: dict[str, VitalSign]
    status: str
    recordedDate: str


class LabReportItem(BaseModel):
    observations: dict[str, VitalSign]
    status: str
    recordedDate: str
    category: str
    conclusion: str


class PatientDetails(BaseModel):
    name: Optional[str] = Field(None, alias="Name", description="The patient's name.")
    age: Optional[str] = Field(None, alias="Age", description="The patient's age.")
    sex: Optional[str] = Field(None, alias="Sex", description="The patient's sex.")
    date_of_birth: Optional[str] = Field(
        None, alias="Date Of Birth", description="The patient's date of birth."
    )
    date_of_admission: Optional[str] = Field(
        None, alias="Date Of Admission", description="The patient's date of admission."
    )
    address: Optional[str] = Field(
        None, alias="Address", description="The patient's address."
    )
    contact_number: Optional[str] = Field(
        None, alias="Contact Number", description="The patient's contact number."
    )
    uhid: Optional[str] = Field(None, alias="UHID", description="The patient's UHID.")
    ip_number: Optional[str] = Field(
        None, alias="IP Number", description="The patient's IP number."
    )
    marital_status: Optional[str] = Field(
        None, alias="Marital Status", description="The patient's marital status."
    )


class DoctorDetails(BaseModel):
    name: str = Field(..., alias="Name", description="The doctor's name.")
    designation: str = Field(
        ..., alias="Designation", description="The doctor's designation."
    )
    department: str = Field(
        ..., alias="Department", description="The doctor's department."
    )


class CommonHealthInformationDTO(BaseModel):
    patient_details: PatientDetails = Field(
        ..., alias="Patient Details", description="Patient's information."
    )
    doctor_details: list[DoctorDetails] = Field(
        ..., alias="Doctor Details", description="Doctor's information."
    )
    chief_complaints: str = Field(
        ..., alias="chiefComplaints", description="The patient's chief complaints."
    )
    physical_examination: PhysicalExamination = Field(
        ..., alias="physicalExamination", description="Patient's physical examination."
    )

    medical_history: Optional[list[MedicalHistoryItem]] = Field(
        None, alias="medicalHistory", description="Patient's medical history."
    )

    family_history: Optional[list[FamilyHistoryItem]] = Field(
        None, alias="familyHistory", description="Patient's family history."
    )

    condtions: Optional[list[str]] = Field(None, description="Patient's conditions.")

    current_procedures: Optional[list[ProcedureItem]] = Field(
        None, alias="currentProcedures", description="Patient's procedures."
    )
    current_medications: Optional[list[str]] = Field(
        None, alias="currentMedications", description="Patient's medications."
    )
    prescribed_medications: Optional[list[str]] = Field(
        None,
        alias="prescribedMedications",
        description="Patient's prescribed medications.",
    )
    allergies: Optional[list[str]] = Field(None, description="Patient's allergies.")
    immunizations: Optional[list[str]] = Field(
        None, alias="immunizations", description="Patient's immunizations."
    )
    advisory_notes: Optional[list[str]] = Field(
        None, alias="advisoryNotes", description="Patient's advisory notes."
    )
    care_plan: Optional[list[str]] = Field(
        None, alias="carePlan", description="Patient's care plan."
    )
    follow_up: Optional[list[str]] = Field(
        None, alias="followUp", description="Patient's follow-up plan."
    )


class OPConsultationSections(CommonHealthInformationDTO):
    pass


class DischargeSummarySections(CommonHealthInformationDTO):
    investigations: InvestigationItem = Field(
        ..., description="Patient's investigations."
    )


class PrescriptionSections(BaseModel):
    prescribed_medications: list[str] = Field(
        ...,
        alias="prescribedMedications",
        description="Patient's prescribed medications.",
    )


class WellnessRecordSections(BaseModel):
    patient_details: PatientDetails = Field(
        ..., alias="Patient Details", description="Patient's information."
    )
    doctor_details: list[DoctorDetails] = Field(
        ..., alias="Doctor Details", description="Doctor's information."
    )
    vital_signs: Optional[dict[str, VitalSign]] = Field(None, alias="vitalSigns")
    body_measurements: Optional[dict[str, VitalSign]] = Field(
        None, alias="bodyMeasurements"
    )
    physical_activities: Optional[dict[str, VitalSign]] = Field(
        None, alias="physicalActivities"
    )
    women_health: Optional[dict[str, VitalSign]] = Field(None, alias="womenHealth")
    life_style: Optional[dict[str, VitalSign]] = Field(None, alias="lifeStyle")
    others: Optional[dict[str, VitalSign]] = Field(None, alias="others")


class ImmunizationRecordSections(BaseModel):
    patient_details: PatientDetails = Field(
        ..., alias="Patient Details", description="Patient's information."
    )
    doctor_details: list[DoctorDetails] = Field(
        ..., alias="Doctor Details", description="Doctor's information."
    )
    immunizations: list[str] = Field(..., description="Patient's immunizations.")


class DiagnosticReportSections(BaseModel):
    patient_details: PatientDetails = Field(
        ..., alias="Patient Details", description="Patient's information."
    )
    doctor_details: list[DoctorDetails] = Field(
        ..., alias="Doctor Details", description="Doctor's information."
    )
    lab_reports: LabReportItem = Field(..., description="Patient's lab reports.")


class OPConsultationDTO(BaseModel):
    case_sheets: Optional[list[str]] = Field(None, description="Patient's case_sheets.", alias="caseSheets")
    payload: Optional[OPConsultationSections] = Field(None, alias="payload", description="Patient's raw data.")

class DischargeSummaryDTO(BaseModel):
    case_sheets: Optional[list[str]] = Field(None, description="Patient's case_sheets.", alias="caseSheets")
    payload: Optional[DischargeSummarySections] = Field(None, alias="payload", description="Patient's raw data.")

class PrescriptionRecordDTO(BaseModel):
    case_sheets: Optional[list[str]] = Field(None, description="Patient's case_sheets.", alias="caseSheets")
    payload: Optional[PrescriptionSections] = Field(None, description="Patient's payload.")

class WellnessRecordDTO(BaseModel):
    case_sheets: Optional[list[str]] = Field(None, description="Patient's case_sheets.", alias="caseSheets")
    payload: Optional[WellnessRecordSections] = Field(None, description="Patient's payload.")

class ImmunizationRecordDTO(BaseModel):
    case_sheets: Optional[list[str]] = Field(None, description="Patient's case_sheets.", alias="caseSheets")
    payload: Optional[ImmunizationRecordSections] = Field(None, description="Patient's payload.")

class DiagnosticReportDTO(BaseModel):
    case_sheets: Optional[list[str]] = Field(None, description="Patient's case_sheets.", alias="caseSheets")
    payload: Optional[DiagnosticReportSections] = Field(None, description="Patient's payload.")

class HealthDocumentRecordDTO(BaseModel):
    case_sheets: Optional[list[str]] = Field(None, description="Patient's case_sheets.")


HealthInformationDTOUnion = Union[
    OPConsultationDTO,
    DischargeSummaryDTO,
    PrescriptionRecordDTO,
    WellnessRecordDTO,
    ImmunizationRecordDTO,
    DiagnosticReportDTO,
    HealthDocumentRecordDTO,
]


class EncounterRequestDTO(BaseModel):
    case_type: CaseType = Field(..., alias="caseType", description="The type of health information case")  # Changed from HealthInformationTypes
    lab_reports : Optional[list[str]]=Field(None, alias="labReports", description="The document references")
    dto: HealthInformationDTOUnion = Field(..., alias="dto", description="The health information data")

    @model_validator(mode="before")
    @classmethod
    def validate_case_type_and_data(cls, values: Any):
        if isinstance(values, dict):
            case_type = values.get("case_type") or values.get("caseType")
            data = values.get("dto")

            if case_type and data:
                # Mapping of case types to their corresponding DTO classes
                health_information_dto_mapping = {
                    CaseType.OP_CONSULTATION.value: OPConsultationDTO,
                    CaseType.DISCHARGE_SUMMARY.value: DischargeSummaryDTO,
                    CaseType.Prescription.value: PrescriptionRecordDTO,
                    CaseType.WellnessRecord.value: WellnessRecordDTO,
                    CaseType.ImmunizationRecord.value: ImmunizationRecordDTO,
                    CaseType.DiagnosticReport.value: DiagnosticReportDTO,
                }

                expected_dto_class = health_information_dto_mapping.get(case_type)
                if expected_dto_class:
                    # Convert the data to the expected DTO class
                    try:
                        values["dto"] = expected_dto_class(**data)
                    except Exception as e:
                        raise ValueError(
                            f"Invalid data for {expected_dto_class.__name__}: {str(e)}"
                        )

            return values
