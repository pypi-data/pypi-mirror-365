from pydantic import BaseModel, Field, PrivateAttr, field_validator
from typing import Self

class BaseStone(BaseModel):
    """
    Base para la creacion de mas Stones, donde debera usarse el metodo apply() para configurar su efecto.

    Args:
        name (str): Nombre de la piedra, generalmente se usa un color.
        value (int): Valor de la piedra.
    """
    value:int = Field(default=0)
    _name:str = PrivateAttr(default=None)

    @field_validator("value",mode="before")
    @classmethod
    def validate_value(cls,value:int) -> int:

        if not isinstance(value,int):
            raise TypeError(f"Expected int, got {type(value).__name__}")
        
        if value < 0:
            raise ValueError("value must be a positive integer")
        
        return value
    
    @property
    def name(self) -> str:
        """
        Retorna el nombre de la Stone.
        """
        return self._name
    
    def apply(self,letter:str,source_alphabet:str = None,target_alphabet:str = None,isEncrypted:bool = False) -> str:
        """
        Efecto de la Stone, donde se decidira de que manera se cambiara la letra.

        Args:
            letter (str): Letra que se cambiara.
            source_alphabet (str): El alfabeto de origen del que se tomara el indice de la letra.
            target_alphabet (str): El alfabeto objetivo del que se usara la letra para sustituir.
            isEncrypted (bool): Esta encriptada o no esta encriptada.

        Returns:
            str: Letra transformada.
        """
        return letter

    def __str__(self) -> str:
        return f"{self.name}:{self.value}"
    
    def __repr__(self) -> str:
        return f"Stone(name={self.name},value={self.value})"
    
    def __eq__(self, other:Self) -> bool:
        if isinstance(other,self.__class__):
            return self.name == other.name
        return False
    
    def __add__(self,other:Self) -> Self:
        if isinstance(other,self.__class__) and self == other:
            new_value  = self.value + other.value
            return self.__class__(value = new_value)
        raise TypeError(f"Expected {type(self).__name__}, got {type(other).__name__}")