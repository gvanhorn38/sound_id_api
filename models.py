
from datetime import datetime
from typing import Annotated, Optional, Union, List

from pydantic import BaseModel, HttpUrl, Field, AfterValidator, SerializeAsAny, conlist

class UrlConstraints:
    allowed_schemes = ["http", "https", "s3"]

ValidURL = Annotated[HttpUrl, UrlConstraints, AfterValidator(str)]

class Task(BaseModel):
    
    # Make URL optional (incase the user uploads a file)
    # SerializeAsAny is to suppress warnings about serialization
    # See here: https://github.com/pydantic/pydantic/issues/7905
    url: SerializeAsAny[Optional[ValidURL]] = None  
    latitude: float = Field(ge=-90, le=90) 
    longitude: float = Field(ge=-180, le=180)
    datetime: datetime
    include_species_codes: Optional[conlist(str, max_length=5)] = None  # Optional list

class Detection(BaseModel):
    species_code: str
    detection_events: int
    detections: int
    detection_rate: float
    max_score: float
    max_start_sec: float
    date_relevant: Optional[int] = 1

class DetectorInfo(BaseModel):
    version: Union[str, None] = None

class TaskStatus(BaseModel):
    id: str
    status: str
    message: Union[str, None] = None
    audio_duration: Union[float, None] = None
    detections: Union[List[Detection], None] = None
    detector_info: Union[DetectorInfo, None] = None