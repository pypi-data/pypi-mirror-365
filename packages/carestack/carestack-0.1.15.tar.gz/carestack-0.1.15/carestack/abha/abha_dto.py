from typing import Optional
from pydantic import BaseModel, Field

from carestack.common.enums import AuthMethodV2


class GenerateAadhaarOtpRequest(BaseModel):
    aadhaar: str

class VerifyOtpResponse(BaseModel):
    txnId: str
    message: str

class enrollWithAadhaar(BaseModel):
    otp: str
    txnId: str
    mobile: str

class AbhaProfile(BaseModel):
    preferredAddress: Optional[str] = None
    firstName: str
    lastName: str
    middleName: str
    dateOfBirth: Optional[str] = Field(None, alias="dob")
    gender: str
    profilePhoto: Optional[str] = Field(None, alias="photo")
    mobile: str
    mobileVerified: Optional[bool] = None
    email: Optional[str] = None
    phrAddress: Optional[list[str]] = None
    address: str
    districtCode: Optional[str] = None
    stateCode: Optional[str] = None
    pinCode: Optional[str] = None
    abhaType: str
    stateName: str
    districtName: str
    ABHANumber: str
    abhaStatus: str


    authMethods: Optional[AuthMethodV2] = None
    emailVerified: Optional[bool] = None
    kycPhoto: Optional[str] = None
    kycVerified: Optional[bool] = None
    monthOfBirth: Optional[str] = None
    name: Optional[str] = None
    subDistrictCode: Optional[str] = None
    subdistrictName: Optional[str] = None
    tags: Optional[dict[str, str]] = None
    townCode: Optional[str] = None
    townName: Optional[str] = None
    verificationStatus: Optional[str] = None
    verificationType: Optional[str] = None
    villageCode: Optional[str] = None
    villageName: Optional[str] = None
    wardCode: Optional[str] = None
    wardName: Optional[str] = None
    yearOfBirth: Optional[str] = None

class AbhaTokens(BaseModel):
    token: str
    expiresIn: int
    refreshToken: str
    refreshExpiresIn: int

class enrollWithAadhaarResponse(BaseModel):
    message: str
    txnId: str
    ABHAProfile: AbhaProfile
    tokens: AbhaTokens
    isNew: bool

class AbhaAddressSuggestionsResponse(BaseModel):
    abhaAddressList: list[str]
    txnId: str

class CreateAbhaAddressRequest(BaseModel):
    abhaAddress: str
    txnId: str

class CreateAbhaAddressResponse(BaseModel):
    txnId: str
    healthIdNumber: str
    preferredAbhaAddress: str

class UpdateMobileNumberRequest(BaseModel):
    updateValue: str = Field (..., alias="updateValue")
    txnId: str

class VerifyMobileOtpRequest(BaseModel):
    otp: str
    txnId: str

class VerifyMobileOtpResponse(BaseModel):
    message: str
    txnId: str
    authResult: str