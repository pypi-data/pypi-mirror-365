from .disk import Disk
from .stones_holder import StoneHolder
from .cipher_io import CipherIO
from pydantic import BaseModel, Field, PrivateAttr, model_validator, field_validator
from typing import Self
import random
from unidecode import unidecode
import warnings

class Cipher(BaseModel):
    """
    Maneja el Encriptado o Desencriptado, usando el 'Disk' y las 'Stones' del 'StoneHolder'.

    Usa un estado o seed para lo que requiera randomizacion, y asi poder replicarlo.

    Args:
        disk (Disk, optional): Disk que se usara para el cifrado.
        stone_holder (StoneHolder, optional): StoneHolder que guarda las Stones que se usaran para los efectos y transformaciones.
        logger (CipherIO, optional): Logger para guardar todo el proceso y configuraciones, usa la clase CipherIO.
        seed (int, optional): Seed que se usara para las partes que requieran ser randomizadas, asi podran replicarse.
    """
    logger:CipherIO = None
    disk:Disk = None
    stone_holder:StoneHolder = None
    seed:int = None

    _random:random.Random = PrivateAttr(default=None)
    _disk_order:list[str] = PrivateAttr(default_factory=list[str])
    _source_alphabet:str = PrivateAttr(default=None)
    _target_alphabet:str = PrivateAttr(default=None)

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
    
    @field_validator("logger",mode="before")
    @classmethod
    def validate_logger(cls,logger:CipherIO) -> CipherIO:
        if logger == None:
            return CipherIO()

        if not isinstance(logger,CipherIO):
            raise TypeError(f"Expected CipherIO, got {type(logger).__name__}")
        
        return logger
        
    @model_validator(mode="after")
    def build_cipher(self) -> Self:

        if not isinstance(self.disk,Disk):
            raise TypeError(f"Expected Disk, got {type(self.disk).__name__}")
        
        if not isinstance(self.stone_holder,StoneHolder):
            raise TypeError(f"Expected StoneHolder, got {type(self.stone_holder).__name__}")

        self._random = random.Random(self.seed)

        return self

    @property
    def source_alphabet(self) -> str:
        """
        Retorna el alfabeto proporcionado en la configuracion del cifrador.
        """
        return self._source_alphabet
    
    @property
    def target_alphabet(self) -> str:
        """
        Retorna el alfabeto del 'Disk' proporcionado.
        """
        return self._target_alphabet

    def Encrypt(self,entry_text:str = None,save_result:bool = True,context_for_log:str = "") -> str:
        """
        Encripta el texto proporcionado.        

        Args:
            entry_text (str, optional): Texto para encriptar.
            save_result (bool, optional): Se guardara el resultado en un log o no. Default en True.
            context_for_log (str, optional): Sera el nombre que se añadira al archivo generado.

        Returns:
            str: Texto Encriptado.
        """
        return self._Cipher(
            entry_text=entry_text,
            isEncrypted=False,
            save_result=save_result,
            context_for_log=context_for_log
        )
    
    def Decrypt(self,entry_text:str = None,save_result:bool = True,context_for_log:str = "") -> str:
        """
        Desencripta el texto proporcionado.        

        Args:
            entry_text (str, optional): Texto para desencriptar.
            save_result (bool, optional): Se guardara el resultado en un log o no. Default en True.
            context_for_log (str, optional): Sera el nombre que se añadira al archivo generado.

        Returns:
            str: Texto Desencriptado.
        """
        return self._Cipher(
            entry_text=entry_text,
            isEncrypted=True,
            save_result=save_result,
            context_for_log=context_for_log
        )
    
    def config_cipher(self,source_alphabet:str = None,disk_order:list[str] = None,disk_index:tuple[str,str] = None) -> None:
        """
        Configuira el cifrado que se hara, con los siguientes parametros.

        Args:
            source_alphabet (str, optional): Alfabeto que se usara como origen.
            disk_order (list[str], optional): Orden de las partes del 'Disk'
            disk_index (tuple[str,str], optional): Index con el que se juntaran los alfabetos, estos deben ser 1 letra del original y 1 del alfabeto del 'Disk'.
        """
        _source_alphabet = source_alphabet.upper() if source_alphabet else 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

        if not self.disk.validate_alphabets(_source_alphabet):
            raise ValueError(f"Alphabets are not the same lenght, wich will cause errors in the Encryption or Decryption\nlen of disk {self._disk.alphabet_len}\nlen of cipher {len(source_alphabet)}")

        self._disk_order = disk_order if disk_order else self._random_disk_order()

        disk_parts:dict = self.disk.parts_dict
        
        _temp_alphabet = ''.join(
            letter
            for disk_id in self._disk_order
            for letter in disk_parts[disk_id]["part"]
        )

        if disk_index:
            self._disk_index = disk_index
        else:
            _index_1 = self._random.choice(_source_alphabet)
            _index_2 = self._random.choice(_temp_alphabet)
            self._disk_index = (_index_1,_index_2)
        
        _index_source_alphabet = _source_alphabet.index(str(self._disk_index[0]).upper())
        _index_target_alphabet = _temp_alphabet.index(str(self._disk_index[1]).upper())

        self._source_alphabet = _source_alphabet[_index_source_alphabet:] + _source_alphabet[:_index_source_alphabet]
        self._target_alphabet = _temp_alphabet[_index_target_alphabet:] + _temp_alphabet[:_index_target_alphabet]

        return self

    def _Cipher(self,entry_text:str = None,isEncrypted:bool = False,save_result:bool = True,context_for_log:str = "") -> str:
        """
        Encargado de encriptar o desencriptar, maneja el paso de las letras al 'StoneHolder' o el paso de caracteres especiales
        como comas, guiones, espacios, etc.

        Args:
            entry_text (str, optional): Texto de entrada al que se le aplicaran las transformaciones.
            isEncrypted (bool, optional): Esta encriptado o no esta encriptado, asi se sabra que transformaciones hacer. Default en False.
            save_result (bool, optional): Se guardara el resultado o no se guardara. Defaults en True.
            context_for_log (str, optional): Sera el nombre que se añadira al archivo generado.

        Raises:
            ValueError: Text was not provided

        Returns:
            str: Text result of the cipher transformations.
        """
        if not entry_text or entry_text == "":
            raise ValueError("There is no text")

        space_positions,_text_no_spaces = self._remove_spaces_from_text(entry_text)

        _source_alphabet,_target_alphabet = self._get_alphabets(isEncrypted)

        _normalized_entry_text = self._normalize_text(
            text=_text_no_spaces,
            source_alphabet=_source_alphabet
        )

        # Cipher
        _cipher_text = ""
        position_offset_for_special_char = 0
        
        for idx,letter in enumerate(_normalized_entry_text):

            _position = idx-position_offset_for_special_char
            if letter in _source_alphabet:
                _cipher_text += self.stone_holder.apply_stones(
                    letter=letter,
                    position=_position,
                    source_alphabet=_source_alphabet,
                    target_alphabet=_target_alphabet,
                    isEncrypted=isEncrypted
                )

            else:
                if letter in _target_alphabet:
                    _warning_text = "\nWarning by letter in the text that can create errors during encrypt or decrypt.\n"
                    _warning_text += f"This can be caused by the letter: [ {letter} ] that exist in the text provided and in the target alphabet but does't exist in the source alphabet"
                    _warning_text += "Please consider using special characters like ,-.? if they exist in the target alphabet but don't want it to be in de decrypt"
                    warnings.warn(message=_warning_text,category=UserWarning)
                position_offset_for_special_char += 1
                self.stone_holder.add_step(f"{letter} -- PASS")
                _cipher_text += letter


        _cipher_text = self._restore_spaces_from_text(_cipher_text,space_positions)

        if save_result:
            self.logger.log_cipher(
                original_text=entry_text.upper(),
                result_text=_cipher_text,
                isEncrypted=isEncrypted,
                disk=self.disk,
                disk_order=self._disk_order,
                disk_index=self._disk_index,
                stone_holder=self.stone_holder,
                name=context_for_log,
                source_alphabet=self._source_alphabet,
                target_alphabet=self._target_alphabet,
                cipher_seed=self.seed
            )

        self.stone_holder._clean_steps()
        return _cipher_text


    ## HELPERS ##
    def _remove_spaces_from_text(self,text:str) -> tuple[list[int],str]:
        """
        Remueve los espacios del texto y regresa sus posiciones y texto sin espacios.
        """
        spaces_positions:list[int] = [pos for pos,letter in enumerate(text) if letter == " "]
        new_text:str = text.replace(" ","")
        return spaces_positions,new_text
    
    def _restore_spaces_from_text(self,spaceless_text:str,space_positions:list[int]) -> str:
        """
        Recrea los espacios del texto usando las posiciones dadas.
        """
        chars = list(spaceless_text)
        for pos in space_positions:
            chars.insert(pos," ")
        return "".join(chars)

    def _random_disk_order(self) -> list[str]:
        """
        Randomiza el orden de las partes del 'Disk' usando las ids de las partes.

        Returns:
            list[str]: Lista del orden randomizado.
        """
        keys = self._disk.ids
        choices = []
        for i in range(len(keys)):
            random_key = self._random.choice(keys)
            choices.append(random_key)
            keys.remove(random_key)
        return choices
    
    def _get_alphabets(self,isEncrypted) -> tuple[str,str]:
        """
        Revisa si se debe encriptar o desencriptar, para devolver el alfabeto como se requiera.

        Args:
            isEncrypted (bool): El texto viene encriptado o no.

        Returns:
            tuple[str,str]: Alfabetos en orden en el que se requieren para las transformaciones.
        """
        if isEncrypted:
            return self._target_alphabet,self._source_alphabet
        else:
            return self._source_alphabet,self._target_alphabet
        
    def _normalize_text(self,text:str='',source_alphabet:str = "") -> str:
        """
        Normaliza el texto para evitar acentos u otros caracteres especiales 
        que no existan en el source.
        Ademas de devolverlo commo mayusculas.

        Args:
            text (str): Texto que se requiere normalizar.
            source_alphabet (str): Alfabeto que se usara como origen.

        Returns:
            str: Texto normalizado.
        """
        normalized_text = ""
        for letter in text.upper():
            if letter not in source_alphabet:
                normalized_text += unidecode(letter)
            else:
                normalized_text += letter

        return normalized_text