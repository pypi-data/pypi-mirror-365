from .base import BaseStone
from pydantic import field_validator, PrivateAttr
from typing import Self

class YellowStone(BaseStone):
    _name:int = PrivateAttr(default="YELLOW")

    @field_validator("value",mode="before")
    @classmethod
    def validate_value(cls,value:int) -> int:
        
        if not isinstance(value,int):
            raise TypeError(f"Expected int, got {type(value).__name__}")
        
        if value < 0:
            raise ValueError("value must be a positive integer")
        
        return value % 4
    
    def __add__(self, other:Self) -> Self:
        """
        Las piedras de este color Yellow deben tener un maximo de valor de 4, por lo que cada suma se calculara usando el modulo con 4.
        """
        if isinstance(other,self.__class__) and self == other:
            new_value = (self.value + other.value) % 4
            return self.__class__(value=new_value)
        
        raise TypeError(f"Expected YellowStone, got {type(other).__name__}")