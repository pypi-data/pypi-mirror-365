import logging
from carestack.abha.abha_service import ABHAService
from carestack.base.base_types import ClientConfig
from carestack.base.errors import EhrApiError, ValidationError
from carestack.common.enums import AbhaSteps
from carestack.abha.abha_dto import (
    CreateAbhaAddressRequest,
    GenerateAadhaarOtpRequest,
    UpdateMobileNumberRequest,
    VerifyMobileOtpRequest,
    enrollWithAadhaar,
)


class CreateABHA:
    def __init__(self, config: ClientConfig):
        self.abha_service = ABHAService(config=config)
        self.logger = logging.getLogger(__name__)

    async def start_registration(self, aadhaar_number: str) -> dict:
        try:
            request_body = GenerateAadhaarOtpRequest(aadhaar=aadhaar_number)
            response = await self.abha_service.generate_aadhaar_otp(request_body)
            return {
                "message": "Aadhaar OTP generated. Please enroll with aadhaar by passing transactionId in next step",
                "data": response.model_dump(),
                "next_step": AbhaSteps.ENROLL_WITH_AADHAAR.value,
                "next_step_payload_hint": {
                    "description": "Provide the OTP received via SMS and the transaction ID.",
                    "required_fields": ["otp", "txnId"],
                    "source_of_data": {"txnId": "from current step's data.txnId"},
                },
            }
        except Exception as e:
            self.logger.error(f"Error starting ABHA registration: {e}", exc_info=True)
            raise e

    async def registration_flow(
        self, step: AbhaSteps, payload: dict
    ) -> dict:
        try:
            self.logger.info(f"Executing ABHA registration flow step: {step.value}")
            if step == AbhaSteps.ENROLL_WITH_AADHAAR:
                request_body = enrollWithAadhaar(**payload)
                response = await self.abha_service.enroll_with_aadhaar(request_body)

                if response.ABHAProfile.mobile == payload.get("mobile"):
                    return {
                        "message": "Aadhaar OTP verified. Now, generate mobile OTP.",
                        "data": response.model_dump(),
                        "next_step": AbhaSteps.GENERATE_MOBILE_OTP.value,
                        "next_step_payload_hint": {
                            "description": "Provide the mobile number for OTP generation"
                            "and the transaction ID from the current step's response data.",
                            "required_fields": ["mobile", "txnId"],
                            "source_of_data": {"txnId": "from current step's data.txnId"},
                        }
                    }
                else:
                    return {
                    "message": "Mobile OTP verified.",
                    "data": response.model_dump(),
                    "next_step": AbhaSteps.ABHA_ADDRESS_SUGGESTION.value,
                    "next_step_payload_hint": {
                        "description": "Provide the transaction ID from the current step's response data to select one abhaId name in list of options",
                        "required_fields": ["txnId"],
                        "source_of_data": {"txnId": "from current step's data.txnId"}
                    }
                }
            elif step == AbhaSteps.GENERATE_MOBILE_OTP:
                request_body = UpdateMobileNumberRequest(**payload)
                response = await self.abha_service.generate_mobile_otp(request_body)
                return {
                    "message": "Mobile OTP generated. Please verify it in the next step.",
                    "data": response.model_dump(),
                    "next_step": AbhaSteps.VERIFY_MOBILE_OTP.value,
                    "next_step_payload_hint": {
                        "description": "Provide the OTP value for verification.",
                        "required_fields": ["otp", "txnId"],
                        "source_of_data": {"txnId": "from current step's data.txnId"}
                    }
                }
            elif step == AbhaSteps.VERIFY_MOBILE_OTP:
                request_body = VerifyMobileOtpRequest(**payload)
                response = await self.abha_service.verify_mobile_otp(request_body)
                return {
                    "message": "Mobile OTP verified.",
                    "data": response.model_dump(),
                    "next_step": AbhaSteps.ABHA_ADDRESS_SUGGESTION.value,
                    "next_step_payload_hint": {
                        "description": "Provide the transaction ID from the current step's response data to select one abhaId name in list of options",
                        "required_fields": ["txnId"],
                        "source_of_data": {"txnId": "from current step's data.txnId"}
                    }
                }
            elif step == AbhaSteps.ABHA_ADDRESS_SUGGESTION:
                response = await self.abha_service.abha_address_suggestion(payload["txnId"])
                return{
                    "message": "ABHA ID suggestions retrieved. Proceed to create the ABHA ID.",
                    "data": response.model_dump(),
                    "next_step": AbhaSteps.CREATE_ABHA_ADDRESS.value,
                    "next_step_payload_hint": {
                        "description": "Provide a chosen abhaAddress and txnId from current step.",
                        "required_fields": [
                            "abhaAddress",
                            "txnId"],
                        "source_of_data": { "abhaAddress": "user choice from current step's data.suggestions",
                            "txnId": "from previous steps"
                        },
                    },
                }
            
            elif step == AbhaSteps.CREATE_ABHA_ADDRESS:
                request_body = CreateAbhaAddressRequest(**payload)
                response = await self.abha_service.create_abha_address(request_body)
                return{
                    "message": "ABHA ID created successfully. Registration complete.",
                    "data": response.model_dump(),
                    "next_step": None,
                }
            
            else:
                raise Exception(f"Invalid or out-of-sequence step in ABHA registration flow: {step}")
        except (EhrApiError, ValidationError) as e:
            self.logger.error(f"Error in the ABHA flow at step {step}: {e}", exc_info=True)
            raise e
        except Exception as e:
            self.logger.error(f"Error in ABHA flow at step {step}: {e}", exc_info=True)
            raise e