from pydantic import BaseModel
from typing import List, Optional


class DomainRequest(BaseModel):
    extension: str
    description: str
    styles: Optional[List[str]] = None
    max_words: Optional[int] = 2
    include_misspelling: Optional[bool] = False


class DomainResponse(BaseModel):
    available_domains: Optional[List[str]] = None
    suggestions: List[str]





class DomainCheckRequest(BaseModel):
    names: List[str]
    extension: str


class DomainCheckResponse(BaseModel):
    available_domains: List[str]



class DomainResponseWizard(BaseModel):
    suggestions: list[str]
    available_domains: list[str] | None = None
