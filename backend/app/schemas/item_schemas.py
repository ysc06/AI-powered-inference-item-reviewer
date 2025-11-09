from pydantic import BaseModel, field_validator
from typing import List, Optional


class GeneratedItem(BaseModel):
    stimulus: Optional[str] = None
    stem: Optional[str] = None
    choices: Optional[List[str]] = None
    # choices: Optional[str] = None 
 
    answer: Optional[str] = None 
    # Pydantic automatically check: leveraged Pydantic validators to encforce business rule at schema level.
    @field_validator("choices")
    def choices_length(cls, choices):
        for choice in choices:
            if len(choice.split())>12:
                raise ValueError("Each choice must be < 12 words.")
        return choices 
    

    @field_validator("stem")
    def stem_length(cls, stem):
        if len(stem) > 20:
            raise ValueError("A stem must be < 20 words.")
        return stem
    
               