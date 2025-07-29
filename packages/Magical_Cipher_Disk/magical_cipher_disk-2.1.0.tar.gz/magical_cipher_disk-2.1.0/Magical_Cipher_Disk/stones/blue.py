from .base import BaseStone
from pydantic import PrivateAttr

class BlueStone(BaseStone):
    _name:str = PrivateAttr(default="BLUE")

    def apply(self,letter:str,source_alphabet:str = None,target_alphabet:str = None,isEncrypted:bool = False) -> str:
        """
        Efecto de la Stone, donde se decidira de que manera se cambiara la letra.
        
        Aplica una transformacion a la letra, cambiando su posicion al exacto opuesto en el alfabeto.

        Args:
            letter (str): Letra que se cambiara.
            source_alphabet (str): El alfabeto de origen del que se tomara el indice de la letra.
            target_alphabet (str): El alfabeto objetivo del que se usara la letra para sustituir.
            isEncrypted (bool): Esta encriptada o no esta encriptada.

        Returns:
            str: Letra transformada.
        """
        len_alphabet = int(len(source_alphabet)/2)
        direction = -1 if isEncrypted else 1
        _index = (target_alphabet.index(str.upper(letter))+len_alphabet*direction)%len(target_alphabet)
        return str.upper(target_alphabet[_index])