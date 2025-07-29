from pydantic import BaseModel, PrivateAttr, model_validator, field_validator
from typing import Self
import random

class Disk(BaseModel):
    """
    Maneja la creacion de las partes del 'Disk' que se usara para Encriptar / Desencriptar.

    Args:
        alphabet (str, optional): Alfabeto que se usara para el 'Disk'.
        splits (list[int], optional): Lista de splits que se usara para dividir el disco en partes.
        seed (int, optional): Seed que se usara para las partes que requieran ser randomizadas, asi podran replicarse.
    """
    alphabet:str = None
    splits:list[int]  = None
    seed:int  = None

    _random:random.Random = PrivateAttr(default_factory=random.Random)
    _shuffled_alphabet:str = PrivateAttr()
    _parts:list[str] = PrivateAttr(default_factory=list)
    _disk_parts:dict[str,dict[str,int | str]] = PrivateAttr(default_factory=dict)

    @field_validator("seed",mode="before")
    @classmethod
    def validate_seed(cls,seed:int) -> int:

        if seed == None:
            return random.SystemRandom().randint(0, 2**32 - 1)
            
        if not isinstance(seed,int):
            raise TypeError(f"Expected int, got {type(seed).__name__}")
        
        if seed <= 0:
            raise ValueError("Seed must be a positive integer.")
        
        return seed
    
    @field_validator("alphabet",mode="before")
    @classmethod
    def validate_alphabet(cls,alphabet:str) -> str:
        if alphabet == None:
            return "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        
        if not isinstance(alphabet,str):
            raise TypeError(f"Expected str, got {type(alphabet).__name__}")
        
        return alphabet.upper()

    @field_validator("splits",mode="before")
    @classmethod
    def validate_splits(cls,splits:list[int]) -> list[int]:
        if splits == None:
            return splits
        
        if not all(isinstance(sp,int) for sp in splits):
            raise TypeError(f"Expected all values in the list to be integers")
        
        return splits

    @model_validator(mode="after")
    def build_disk(self) -> Self:

        self._random = random.Random(self.seed)
        
        self._shuffled_alphabet = self.__create_shuffle_alphabet()

        if self.splits is None:
            object.__setattr__(self, 'splits', self.__create_splits_list())

        self._parts = self.__create_split_alphabet()
        
        self._disk_parts = {}
        for part in self._parts:
            _id = f"{part[0]}{part[-1]}"
            self._disk_parts[_id] = {
                "lenght":len(part),
                "part":part
            }

        return self
    
    @property
    def parts_list(self) -> list[str]:
        """
        Retorna una lista copia de de las partes del 'Disk'.
        """
        return self._parts.copy()
    
    @property
    def parts_dict(self) -> dict[str,dict[str,int | str]]:
        """
        Retorna un diccionario copia de las partes del 'Disk'.
        """
        return self._disk_parts.copy()
    
    @property
    def ids(self) -> list[str]:
        """
        Retorna la lista de las ids de cada parte.
        """
        return list(self._disk_parts.keys())
    
    @property
    def alphabet_len(self) -> int:
        """
        Retorna el tamaño del alfabeto.
        """
        return len(self.alphabet)
    
    def get_splits(self) -> list[int]:
        """
        Retorna una copia de la lista de splits.
        """
        return self.splits.copy()

    def validate_alphabets(self,source_alphabet:str = None) -> bool:
        """
        Valida los alfabetos tanto del Disk como el proporcionado en la funcion,
        tomando en cuenta solo el tamaño de ambos.

        Args:
            source_alphabet (str): Alfabeto que se usara como comparacion.

        Returns:
            bool: Verdadero si son iguales o Falso si no.
        """
        if not isinstance(source_alphabet,str):
            return False
            
        return len(source_alphabet) == len(self.alphabet)

    ## HELPERS ##
    def __create_shuffle_alphabet(self) -> str:
        """
        Randomiza el orden del alfabeto.

        Returns:
            str: Alfabeto revuelto / desordenado.
        """
        _shuffled_alphabet = list(self.alphabet)[:]
        self._random.shuffle(_shuffled_alphabet)

        return "".join(_shuffled_alphabet)
    
    def __create_splits_list(self) -> list[int]:
        """
        Crea splits random, entre 3 y 6 partes.

        Returns:
            list[int]: Lista de splits.
        """
        _num_parts = self._random.randint(3,6)
        _len_alphabet = len(self._shuffled_alphabet)
        
        _base = _len_alphabet // _num_parts
        _extra = _len_alphabet % _num_parts

        _splits_list = [_base + (1 if i < _extra else 0) for i in range(_num_parts)]

        return _splits_list
    
    def __create_split_alphabet(self) -> list[str]:
        """
        Crea los splits del alfabeto y los splits guardados, esto creara lo que seran las partes del 'Disk'

        Returns:
            list[str]: Lista de partes del alfabeto.
        """
        _split_alphabet = []
        _temp_alphabet = self._shuffled_alphabet
        splits = self.splits
        idx = 0
        while len(_temp_alphabet) > 0:
            split_size = splits[idx % len(splits)]
            _split_alphabet.append(_temp_alphabet[:split_size])
            _temp_alphabet = _temp_alphabet[split_size:]
            idx += 1
        return _split_alphabet