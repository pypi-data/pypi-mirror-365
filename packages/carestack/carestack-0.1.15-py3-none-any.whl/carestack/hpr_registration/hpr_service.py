from pydantic import BaseModel, ValidationError
from carestack.common.enums import HPR_API_ENDPOINTS
from carestack.hpr_registration.hpr_dto import (
    CheckAccountExistRequestSchema,
    CreateHprIdWithPreVerifiedRequestBody,
    CreateHprIdWithPreVerifiedResponseBody,
    DemographicAuthViaMobileRequestSchema,
    DemographicAuthViaMobileResponseSchema,
    GenerateAadhaarOtpRequestSchema,
    GenerateAadhaarOtpResponseSchema,
    GenerateMobileOtpRequestSchema,
    HpIdSuggestionRequestSchema,
    HprIdSuggestionResponse,
    HprAccountResponse,
    MobileOtpResponseSchema,
    NonHprAccountResponse,
    VerifyAadhaarOtpRequestSchema,
    VerifyAadhaarOtpResponseSchema,
    VerifyMobileOtpRequestSchema,
    HprIdSuggestionResponse,
)
from carestack.base.base_service import BaseService
from carestack.base.base_types import ClientConfig
from carestack.base.errors import EhrApiError
import logging
from typing import Any, Type, TypeVar, Union

T = TypeVar("T")


class HPRService(BaseService):
    """
    ProfessionalService for handling HPR registration-related operations.

    This service provides methods for interacting with the HPR registration API,
    including Aadhaar OTP generation and verification, mobile OTP handling, etc.

    Args:
        config (ClientConfig): Configuration object containing API credentials and settings.
    """

    def __init__(self, config: ClientConfig):
        super().__init__(config)
        self.logger = logging.getLogger(__name__)

    async def validate_data(
        self, dto_type: Type[BaseModel], request_data: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Validates request data using Pydantic models.

        Args:
            dto_type: Pydantic model for validation.
            request_data (Dict[str, Any]): Data to be validated.

        Returns:
            Dict[str, Any]: Validated data as a dictionary.

        Raises:
            EhrApiError: If validation fails.
        """
        try:
            validated_data = dto_type(**request_data)
            return validated_data.model_dump(by_alias=True)
        except ValidationError as err:
            self.logger.exception("Validation failed with pydantic error.")
            raise EhrApiError(f"Validation failed: {err}", 400) from err

    async def generate_aadhaar_otp(
        self, request_data: dict[str, Any]
    ) -> GenerateAadhaarOtpResponseSchema:
        """
        Generates Aadhaar OTP.

        Args:
            request_data (Dict[str, Any]): Request data containing aadhaar number.

        Returns:
            GenerateAadhaarOtpResponseSchema: Response with txnId and mobileNumber.

        Raises:
            EhrApiError: If the request fails or validation fails.
        """
        if not request_data.get("aadhaar"):
            raise EhrApiError("Aadhaar number is required", 400)

        validated_data = await self.validate_data(
            GenerateAadhaarOtpRequestSchema, request_data
        )
        try:
            response = await self.post(
                HPR_API_ENDPOINTS.GENERATE_AADHAAR_OTP,
                validated_data,
                GenerateAadhaarOtpResponseSchema,
            )
            return response
        except EhrApiError as e:
            raise e
        except Exception as e:
            self.logger.error(
                "An unexpected error occured while generating Aadhaar OTP",
                exc_info=True,
            )
            raise EhrApiError(
                "An unexpected error occured while generating Aadhaar OTP"
            ) from e

    async def verify_aadhaar_otp(
        self, request_data: dict[str, Any]
    ) -> VerifyAadhaarOtpResponseSchema:
        """
        verifies Aadhaar OTP.

        Args:
            request_data (Dict[str, Any]): Request data containing otp and domain name,idtype,restriction,txnid.

        Returns:
            VerifyAadhaarOtpResponseSchema: Response with txnId,gender,mobileNumber,email,etc.

        Raises:
            EhrApiError: If the request fails or validation fails.
        """
        if not request_data.get("otp"):
            raise EhrApiError("OTP is required", 400)
        validated_data = await self.validate_data(
            VerifyAadhaarOtpRequestSchema, request_data
        )
        try:
            response = await self.post(
                HPR_API_ENDPOINTS.VERIFY_AADHAAR_OTP,
                validated_data,
                VerifyAadhaarOtpResponseSchema,
            )
            return response
        except EhrApiError as e:
            raise e
        except Exception as e:
            self.logger.error(
                "An unexpected error occured while verifying Aadhaar OTP", exc_info=True
            )
            raise EhrApiError(
                "An unexpected error occured while verifying Aadhaar OTP"
            ) from e

    async def check_account_exist(
        self, request_data: dict[str, Any]
    ) -> Union[HprAccountResponse, NonHprAccountResponse]:
        """
        Checks if an account exists.

        Args:
            request_data (Dict[str, Any]): Request data containing txnid, preverifiedcheck.

        Returns:
            Union[HprAccountResponse, NonHprAccountResponse]: Response with account details.

        Raises:
            EhrApiError: If the request fails or validation fails.
        """
        if not request_data.get("txnId"):
            raise EhrApiError("Transaction ID is required", 400)

        validated_data = await self.validate_data(
            CheckAccountExistRequestSchema, request_data
        )

        try:
            # Get the raw response as a dictionary first by not passing a response_model
            response_data = await self.post(
                HPR_API_ENDPOINTS.CHECK_ACCOUNT_EXIST,
                validated_data,
                response_model=dict,
            )

            if not isinstance(response_data, dict):
                raise EhrApiError("Invalid response format from API", 500)

            # Check if hprIdNumber is present and not empty, then parse with the correct model
            if response_data.get("hprIdNumber"):
                return HprAccountResponse(**response_data)
            else:
                return NonHprAccountResponse(**response_data)
        except ValidationError as e:
            self.logger.error(
                "Pydantic validation failed for account existence check: %s", e
            )
            raise EhrApiError(f"Response validation failed: {e}", 400) from e
        except EhrApiError as e:
            raise e
        except Exception as e:
            self.logger.error(
                "An unexpected error occurred while checking account existence",
                exc_info=True,
            )
            raise EhrApiError(
                f"An unexpected error occurred while checking account existence: {e}"
            ) from e

    async def demographic_auth_via_mobile(
        self, request_data: dict[str, Any]
    ) -> DemographicAuthViaMobileResponseSchema:
        """
        verifies demographic auth via mobile.

        Args:
            request_data (Dict[str, Any]): Request data containing txnid,mobile number.

        Returns:
            DemographicAuthViaMobileResponseSchema: Response with verified.

        Raises:
            EhrApiError: If the request fails or validation fails.
        """
        if not request_data.get("mobileNumber"):
            raise EhrApiError("Mobile number is required", 400)
        validated_data = await self.validate_data(
            DemographicAuthViaMobileRequestSchema, request_data
        )
        try:
            response = await self.post(
                HPR_API_ENDPOINTS.DEMOGRAPHIC_AUTH_MOBILE,
                validated_data,
                DemographicAuthViaMobileResponseSchema,
            )
            return response
        except EhrApiError as e:
            raise e
        except Exception as e:
            self.logger.error(
                "An unexpected error occured while verifying demographic auth via mobile",
                exc_info=True,
            )
            raise EhrApiError(
                "An unexpected error occured while verifying demographic auth via mobile"
            ) from e

    async def generate_mobile_otp(
        self, request_data: dict[str, Any]
    ) -> MobileOtpResponseSchema:
        """
        generates mobile OTP.

        Args:
            request_data (Dict[str, Any]): Request data containing txnid,mobile.

        Returns:
            MobileOtpResponseSchema: Response with txnid.

        Raises:
            EhrApiError: If the request fails or validation fails.
        """
        if not request_data.get("mobile"):
            raise EhrApiError("Mobile number is required", 400)
        validated_data = await self.validate_data(
            GenerateMobileOtpRequestSchema, request_data
        )
        try:
            response = await self.post(
                HPR_API_ENDPOINTS.GENERATE_MOBILE_OTP,
                validated_data,
                MobileOtpResponseSchema,
            )
            return response
        except EhrApiError as e:
            raise e
        except Exception as e:
            self.logger.error(
                "An unexpected error occured while generating mobile OTP", exc_info=True
            )
            raise EhrApiError(
                "An unexpected error occured while generating mobile OTP"
            ) from e

    async def verify_mobile_otp(
        self, request_data: dict[str, Any]
    ) -> MobileOtpResponseSchema:
        """
        verifies mobile OTP.

        Args:
            request_data (Dict[str, Any]): Request data containing txnid,otp.

        Returns:
            MobileOtpResponseSchema: Response with txnid.

        Raises:
            EhrApiError: If the request fails or validation fails.
        """
        if not request_data.get("otp"):
            raise EhrApiError("OTP is required", 400)
        validated_data = await self.validate_data(
            VerifyMobileOtpRequestSchema, request_data
        )
        try:
            response = await self.post(
                HPR_API_ENDPOINTS.VERIFY_MOBILE_OTP,
                validated_data,
                MobileOtpResponseSchema,
            )
            return response
        except EhrApiError as e:
            raise e
        except Exception as e:
            self.logger.error(
                "An unexpected error occured while verifying mobile OTP", exc_info=True
            )
            raise EhrApiError(
                "An unexpected error occured while verifying mobile OTP"
            ) from e

    async def get_hpr_suggestion(self, request_data: dict[str, Any]) -> list[str]:
        """
        Gets HPR ID suggestions.

        Args:
            request_data (Dict[str, Any]): Request data containing txnid.

        Returns:
            list[str]: A list of HPR ID suggestions.

        Raises:
            EhrApiError: If the request fails or validation fails.
        """
        if not request_data.get("txnId"):
            raise EhrApiError("Transaction ID is required", 400)

        validated_data = await self.validate_data(
            HpIdSuggestionRequestSchema, request_data
        )

        try:
            response: HprIdSuggestionResponse = await self.post(
                HPR_API_ENDPOINTS.GET_HPR_SUGGESTION,
                validated_data,
                HprIdSuggestionResponse,
            )

            # Pydantic's RootModel wraps the list. We return the underlying list.
            return response.root

        except EhrApiError as e:
            raise e
        except Exception as e:
            self.logger.error(
                "An unexpected error occurred while getting HPR suggestions",
                exc_info=True,
            )
            raise EhrApiError(
                "An unexpected error occurred while getting HPR suggestions"
            ) from e

    async def create_hpr_id_with_preverified(
        self, request_data: dict[str, Any]
    ) -> CreateHprIdWithPreVerifiedResponseBody:
        """
        create hpr id with preverified data.

        Args:
            request_data (Dict[str, Any]): Request data containing all the details.

        Returns:
            CreateHprIdWithPreVerifiedResponseBody: Response with all the details.

        Raises:
            EhrApiError: If the request fails or validation fails.
        """
        if not request_data:
            raise EhrApiError("Request data is required", 400)
        validated_data = await self.validate_data(
            CreateHprIdWithPreVerifiedRequestBody, request_data
        )
        try:
            response = await self.post(
                HPR_API_ENDPOINTS.CREATE_HPR_ID_WITH_PREVERIFIED,
                validated_data,
                CreateHprIdWithPreVerifiedResponseBody,
            )
            return response
        except EhrApiError as e:
            raise e
        except Exception as e:
            self.logger.error(
                "An unexpected error occured while creating hpr id with preverified data",
                exc_info=True,
            )
            raise EhrApiError(
                "An unexpected error occured while creating hpr id with preverified data"
            ) from e
