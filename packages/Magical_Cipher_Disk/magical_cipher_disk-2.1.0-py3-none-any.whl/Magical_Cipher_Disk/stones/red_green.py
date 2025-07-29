from .base import BaseStone
from pydantic import PrivateAttr

class RedGreenStone(BaseStone):
    _name:str = PrivateAttr(default="RED-GREEN")

    def apply(self,letter:str,source_alphabet:str = None,target_alphabet:str = None,isEncrypted:bool = False) -> str:
        """
        Efecto de la Stone, donde se decidira de que manera se cambiara la letra.

        Aplica una transformacion cambiando la posicion de la letra usando el valor de la piedra, ya sea en sentido horario (Positivo) o en sentido contrario (Negativo)
        tomando el index del source alphabet y usandolo en el target alphabet.
        
        Args:
            letter (str): Letra que se cambiara.
            source_alphabet (str): El alfabeto de origen del que se tomara el indice de la letra.
            target_alphabet (str): El alfabeto objetivo del que se usara la letra para sustituir.
            isEncrypted (bool): Esta encriptada o no esta encriptada.

        Returns:
            str: Letra transformada.
        """
        _orden = -self.value if isEncrypted else self.value

        _index = (source_alphabet.index(str.upper(letter))+_orden)%len(target_alphabet)
        return str.upper(target_alphabet[_index])