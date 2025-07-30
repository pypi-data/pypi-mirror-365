import logging
import re
from typing import Any, Optional
from uuid import UUID
from pydantic import BaseModel, RootModel, ValidationError

from carestack.base.base_service import BaseService
from carestack.base.base_types import ClientConfig
from carestack.base.errors import EhrApiError
from carestack.common.enums import DOCUMENT_LINKING_ENDPOINTS, HealthInformationTypes

from carestack.document_linking.dto.create_care_context_dto import (
    CreateCareContextDTO,
    CreateCareContextResponse,
)
from carestack.document_linking.dto.health_document_linking_dto import (
    HealthDocumentLinkingDTO,
)
from carestack.document_linking.dto.link_care_context_dto import (
    LinkCareContextDTO,
)
from carestack.document_linking.dto.update_visit_records_dto import (
    UpdateVisitRecordsDTO,
    UpdateVisitRecordsResponse,
)
from carestack.document_linking.schema import (
    map_to_consultation_dto,
    map_to_create_care_context_dto,
)

class TransactionState:
    """Represents the state of a document linking transaction."""

    def __init__(self) -> None:
        self.care_context_reference: Optional[str] = None
        self.request_id: Optional[str] = None
        self.appointment_created: bool = False
        self.care_context_created: bool = False
        self.visit_records_updated: bool = False
        self.care_context_linked: bool = False

    def __str__(self) -> str:
        return (
            f"care_context_reference={self._mask_data(self.care_context_reference)}, request_id={self._mask_data(self.request_id)}, "
            f"appointment_created={self.appointment_created}, care_context_created={self.care_context_created}, "
            f"visit_records_updated={self.visit_records_updated}, care_context_linked={self.care_context_linked})"
        )

    def _mask_data(self, data: Optional[str]) -> str:
        """Masks sensitive data."""
        if data is None:
            return "null"
        if len(data) <= 4:
            return "*" * len(data)
        return data[:2] + "*" * (len(data) - 4) + data[-2:]


class GenericDictResponseSchema(RootModel[dict[str, Any]]):
    pass


class DocumentLinking(BaseService):
    """Service responsible for linking health documents through a multi-step process."""

    def __init__(self, config: ClientConfig) -> None:
        super().__init__(config)
        self.logger = logging.getLogger(__name__)

    async def _validate_data(self, data: Any) -> None:
        """Validates the input data against the given DTO type."""
        if data is None:
            raise ValueError("Input data cannot be null")
        try:
            if isinstance(data, HealthDocumentLinkingDTO):
                self._validate_health_document_linking_dto(data)
            elif isinstance(data, CreateCareContextDTO):
                self._validate_create_care_context_dto(data)
            elif isinstance(data, UpdateVisitRecordsDTO):
                self._validate_consultation_dto(data)
            elif isinstance(data, LinkCareContextDTO):
                self._validate_link_care_context_dto(data)
            else:
                raise TypeError(f"Unsupported DTO type: {type(data)}")
        except ValidationError as e:
            self.logger.exception(f"Validation error: {e}")
            raise ValueError(f"Validation failed: {e}") from e

    def _validate_health_document_linking_dto(
        self, dto: HealthDocumentLinkingDTO
    ) -> None:
        self._validate_not_empty(dto.patient_reference, "patientReference")
        self._validate_not_empty(dto.practitioner_reference, "practitionerReference")

        if not (
            len(dto.patient_reference) in (32, 36)
            and dto.patient_reference.replace("-", "").isalnum()
        ):
            raise ValueError(
                "Patient reference must be a valid 32 or 36 character UUID"
            )

        self._validate_not_empty(
            str(dto.appointment_start_date), "appointmentStartDate"
        )
        self._validate_not_empty(str(dto.appointment_end_date), "appointmentEndDate")
        if dto.appointment_priority is not None and not dto.appointment_priority.value:
            raise ValueError("Appointment priority cannot be empty")
        self._validate_not_empty(dto.organization_id, "organizationID")
        self._validate_not_empty(dto.mobile_number, "mobileNumber")

    def _validate_create_care_context_dto(self, dto: CreateCareContextDTO) -> None:
        self._validate_not_empty(str(dto.patient_reference), "patientReference")
        self._validate_not_empty(
            str(dto.practitioner_reference), "practitionerReference"
        )
        self._validate_not_empty(dto.appointment_reference, "appointmentReference")
        self._validate_not_empty(dto.appointment_date, "appointmentDate")

        uuid_pattern = r"^[a-fA-F0-9-]{36}$"
        for value, field in [
            (dto.patient_reference, "patientReference"),
            (dto.practitioner_reference, "practitionerReference"),
            (dto.appointment_reference, "appointmentReference"),
        ]:
            if not re.fullmatch(uuid_pattern, str(value)):
                raise ValueError(f"{field} must be a valid 36-character UUID")

        if dto.resend_otp is None:
            raise ValueError("Resend OTP flag is required")

    def _validate_consultation_dto(self, dto: UpdateVisitRecordsDTO) -> None:
        for field_value, field_name in [
            (dto.care_context_reference, "careContextReference"),
            (dto.patient_reference, "patientReference"),
            (dto.practitioner_reference, "practitionerReference"),
            (dto.appointment_reference, "appointmentReference"),
        ]:
            self._validate_not_empty(field_value, field_name)

    def _validate_link_care_context_dto(self, dto: LinkCareContextDTO) -> None:
        for field_value, field_name in [
            (dto.request_id, "requestId"),
            (dto.appointment_reference, "appointmentReference"),
            (dto.patient_address, "patientAddress"),
            (dto.patient_reference, "patientReference"),
            (dto.care_context_reference, "careContextReference"),
            (dto.auth_mode.value, "authMode"),
        ]:
            self._validate_not_empty(field_value, field_name)

    def _validate_not_empty(self, value: Optional[str], field_name: str) -> None:
        if not value:
            raise ValueError(f"{field_name} cannot be null or empty")

    def _serialize_model(self, model: BaseModel) -> dict[str, Any]:
        """Helper function to serialize a Pydantic model handling special types."""
        serialized: dict[str, Any] = {}
        for key, value in model.model_dump(
            by_alias=True, exclude_none=True, mode="json"
        ).items():
            if isinstance(value, UUID):
                serialized[key] = str(value)
            elif isinstance(value, HealthInformationTypes):
                serialized[key] = value.value
            elif isinstance(value, list):
                serialized[key] = [
                    self._serialize_model(item) if isinstance(item, BaseModel) else item
                    for item in value
                ]
            else:
                serialized[key] = value
        return serialized

    async def _create_care_context(
        self,
        health_document_linking_dto: HealthDocumentLinkingDTO,
    ) -> CreateCareContextDTO:
        """Creates care context data from health document linking information."""
        if health_document_linking_dto is None or not isinstance(
            health_document_linking_dto, HealthDocumentLinkingDTO
        ):
            raise ValueError("Input data cannot be null")
        care_context_data = map_to_create_care_context_dto(
            health_document_linking_dto,
        )
        await self._validate_data(care_context_data)
        return care_context_data

    async def _send_care_context_request(
        self, care_context_data: CreateCareContextDTO
    ) -> CreateCareContextResponse:
        """Sends care context creation request to the API."""
        data_to_send = self._serialize_model(care_context_data)
        response = await self.post(
            DOCUMENT_LINKING_ENDPOINTS.CREATE_CARE_CONTEXT,
            data_to_send,
            response_model=CreateCareContextResponse,
        )
        return response

    async def _update_visit_records(
        self,
        health_document_linking_dto: HealthDocumentLinkingDTO,
        care_context_response: CreateCareContextResponse,
    ) -> UpdateVisitRecordsResponse:
        """Updates visit records with consultation data."""
        
        consultation_data = map_to_consultation_dto(
            health_document_linking_dto,
            care_context_response.care_context_reference,
            care_context_response.request_id,
        )

        await self._validate_data(consultation_data)
        data_to_send = self._serialize_model(consultation_data)

        return await self.post(
            DOCUMENT_LINKING_ENDPOINTS.UPDATE_VISIT_RECORDS,
            data_to_send,
            response_model=UpdateVisitRecordsResponse,
        )


    # async def _link_care_context(
    #     self,
    #     health_document_linking_dto: HealthDocumentLinkingDTO,
    #     care_context_response: dict[str, Any],
    #     appointment_response: dict[str, Any],
    # ) -> bool:
    #     """Links the care context to the existing health document."""
    #     link_data = map_to_link_care_context_dto(
    #         health_document_linking_dto,
    #         care_context_response["careContextReference"],
    #         appointment_response["resourceId"],
    #         care_context_response["requestId"],
    #     )
    #     await self._validate_data(link_data)
    #     response = await self.post(
    #         DOCUMENT_LINKING_ENDPOINTS.LINK_CARE_CONTEXT,
    #         link_data.model_dump(by_alias=True, exclude_none=True, mode="json"),
    #     )
    #     self.logger.info(f"LinkCareContext API response: {response}")
    #     return bool(response)

    async def _link_health_document(
        self, health_document_linking_dto: HealthDocumentLinkingDTO
    ) -> UpdateVisitRecordsResponse:
        """
        Performs a complete health document linking process.
        """
        transaction_state = TransactionState()

        try:
            await self._validate_data(health_document_linking_dto)

            # Step 1: Create Care Context
            care_context_data = await self._create_care_context(
                health_document_linking_dto,
            )
            care_context_response = await self._send_care_context_request(
                care_context_data
            )

            transaction_state.care_context_reference = (
                care_context_response.care_context_reference
            )
            transaction_state.request_id = care_context_response.request_id
            transaction_state.care_context_created = True
            self.logger.info(
                f"Care context created with reference: {transaction_state.care_context_reference}"
            )
            response = UpdateVisitRecordsResponse(success=False)

            # Step 2: Update Visit Records (if available)
            if health_document_linking_dto.health_records:
                # here we get health_document_linking_dto which contains health_records,each health_record contains healthInformationType,based on this type we need to
                # create the specific encounter methods to create the target dto,so here we need to call
                response = await self._update_visit_records(
                    health_document_linking_dto,
                    care_context_response,
                )
                transaction_state.visit_records_updated = True
            else:
                self.logger.info(
                    "No health records provided. Skipping visit record update."
                )
            # Step 3: Optionally link care context if needed (commented out in original code)
            # link_success = await self._link_care_context(
            #     health_document_linking_dto,
            #     care_context_response,
            #     appointment_response,
            # )
            # if link_success:
            #     transaction_state.care_context_linked = True
            #     self.logger.info("Health document successfully linked.")

            return response

        except ValueError as e:
            raise ValueError(
                f"Transaction failed due to data validation error: {e}"
            ) from e
        except EhrApiError as e:
            raise EhrApiError(
                message=f"Transaction failed due to API error: {e.message}. Current state: {transaction_state}",
                status_code=e.status_code,
            ) from e
        except Exception as e:
            raise EhrApiError(
                message=f"Transaction failed due to unexpected error: {e}. Current state: {transaction_state}",
                status_code=500,
            ) from e
