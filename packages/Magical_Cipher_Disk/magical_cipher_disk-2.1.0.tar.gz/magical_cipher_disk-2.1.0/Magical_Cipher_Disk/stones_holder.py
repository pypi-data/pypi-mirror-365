from .stones import BaseStone
from pydantic import BaseModel, Field, PrivateAttr, model_validator, field_validator
from typing import Self

class StoneHolder(BaseModel):
    """
    Guarda la coleccion de 'Stones' y maneja cuando aplicar sus efectos para las transformaciones de letras.

    Combina la lista dada de 'Stones' en un diccionario de nombre y valor para un uso mas sencillo.
    Ademas recuerda / guarda los 'steps' / 'pasos' de cada transforacion para poder hacer un log despues.

    Args:
        stones (list[BaseStone]): Lista de 'BaseStones' de la cual se tomaran los efectos para las transforaciones.
    """
    stones:list[BaseStone] = Field(default_factory=list[BaseStone])
    _steps:list[str] = PrivateAttr(default_factory=list[str])
    _merged_stones:dict[str,BaseStone] = PrivateAttr(default_factory=dict[str,BaseStone])

    @model_validator(mode="after")
    def merge_stones(self) -> Self:
        self._merged_stones = {}
        for stone in self.stones:
            key  = stone.name
            if key in self._merged_stones:
                self._merged_stones[key] = self._merged_stones[key] + stone
            else:
                self._merged_stones[key] = stone

        return self

    @property
    def stones_dict(self) -> dict[str,BaseStone]:
        """
        Retorna un diccionario copia de 'Stones' guardadas, por nombre y valor.
        """
        return self._merged_stones.copy()
    
    @property
    def steps(self) -> str:
        """
        Retorna un string formateado de todos los 'steps' / 'pasos' guardados, uno por linea.
        """
        return "\n".join(self._steps)
    
    def apply_stones(self,letter:str,position:int = 0,source_alphabet:str = None,target_alphabet:str = None,isEncrypted:bool = False) -> str:
        """
        Aplica transformaciones basadas en las 'Stones' que fueron guardadas previamente usando el 'StoneHolder', estas transformaciones
        cambian la letra a otra.

        Si la letra no sufrio ningun cambio con las piedras anteriores, se hara un cambio simple.

        Ademas se guarda el 'step' / 'paso' por cada transformación.

        Args:
            letter (str): La letra a la que se aplicaran los cambios.
            position (int): La posicion de la letra en la frase u oracion, usada para saber cuando aplicar las piedras.
            source_alphabet (str): El alfabeto de origen del que se tomara el indice de la letra.
            target_alphabet (str): El alfabeto objetivo del que se usara la letra para sustituir.
            isEncrypted (bool, optional): El valor para conocer si se esta Encriptando o Desencriptando.

        Raises:
            ValueError: Error conel Alfabeto.

        Returns:
            str: La letra cambiada despues de todas las transformaciones. 
        """

        if not source_alphabet or not isinstance(source_alphabet,str):
            raise ValueError(f"Error with the alphabet {source_alphabet}") 
        
        if not target_alphabet or not isinstance(target_alphabet,str):
            raise ValueError(f"Error with the alphabet {target_alphabet}")

        YELLOW_STONE:BaseStone = self._merged_stones.get("YELLOW")

        if YELLOW_STONE and YELLOW_STONE.value > 0 and position >= 0:
            if position % YELLOW_STONE.value == 0:
                _letter = self._call_stone_redgreen(
                    letter=letter,
                    source_alphabet=source_alphabet,
                    target_alphabet=target_alphabet,
                    isEncrypted=isEncrypted
                )
                
                _letter = self._call_stone_blue(
                    letter=_letter,
                    position=position,
                    source_alphabet=source_alphabet,
                    target_alphabet=target_alphabet,
                    isEncrypted=isEncrypted
                )
                
                if letter == _letter:
                    _letter = self._call_simple_change(
                        letter=letter,
                        source_alphabet=source_alphabet,
                        target_alphabet=target_alphabet
                    )

                return _letter
            
        return self._call_simple_change(
            letter=letter,
            source_alphabet=source_alphabet,
            target_alphabet=target_alphabet
        )
    
    ## CALL LETTER CHANGES STONES/SIMPLE ##
    def _call_simple_change(self,letter:str,source_alphabet:str,target_alphabet:str) -> str:
        """
        Cambio simple de una letra y añadiendo el step al registro.
        """
        _letter = self._change_letter(letter,source_alphabet,target_alphabet)

        self.add_step(f"{letter} -> {_letter} -- Change [SIMPLE]")

        return _letter

    def _call_stone_redgreen(self,letter:str,source_alphabet:str,target_alphabet:str,isEncrypted:bool) -> str:
        """
        LLamada a la RED-GREEN Stone siesta disponible, y genera el cambio ademas de guardar el step en el registro.
        """
        REDGREEN_STONE:BaseStone = self._merged_stones.get("RED-GREEN")

        if REDGREEN_STONE:
            _letter = REDGREEN_STONE.apply(letter, source_alphabet, target_alphabet, isEncrypted)

            self.add_step(f"{letter} -> {_letter} -- Change [RED-GREEN]")
            return _letter
        
        return letter

    def _call_stone_blue(self,letter:str,position:int,source_alphabet:str,target_alphabet:str,isEncrypted:bool) -> str:
        """
        LLamada a la BLUE Stone siesta disponible, y genera el cambio ademas de guardar el step en el registro.
        """
        BLUE_STONE:BaseStone = self._merged_stones.get("BLUE")

        if BLUE_STONE:
            if BLUE_STONE.value > 0 and position % BLUE_STONE.value == 0:
                _letter = BLUE_STONE.apply(letter, source_alphabet, target_alphabet, isEncrypted)

                self.add_step(f" ^ {letter} -> {_letter} -- Change [BLUE]")
                return _letter
        
        return letter
        
    ## GETTERS ##
    def get_steps_by_stone(self, stone_name: str) -> list[str]:
        """
        Toma los 'steps' / 'pasos' para devolver solo aquellos que sean de la piedra
        requerida.

        Args:
            stone_name (str): Nombre de la piedra de la cual se quieren obtener los 'steps' / 'pasos'.

        Returns:
            list[str]: Lista de 'steps' / 'pasos' de la piedra especificada.
        """
        return [t for t in self._steps if f"[{stone_name.upper()}]" in t]
    
    ## HELPERS ##
    def _change_letter(self,letter:str,source_alphabet:str,target_alphabet:str) -> str:
        """
        Cambia la letra a su substitucion directa del 'source alphabet' al 'target alphabet',
        usando el indice de la letra.

        Args:
            letter (str): La letra que se cambiara.
            source_alphabet (str): El alfabeto de origen del que se tomara el indice de la letra.
            target_alphabet (str): El alfabeto objetivo del que se usara la letra para sustituir.

        Returns:
            str: La letra cambiada.
        """
        if letter in source_alphabet:
            _index = source_alphabet.index(str.upper(letter))
            _result = str.upper(target_alphabet[_index])
            return _result
        
        return letter
    
    def _clean_steps(self) -> None:
        """
        Limpia / Reinicia los 'steps' / 'pasos' que se guardaron anteriormente
        """
        self._steps = []

    def add_step(self,text:str) -> None:
        """
        Añade 'steps' / 'pasos' para guardar el proceso.

        Args:
            text (str): El texto que se guardara como 'step' / 'paso'
        """
        self._steps.append(text)