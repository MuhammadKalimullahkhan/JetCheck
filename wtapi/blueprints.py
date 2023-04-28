from pydantic import BaseModel, Field
from typing import Optional


# class Auther(BaseModel):
#     fname : str
#     lname : str
    
class SubmitFileInfo(BaseModel):
    session_id    : Optional[str] = Field(alias="sid")
    file_stream   : Optional[bytes]
    file_name     : str 
    file_title    : Optional[str]
    auther_fname  : str
    auther_lname  : str
    assignment_id : Optional[int] = Field(alias="aid")
    class_url     : Optional[str] = Field(default="https://www.turnitin.com/t_class_home.asp?lang=en_us&cid=32539105")

    class Config:
        allow_population_by_field_name = True

class DownloadFileInfo(BaseModel):
    session_id    : Optional[str]
    file_title    : Optional[str]
    assignment_id : Optional[int]

    class Config:
        allow_population_by_field_name = True


# class FileInfo(BaseModel):
#     session_id : str = Field(alias="sid")
#     file_stream : bytes
#     file_name : str 
#     file_title : str
#     auther : Auther
#     assignment_id: int = Field(alias="aid")

#     @validator('file_stream', pre=True)
#     def bytes_to_base64(cls, value):
#         return base64.b64encode(value)

#     @validator('file_stream', pre=False)
#     def base64_to_bytes(cls, value):
#         return base64.b64decode(value)

#     class Config:
#         allow_population_by_field_name = True

# auther = Auther(
#     fname="Muhammad Kalim",
#     lname="Ullah"
# )

# file = File(
#     file_stream=bytes(),
#     file_name="Hello there.txt",
#     file_title="My New Thesis",
#     auther=auther,
#     sid="thisismysessionid",
#     assignment_id=123456789
# )

# print(file.json())