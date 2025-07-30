import logging
import os

from carestack.base.base_service import BaseService
from carestack.base.base_types import ClientConfig
from carestack.base.errors import EhrApiError
from carestack.common.enums import CREATE_ABHA_ENDPOINTS, AbhaSteps
from carestack.abha.abha_dto import (
    AbhaAddressSuggestionsResponse,
    CreateAbhaAddressRequest,
    CreateAbhaAddressResponse,
    GenerateAadhaarOtpRequest,
    UpdateMobileNumberRequest,
    VerifyMobileOtpRequest,
    VerifyMobileOtpResponse,
    VerifyOtpResponse,
    enrollWithAadhaar,
    enrollWithAadhaarResponse,
)
from carestack.abha.encrypt_data import encrypt_data_for_abha


class ABHAService(BaseService):
    def __init__(self, config: ClientConfig):
        super().__init__(config)
        self.logger = logging.getLogger(__name__)
        self.abha_public_key = os.getenv("ABHA_PUBLIC_KEY").replace("\\n", "\n")
        if not self.abha_public_key:
            self.logger.warning(
                "ABHA_PUBLIC_KEY environment variable is not set. Encryption will fail."
            )

    async def generate_aadhaar_otp(
        self, request_body: GenerateAadhaarOtpRequest
    ) -> VerifyOtpResponse:
        """
        Generates an OTP for Aadhaar verification by encrypting the Aadhaar number
        and sending it to the ABHA API.

        :param request: A GenerateAadhaarOtpRequest object containing the Aadhaar number.
        :return: A GenerateAadhaarOtpResponse object with the transaction ID.
        :raises ValueError: If the ABHA_PUBLIC_KEY is not configured.
        """

        try:
            encrypted_aadhaar = await encrypt_data_for_abha(
                data_to_encrypt=request_body.aadhaar,
                certificate_pem=self.abha_public_key,
            )

            payload = {"aadhaar": encrypted_aadhaar}

            response = await self.post(
                CREATE_ABHA_ENDPOINTS.GENERATE_AADHAAR_OTP,
                payload,
                response_model=VerifyOtpResponse,
            )
            return response
        except EhrApiError as e:
           raise e
        except Exception as e:
            self.logger.error(
                "An unexpected error occured while generating aadhaar based otp",
                exc_info=True,
            )
            raise EhrApiError(
                "An unexpected error occured while generating aadhaar based otp"
            ) from e
        
    async def enroll_with_aadhaar(
        self, request_body: enrollWithAadhaar
    ) -> enrollWithAadhaarResponse:
        try:
            encrypted_otp = await encrypt_data_for_abha(
                data_to_encrypt=request_body.otp,
                certificate_pem=self.abha_public_key,
            )

            payload = {
                "otp": encrypted_otp,
                "txnId": request_body.txnId,
                "mobile": request_body.mobile,
            }

            response = await self.post(
                CREATE_ABHA_ENDPOINTS.ENROLL_WITH_AADHAAR,
                payload,
                response_model=enrollWithAadhaarResponse,
            )
            return response
        except EhrApiError as e:
            raise e
        except Exception as e:
            self.logger.error(
                "An unexpected error occured while enrolling with aadhaar",
                exc_info=True,
            )
            raise EhrApiError(
                "An unexpected error occured while enrolling with aadhaar"
            ) from e

    async def generate_mobile_otp(
        self, request_body: UpdateMobileNumberRequest
    ) -> VerifyOtpResponse:
        try:
            encrypted_mobile = await encrypt_data_for_abha(
                data_to_encrypt=request_body.updateValue,
                certificate_pem=self.abha_public_key
            )
            payload = {"updateValue": encrypted_mobile, "txnId": request_body.txnId}

            response = await self.post(
                CREATE_ABHA_ENDPOINTS.GENERATE_MOBILE_OTP,
                payload,
                response_model=VerifyOtpResponse,
            )
            return response
        except EhrApiError as e:
            raise e
        except Exception as e:
            self.logger.error(
                "An unexpected error occured while generating mobile otp",
                exc_info=True,
            )
            raise EhrApiError(
                "An unexpected error occured while generating mobile otp"
            ) from e
    
    async def verify_mobile_otp(
        self, request_body: VerifyMobileOtpRequest
    ) -> VerifyMobileOtpResponse:
        try:
            encrypted_otp = await encrypt_data_for_abha(
                data_to_encrypt=request_body.otp,
                certificate_pem=self.abha_public_key
            )
            payload = {"otp": encrypted_otp, "txnId": request_body.txnId}

            response = await self.post(
                CREATE_ABHA_ENDPOINTS.VERIFY_MOBILE_OTP,
                payload,
                response_model=VerifyMobileOtpResponse,
            )
            return response
        except EhrApiError as e:
            raise e
        except Exception as e:
            self.logger.error(
                "An unexpected error occured while verifying mobile otp",
                exc_info=True,
            )
            raise EhrApiError(
                "An unexpected error occured while verifying mobile otp"
            ) from e
        
    async def abha_address_suggestion(
        self, txnId: str ) -> AbhaAddressSuggestionsResponse:
        try:
            response = await self.get(
                CREATE_ABHA_ENDPOINTS.ABHA_ADDRESS_SUGGESTION,
                query_params={"txnId": txnId},
                response_model=AbhaAddressSuggestionsResponse,
            )
            return response
        except EhrApiError as e:
            raise e
        except Exception as e:
            self.logger.error(
                "An unexpected error occured while getting abha address suggestions",
                exc_info=True,
            )
            raise EhrApiError("An unexpected error occured while getting abha address suggestions") from e
        
    async def create_abha_address(
        self, request_body: CreateAbhaAddressRequest
    ) -> CreateAbhaAddressResponse:
        try:
            payload = {"abhaAddress": request_body.abhaAddress, "txnId": request_body.txnId}

            response = await self.post(
                CREATE_ABHA_ENDPOINTS.CREATE_ABHA,
                payload,
                response_model=CreateAbhaAddressResponse,
            )
            return response
        except EhrApiError as e:
            raise e
        except Exception as e:
            self.logger.error(
                "An unexpected error occured while creating abha address",
                exc_info=True,
                )
            raise EhrApiError("An unexpected error occured while creating abha address") from e
        
    async def create_abha_flow(self, step: AbhaSteps, payload: dict):
        try:
            if step == AbhaSteps.GENERATE_AADHAAR_OTP:
                request_body = GenerateAadhaarOtpRequest(**payload)
                return await self.generate_aadhaar_otp(request_body)
            
            elif step == AbhaSteps.ENROLL_WITH_AADHAAR:
                request_body = enrollWithAadhaar(**payload)
                return await self.enroll_with_aadhaar(request_body)
            
            elif step == AbhaSteps.GENERATE_MOBILE_OTP:
                request_body = UpdateMobileNumberRequest(**payload)
                return await self.generate_mobile_otp(request_body)
            
            elif step == AbhaSteps.VERIFY_MOBILE_OTP:
                request_body = VerifyMobileOtpRequest(**payload)
                return await self.verify_mobile_otp(request_body)
            
            # elif step == AbhaSteps.ABHA_ADDRESS_SUGGESTION:
            #     return await self.abha_address_suggestion()
            
            elif step == AbhaSteps.CREATE_ABHA_ADDRESS:
                request_body = CreateAbhaAddressRequest(**payload)
                return await self.create_abha_address(request_body)
            
            else:
                raise EhrApiError(f"Invalid step in ABHA creation flow: {step}")

        except Exception as e:
            self.logger.error(f"Error occurred in ABHA multistep flow for step {step}", exc_info=True)
            raise e