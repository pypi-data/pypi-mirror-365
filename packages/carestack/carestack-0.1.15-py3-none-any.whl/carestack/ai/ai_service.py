import logging
from typing import Any, Type, TypeVar

from pydantic import BaseModel, ValidationError

from carestack.base.base_service import BaseService
from carestack.base.base_types import ClientConfig
from carestack.base.errors import EhrApiError
from carestack.common.enums import AI_ENDPOINTS
from .ai_dto import (
    DischargeSummaryResponse,
    FhirBundleResponse,
    GenerateFhirBundleDto,
    ProcessDSDto,
)
from .ai_utils import AiUtilities

_DTO_T = TypeVar("_DTO_T", bound=BaseModel)


class AiService(BaseService):
    """
    Service for AI-related operations, such as generating discharge summaries.
    """

    def __init__(self, config: ClientConfig):
        super().__init__(config)
        self.logger = logging.getLogger(__name__)
        self.utilities = AiUtilities()

    async def _validate_data(
        self, dto_type: Type[_DTO_T], request_data: dict[str, Any]
    ) -> _DTO_T:
        """
        Validates dictionary data against a Pydantic model and returns the validated instance.
        """
        try:
            validated_instance: _DTO_T = dto_type(**request_data)
            return validated_instance
        except ValidationError as err:
            self.logger.error(
                f"Pydantic validation failed: {err.errors()}", exc_info=True
            )
            raise EhrApiError(f"Validation failed: {err.errors()}", 400) from err

    async def generate_discharge_summary(
        self, process_ds_data: dict[str, Any]
    ) -> DischargeSummaryResponse:
        """
        Generates a discharge summary based on the provided data.

        Args:
            process_ds_data: A dictionary containing data conforming to ProcessDSDto. Expected keys:
                             'case_type' (str), 'files' (Optional[List[str]]),
                             'encrypted_data' (Optional[str]), 'public_key' (Optional[str]).

        Returns:
            A string representing the generated discharge summary.

        Raises:
            EhrApiError: If validation fails, the API call returns an error, or an unexpected error occurs.
        """
        self.logger.info(
            f"Starting generation of discharge summary with data: {process_ds_data}"
        )
        try:
            process_ds_dto: ProcessDSDto = await self._validate_data(
                ProcessDSDto, process_ds_data
            )
            # Throw an error if there is no encrypted_data and no files are provided.
            if not process_ds_dto.encrypted_data and not process_ds_dto.files:
                raise ValueError("No files or encrypted data provided.")

            # If encrypted_data is provided, use it. Otherwise, encrypt the files.
            if process_ds_dto.encrypted_data:
                encrypted_data = process_ds_dto.encrypted_data
            else:
                payload_to_encrypt = {"files": process_ds_dto.files}
                encrypted_data = await self.utilities.encryption(
                    payload=payload_to_encrypt
                )

            payload = {
                "caseType": process_ds_dto.case_type,
                "encryptedData": encrypted_data,
                "publicKey": process_ds_dto.public_key,
            }

            if process_ds_dto.public_key:
                payload["publicKey"] = process_ds_dto.public_key

            discharge_summary: DischargeSummaryResponse = await self.post(
                AI_ENDPOINTS.GENERATE_DISCHARGE_SUMMARY,
                payload,
                response_model=DischargeSummaryResponse,
            )

            return discharge_summary

        except EhrApiError as e:
            self.logger.error(
                f"EHR API Error during discharge summary generation: {e.message}",
                exc_info=True,
            )
            raise
        except ValueError as e:
            self.logger.error(
                f"Validation error in discharge summary generation: {e}", exc_info=True
            )
            raise EhrApiError(str(e), 422) from e
        except Exception as error:
            error_message = str(error)
            self.logger.error(
                f"Unexpected error in generate_discharge_summary: {error_message}",
                exc_info=True,
            )
            raise EhrApiError(
                f"An unexpected error occurred while generating discharge summary: {error_message}",
                500,
            ) from error

    async def generate_fhir_bundle(
        self, generate_fhir_bundle_data: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Generates a FHIR bundle based on the provided data.

        Args:
            generate_fhir_bundle_data: A dictionary containing data conforming to GenerateFhirBundleDto.

        Returns:
            A dictionary representing the generated FHIR bundle.

        Raises:
            EhrApiError: If validation fails, the API call returns an error, or an unexpected error occurs.
        """
        self.logger.info(
            f"Starting generation of FHIR bundle with data: {generate_fhir_bundle_data}"
        )
        try:
            fhir_bundle_dto: GenerateFhirBundleDto = await self._validate_data(
                GenerateFhirBundleDto, generate_fhir_bundle_data
            )

            if (
                not fhir_bundle_dto.encrypted_data
                and not fhir_bundle_dto.extracted_data
            ):
                raise ValueError("No extracted data or encrypted data provided.")

            if fhir_bundle_dto.encrypted_data:
                encrypted_data = fhir_bundle_dto.encrypted_data
            else:
                encrypted_data = await self.utilities.encryption(
                    payload=fhir_bundle_dto.extracted_data or {}
                )

            payload = {
                "caseType": fhir_bundle_dto.case_type,
                "encryptedData": encrypted_data,
            }

            if fhir_bundle_dto.record_id:
                payload["recordId"] = fhir_bundle_dto.record_id

            if fhir_bundle_dto.public_key:
                payload["publicKey"] = fhir_bundle_dto.public_key

            fhir_bundle_response: FhirBundleResponse = await self.post(
                AI_ENDPOINTS.GENERATE_FHIR_BUNDLE,
                payload,
                response_model=FhirBundleResponse,
            )

            return fhir_bundle_response.root

        except EhrApiError as e:
            self.logger.error(
                f"EHR API Error during FHIR bundle generation: {e.message}",
                exc_info=True,
            )
            raise
        except ValueError as e:
            self.logger.error(
                f"Validation error in FHIR bundle generation: {e}", exc_info=True
            )
            raise EhrApiError(str(e), 422) from e
        except Exception as error:
            error_message = str(error)
            self.logger.error(
                f"Unexpected error in generate_fhir_bundle: {error_message}",
                exc_info=True,
            )
            raise EhrApiError(
                "An unexpected error occurred while generating FHIR bundle: "
                f"{error_message}",
                500,
            ) from error
