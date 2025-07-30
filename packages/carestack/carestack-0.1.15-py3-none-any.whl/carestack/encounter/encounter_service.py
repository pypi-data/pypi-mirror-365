import logging
from typing import Any, Optional, Union

from dotenv import load_dotenv

from carestack.ai.ai_dto import DischargeSummaryResponse, FhirBundleResponse
from carestack.ai.ai_utils import AiUtilities
from carestack.base.base_service import BaseService
from carestack.base.base_types import ClientConfig
from carestack.base.errors import EhrApiError
from carestack.common.enums import AI_ENDPOINTS
from carestack.encounter.dto.encounter_dto import EncounterRequestDTO

load_dotenv()


class Encounter(BaseService):
    """
    Service for managing encounters.
    """

    def __init__(self, config: ClientConfig):
        super().__init__(config)
        self.logger = logging.getLogger(__name__)
        self.utilities = AiUtilities()

    async def create(self, request_body: EncounterRequestDTO) -> dict[str, Any]:
        """
        Creates a FHIR bundle or discharge summary based on the case type and DTO content.
        """
        try:
            case_type = request_body.case_type.value
            dto = request_body.dto.model_dump(by_alias=True, exclude_none=True)

            self._validate_request_data(dto)

            if "payload" in dto and dto["payload"] is not None:
                return await self._generate_fhir_from_payload(
                    case_type, dto["payload"], request_body.lab_reports
                )

            if dto.get("caseSheets"):
                return await self._generate_fhir_from_files(
                    case_type, dto["caseSheets"], request_body.lab_reports
                )

            raise ValueError("Unexpected state in encounter creation.")

        except EhrApiError as e:
            self.logger.error(
                f"EHR API error in FHIR bundle generation: {e.message}", exc_info=True
            )
            raise
        except ValueError as e:
            self.logger.error(
                f"Validation error in FHIR bundle generation: {e}", exc_info=True
            )
            raise EhrApiError(str(e), 422) from e
        except Exception as error:
            self.logger.error(f"Unexpected error in generate_fhir_bundle: {error}", exc_info=True)
            raise EhrApiError(
                f"An unexpected error occurred while generating FHIR bundle: {error}", 500
            ) from error

    def _validate_request_data(self, dto: dict[str, Any]) -> None:
        """
        Validates that the request contains the necessary data.
        """
        has_case_sheets = bool(dto.get("caseSheets"))
        has_payload = "payload" in dto and dto["payload"] is not None

        if not has_case_sheets and not has_payload:
            raise ValueError("No case_sheets or payload provided for the encounter.")

    async def _generate_fhir_from_payload(
        self, case_type: str, payload: dict[str, Any], lab_reports: Optional[list[str]] = None
    ) -> dict[str, Any]:
        """
        Generates FHIR bundle from extracted payload and optional lab reports.
        """
        encryptedData = await self.utilities.encryption(payload=payload)

        request_payload = {
            "caseType": case_type,
            "encryptedData": encryptedData,
        }
        
        # If lab reports are provided, encrypt and include them
        if lab_reports:
            encrypted_lab_reports_resp = await self.utilities.encryption(payload={"files": lab_reports})
            encrypted_lab_reports = self._normalize_encryption_response(encrypted_lab_reports_resp)
            request_payload["files"] = encrypted_lab_reports
            
        return await self.post(
            AI_ENDPOINTS.GENERATE_FHIR_BUNDLE,
            request_payload,
            response_model=dict[str, Any],
        )

    async def _generate_fhir_from_files(
        self,
        case_type: str,
        case_sheets: list[str],
        lab_reports: Optional[list[str]] = None
    ) -> dict[str, Any]:
        """
        Generates FHIR bundle from case sheets and optional lab reports.
        """
        try:
            # Step 1: Encrypt case sheets
            encrypted_case_sheets_resp = await self.utilities.encryption(payload={"files": case_sheets})
            encrypted_case_sheets = self._normalize_encryption_response(encrypted_case_sheets_resp)

            # Step 2: Generate discharge summary
            discharge_response = await self._generate_discharge_summary(
                case_type, encrypted_case_sheets_resp
            )

            # Step 3: Encrypt lab reports if provided
            encrypted_lab_reports = []
            if lab_reports:
                encrypted_lab_reports_resp = await self.utilities.encryption(payload={"files": lab_reports})
                encrypted_lab_reports = self._normalize_encryption_response(encrypted_lab_reports_resp)

            # Step 4: Generate FHIR bundle
            all_encrypted_files = encrypted_case_sheets + encrypted_lab_reports
            return await self._generate_fhir_bundle(
                case_type, discharge_response.extracted_data, all_encrypted_files
            )

        except Exception as e:
            self.logger.error(
                f"Error generating FHIR from files: {str(e)}", exc_info=True
            )
            raise

    def _normalize_encryption_response(
        self, response: Union[dict[str, Any], list[str], str]
    ) -> list[str]:
        """
        Normalizes encryption response to a consistent list format.
        
        Args:
            response: The encryption response which can be dict, list, or string
            
        Returns:
            list[str]: Normalized list of encrypted files
        """
        if isinstance(response, dict):
            return response.get("files", [])
        elif isinstance(response, list):
            return response
        elif isinstance(response, str):
            return [response]
        else:
            self.logger.warning(f"Unexpected encryption response type: {type(response)}")
            return []

    async def _generate_discharge_summary(
        self, case_type: str, encrypted_data: Any
    ) -> DischargeSummaryResponse:
        """
        Generates discharge summary from encrypted case sheets.
        
        Args:
            case_type: The type of case
            encrypted_data: Raw encrypted data response
            
        Returns:
            DischargeSummaryResponse: The discharge summary response
        """
        discharge_payload = {
            "caseType": case_type,
            "encryptedData": encrypted_data,
        }

        return await self.post(
            AI_ENDPOINTS.GENERATE_DISCHARGE_SUMMARY,
            discharge_payload,
            response_model=DischargeSummaryResponse,
        )

    async def _generate_fhir_bundle(
        self, case_type: str, extracted_data: Any, encrypted_files: list[str]
    ) -> dict[str, Any]:
        """
        Generates FHIR bundle from extracted data and encrypted files.
        
        Args:
            case_type: The type of case
            extracted_data: Extracted data from discharge summary
            encrypted_files: List of encrypted files
            
        Returns:
            dict[str, Any]: The FHIR bundle response
        """
        fhir_payload = {
            "caseType": case_type,
            "extractedData": extracted_data,
            "files": encrypted_files,
        }

        fhir_response = await self.post(
            AI_ENDPOINTS.GENERATE_FHIR_BUNDLE,
            fhir_payload,
            response_model=FhirBundleResponse,
        )

        return fhir_response.root