from pydantic import BaseModel
from typing import List, Optional


class Quantity(BaseModel):
    value: str
    unit: str
    code: str


class ReferenceRangeValue(BaseModel):
    value: str
    unit: str
    code: str


class ReferenceRange(BaseModel):
    low: ReferenceRangeValue
    high: ReferenceRangeValue


class PhysicalExaminationItem(BaseModel):
    code: str
    text: str
    status: str
    effectiveDateTime: str
    valueQuantity: Quantity
    referenceRange: ReferenceRange


class ConditionItem(BaseModel):
    code: str
    text: str
    clinicalStatus: str


class MedicalHistoryCondition(BaseModel):
    code: str
    text: str
    clinicalStatus: str


class MedicalHistoryProcedure(BaseModel):
    code: str
    text: str
    status: str
    procedure: dict
    complications: dict
    performedDate: str


class FamilyHistoryItem(BaseModel):
    status: str
    condition: dict
    relationship: dict
    gender: dict


class AllergyItem(BaseModel):
    status: str
    verificationStatus: Optional[str]
    recordedDate: Optional[str]
    reaction: Optional[str]


class MedicationStatementItem(BaseModel):
    code: str
    text: str
    status: str
    dateAsserted: str
    reasonCode: dict
    medication: dict


class AdvisoryNoteItem(BaseModel):
    category: dict
    note: dict


class ProcedureItem(BaseModel):
    status: str
    procedureText: Optional[str]
    complicationText: Optional[str]
    performedDate: Optional[str]


class CarePlanItem(BaseModel):
    title: str
    description: str
    status: str
    intent: str
    category: dict


class InvestigationAdviceItem(BaseModel):
    code: str
    text: str
    status: str
    intent: str


class FollowUpItem(BaseModel):
    serviceType: dict
    serviceCategory: dict
    appointmentType: dict
    appointmentReference: str


class OpConsultationResponseSchema(BaseModel):
    physicalExamination: List[PhysicalExaminationItem]
    medicalHistory: List[MedicalHistoryCondition | MedicalHistoryProcedure]
    familyHistory: List[FamilyHistoryItem]
    allergies: List[AllergyItem]
    medicationStatements: List[MedicationStatementItem]
    conditions: List[ConditionItem]
    investigations: List[dict]
    procedures: List[dict]
    medications: List[dict]
    carePlan: List[CarePlanItem]
    advisoryNotes: List[AdvisoryNoteItem]
    investigationAdvice: List[InvestigationAdviceItem]
    followUps: List[FollowUpItem]
    medicationRequests: List[dict]
    immunizations: List[dict]
    reports: List[dict]
    vitalSigns: List[dict]
    bodyMeasurements: List[dict]
    physicalActivities: List[dict]
    generalAssessments: List[dict]
    womenHealth: List[dict]
    lifeStyle: List[dict]
    others: List[dict]

    class Config:
        schema_extra = {
            "description": "Structured response schema for OP Consultation summary"
        }
