import logging
from typing import Any

from pydantic import ValidationError

from carestack.base.base_types import ClientConfig
from carestack.base.errors import EhrApiError
from carestack.common.enums import HprRegistrationSteps
from carestack.hpr_registration.hpr_service import HPRService


class CreateHPR:
    """
    Orchestrates the multi-step HPR (Healthcare Professional Registry) registration process.

    This service provides a guided workflow for HPR registration, simplifying the
    developer experience by managing the sequence of API calls. It uses an instance
    of HPRService to perform the underlying API interactions.

    Args:
        hpr_service (HPRService): An instance of the HPRService for making API calls.
    """

    def __init__(self, config: ClientConfig):
        self.hpr_service = HPRService(config=config)
        self.logger = logging.getLogger(__name__)

    async def start_registration(self, aadhaar_number: str) -> dict[str, Any]:
        """Starts the registration by generating Aadhaar OTP."""
        try:
            payload = {"aadhaar": aadhaar_number}
            response = await self.hpr_service.generate_aadhaar_otp(payload)
            return {
                "message": "Aadhaar OTP generated. Please verify it in the registration flow method. Store the generated transactionId for further flow steps.",
                "data": response.model_dump(),
                "next_step": HprRegistrationSteps.VERIFY_AADHAAR_OTP.value,
                "next_step_payload_hint": {
                    "description": "Provide the OTP received via SMS and the transaction ID.",
                    "required_fields": ["otp", "txnId"],
                    "source_of_data": {"txnId": "from current step's data.txnId"},
                },
            }
        except Exception as e:
            self.logger.error(f"Error starting HPR registration: {e}", exc_info=True)
            raise EhrApiError(f"Failed to start registration: {str(e)}") from e

    async def registration_flow(
        self, step: HprRegistrationSteps, payload: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Executes a specific step in the HPR registration flow and returns the next step.

        Args:
            step (HprRegistrationSteps): The current step in the registration flow.
            payload (Dict[str, Any]): The data required for the current step.

        Returns:
            Dict[str, Any]: A dictionary containing the API response data, a user-friendly
                            message, and the name of the next step in the flow.

        Raises:
            EhrApiError: If the step is invalid, validation fails, or an API error occurs.
        """
        try:
            self.logger.info(f"Executing HPR registration flow step: {step.value}")

            if step == HprRegistrationSteps.VERIFY_AADHAAR_OTP:
                response = await self.hpr_service.verify_aadhaar_otp(payload)
                return {
                    "message": "Aadhaar OTP verified. Now, check if an HPR account exists.",
                    "data": response.model_dump(),
                    "next_step": HprRegistrationSteps.CHECK_ACCOUNT_EXIST.value,
                    "next_step_payload_hint": {
                        "description": "Provide the transaction ID from the current step's response data to check for an existing account.",
                        "required_fields": ["txnId",],
                        "source_of_data": {"txnId": "from current step's data.txnId"},
                    },
                }

            elif step == HprRegistrationSteps.CHECK_ACCOUNT_EXIST:
                response = await self.hpr_service.check_account_exist(payload)
                if(response.hprIdNumber):
                    return {
                        "message": "An HPR account already exists for this user. The registration flow is complete.",
                        "data": response.model_dump(),
                        "next_step": None,
                        "next_step_payload_hint": None,
                    }
                else:  # NonHprAccountResponse
                    return {
                        "message": "No HPR account found. Proceed to check whether mobile number is aadhaar authenticated or not. Store the response data for creating HPR ID.",
                        "data": response.model_dump(),
                        "next_step": HprRegistrationSteps.DEMOGRAPHIC_AUTH_VIA_MOBILE.value,
                        "next_step_payload_hint": {
                            "description": "Provide the mobile number for verification.",
                            "required_fields": ["mobileNumber", "txnId"],
                            "source_of_data": {"txnId": "from current step's data.txnId"},
                        }
                    }
                
            elif step == HprRegistrationSteps.DEMOGRAPHIC_AUTH_VIA_MOBILE:
                response = await self.hpr_service.demographic_auth_via_mobile(payload)
                if response.verified:
                    return {
                        "message": "Demographic auth successful. Proceed to generate mobile OTP.",
                        "data": response.model_dump(),
                        "next_step": HprRegistrationSteps.GENERATE_MOBILE_OTP.value,
                        "next_step_payload_hint": {
                            "description": "Provide the mobile number for OTP generation.",
                            "required_fields": ["mobileNumber", "txnId"],
                            "source_of_data": {"txnId": "from current step's data.txnId"}
                        }
                    }
                else:
                    return {
                        "message": "Demographic auth failed. Proceed to get HPR ID suggestions.",
                        "data": response.model_dump(),
                        "next_step": HprRegistrationSteps.GET_HPR_ID_SUGGESTION.value,
                    }

            elif step == HprRegistrationSteps.GENERATE_MOBILE_OTP:
                response = await self.hpr_service.generate_mobile_otp(payload)
                return {
                    "message": "Mobile OTP generated. Please verify it in the next step.",
                    "data": response.model_dump(),
                    "next_step": HprRegistrationSteps.VERIFY_MOBILE_OTP.value,
                    "next_step_payload_hint": {
                        "description": "Provide the OTP value for verification.",
                        "required_fields": ["otp", "txnId"],
                        "source_of_data": {"txnId": "from current step's data.txnId"}
                    }
                }
            
            elif step == HprRegistrationSteps.VERIFY_MOBILE_OTP:
                response = await self.hpr_service.verify_mobile_otp(payload)
                return {
                    "message": "Mobile OTP verified.",
                    "data": response.model_dump(),
                    "next_step": HprRegistrationSteps.GET_HPR_ID_SUGGESTION.value,
                    "next_step_payload_hint": {
                        "description": "Provide the transaction ID from the current step's response data to select one hprId name in list of options",
                        "required_fields": ["txnId"],
                        "source_of_data": {"txnId": "from current step's data.txnId"}
                    }
                }
            

            elif step == HprRegistrationSteps.GET_HPR_ID_SUGGESTION:
                response = await self.hpr_service.get_hpr_suggestion(payload)
                return {
                    "message": "HPR ID suggestions retrieved. Proceed to create the HPR ID.",
                    "data": response,
                    "next_step": HprRegistrationSteps.CREATE_HPR_ID_WITH_PREVERIFIED.value,
                    "next_step_payload_hint": {
                        "description": "Provide a chosen hprId, a password, and all user demographic data from previous steps.",
                        "required_fields": [
                            "hprId",
                            "password",
                            "txnId",
                            "firstName",
                            "middleName",
                            "lastName",
                            "yearOfBirth",
                            "dayOfBirth",
                            "monthOfBirth",
                            "gender",
                            "email",
                            "mobile",
                            "address",
                        ],
                        "source_of_data": {
                            "hprId": "user choice from current step's data.suggestions",
                            "password": "user input",
                            "txnId": "from previous steps",
                            "other_fields": "from CHECK_ACCOUNT_EXIST step's data",
                        },
                    },
                }

            elif step == HprRegistrationSteps.CREATE_HPR_ID_WITH_PREVERIFIED:
                response = await self.hpr_service.create_hpr_id_with_preverified(payload)
                return {
                    "next_step": None,
                    "message": "HPR ID created successfully. Registration complete.",
                    "data": response.model_dump(),
                }

            else:
                raise EhrApiError(f"Invalid or out-of-sequence step in HPR registration flow: {step}")

        except (EhrApiError, ValidationError) as e:
            self.logger.error(f"Error in HPR flow at step {step}: {e}", exc_info=True)
            raise e
        except Exception as e:
            self.logger.error(f"Unexpected error in HPR flow at step {step}", exc_info=True)
            raise EhrApiError(f"An unexpected error occurred during step {step}: {str(e)}") from e