import logging
from typing import Optional
from carestack.appointment.appointment_dto import AppointmentDTO, AppointmentResponse, CreateAppointmentResponeType, GetAppointmentResponse, UpdateAppointmentDTO
from carestack.base.base_service import BaseService
from carestack.base.base_types import ClientConfig
from carestack.base.errors import EhrApiError
from carestack.common.enums import AppointmentEndpoints

class AppointmentService(BaseService):
    """
    Service for managing appointments.
    """

    def __init__(self, config: ClientConfig):
        super().__init__(config)
        self.logger = logging.getLogger(__name__)

        
    async def create(
        self, appointment_data: AppointmentDTO
    ) -> CreateAppointmentResponeType:
        """Sends appointment creation request to the API."""
        response = await self.post(
            AppointmentEndpoints.ADD_APPOINTMENT,
            appointment_data.model_dump(by_alias=True, exclude_none=True, mode="json"),
            response_model=CreateAppointmentResponeType,# type: ignore
        )
        return response
    
    async def find_all(self, next_page: Optional[str] = None) -> GetAppointmentResponse:
        """Retrieves all appointments with optional pagination."""
        try:
            params = {"nextPage": next_page} if next_page else None
            response = await self.get(AppointmentEndpoints.GET_ALL_APPOINTMENTS, response_model=GetAppointmentResponse, query_params=params)
            return response
        except EhrApiError as e:
            self.logger.error("Error fetching all appointments: %s", e, exc_info=True)
            raise
        except Exception as e:
            self.logger.error("An unexpected error occurred while fetching all appointments: %s", e, exc_info=True)
            raise EhrApiError("An unexpected error occurred while fetching all appointments.", 500) from e

    async def find_by_id(self, appointment_reference: str) -> AppointmentResponse:
        """Retrieves an appointment by its ID."""
        if appointment_reference is None or appointment_reference.strip() == "":
            raise EhrApiError("Appointment Reference cannot be null or empty.", 400)
        try:
            response = await self.get(AppointmentEndpoints.GET_APPOINTMENT_BY_ID.format(reference=appointment_reference), response_model=AppointmentResponse)
            return response
        except EhrApiError as e:
            self.logger.error("Error fetching appointment: %s", e, exc_info=True)
            raise e
        except Exception as e:
            self.logger.error("An unexpected error occurred while fetching appointment: %s", e, exc_info=True)
            raise EhrApiError("An unexpected error occurred while fetching appointment.", 500)
        
    async def exists(self,appointment_reference: str)->bool:
        """Checks if an appointment exists by its ID."""
        if not appointment_reference:
            return False
        try:
            response = await self.get(AppointmentEndpoints.APPOINTMENT_EXISTS.format(reference=appointment_reference), AppointmentResponse)
            if response.message == "Appointment Found !!!":
                return True
            else:
                return False
        except EhrApiError as e:
            raise e 
        except Exception as e:
            self.logger.error("An unexpected error occurred while checking appointment existence: %s", e, exc_info=True)
            raise EhrApiError ("An unexcepted error occurred while checking appointment existence.", 500) from e
        
    
    async def delete(self, appointment_reference: str) -> None:
        """
        Deletes a patient by ID.

        Args:
            patient_id (str): The patient's unique ID.

        Raises:
            EhrApiError: If the ID is invalid or the request fails.
        """
        if not appointment_reference:
            raise EhrApiError("Patient ID cannot be null or empty.", 400)
        try:
            await super().delete(
                AppointmentEndpoints.DELETE_APPOINTMENT.format(reference=appointment_reference),
            )
        except EhrApiError as e:
            raise e
        except Exception as e:
            self.logger.error(
                "An unexpected error occurred while deleting patient: %s",
                e,
                exc_info=True,
            )
            raise EhrApiError(
                f"An unexpected error occurred while deleting patient: {e}", 500
            ) from e
    
    async def update(self, request_body: UpdateAppointmentDTO) -> AppointmentResponse:
        """Updates an appointment."""
        try:
            response = await self.put(AppointmentEndpoints.UPDATE_APPOINTMENT, request_body, AppointmentResponse)
            return response
        except EhrApiError as e:
            self.logger.error("Error updating appointment: %s", e, exc_info=True)
            raise e
        except Exception as e:
            self.logger.error("An unexpected error occurred while updating appointment: %s", e, exc_info=True)
            raise EhrApiError("An unexpected error occurred while updating appointment.", 500) from e
           