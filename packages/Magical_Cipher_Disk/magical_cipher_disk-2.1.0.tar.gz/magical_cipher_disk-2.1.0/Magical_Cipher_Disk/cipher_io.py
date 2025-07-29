from pathlib import Path
from datetime import datetime
from importlib.metadata import version, PackageNotFoundError

from .disk import Disk
from .stones_holder import StoneHolder
from pydantic import BaseModel, Field, PrivateAttr, model_validator, field_validator
from typing import Self

class CipherIO(BaseModel):
    """
    Maneja la creacion del archivo donde se guardan las configuraciones y demas del Cipher.

    Args:
        base_path (str, optional): Path Base de donde se quieren guardar los archivos. Default en "./Messages".
        debug (bool, optional): Esta en modo debug o no. Default en False.
    """
    debug:bool = False
    base_path:str = None

    _path:Path = PrivateAttr(default=None)

    _path_encrypted:Path = PrivateAttr(default=None)
    _path_decrypted:Path = PrivateAttr(default=None)

    @model_validator(mode="after")
    def create_paths(self) -> Self:

        if not self.base_path:
            _dir_path = "./Messages_For_Debug" if self.debug else "./Messages"
        else:
            _dir_path = self.base_path

        self._path = Path(_dir_path).resolve()
        self._path.mkdir(parents=True, exist_ok=True)

        self._path_encrypted = self._path / "Encrypted"
        self._path_decrypted = self._path / "Decrypted"

        for paths in [self._path_encrypted,self._path_decrypted]:
            paths.mkdir(parents=True,exist_ok=True)

        return self

    def _unique_path(self, name: str,timestamp:str, is_encrypted_suffix: str, ext: str = "txt") -> Path:
        """
        Creacion del path del archivo para que sea unico.

        Args:
            name (str): Nombre del archivo.
            timestamp (str): Fecha.
            is_encrypted_suffix (str): Esta encriptado o no esta encriptado.
            ext (str, optional): Extension del archivo. Default en "txt".

        Returns:
            Path: Path completo del archivo
        """
        filename = f"{timestamp}_{is_encrypted_suffix.upper()}_{name}.{ext}"
        _is_encrypted_suffix = is_encrypted_suffix.lower() 

        if _is_encrypted_suffix == "encrypted":
            return self._path_encrypted / filename
        elif _is_encrypted_suffix == "decrypted":
            return self._path_decrypted / filename
        else:
            return self._path / filename
    
    def log_cipher(self,
                original_text:str,result_text:str,isEncrypted:bool,
                disk:Disk,disk_order:list[str],disk_index:tuple[str,str],stone_holder:StoneHolder,
                name:str, source_alphabet:str, target_alphabet:str, cipher_seed:int
            ) -> None:
        """
        Guarda la configuracion, el texto de entrada y salida, y las piedras usadas.

        Ademas, si existen, se guardaran los 'steps' / 'pasos' de la transformacion del texto.

        Args:
            original_text (str): Texto original.
            result_text (str): Texto como resultado, ya sea encriptado o desencriptado.
            isEncrypted (bool): El texto original esta encriptado o desencriptado.
            disk (Disk): Disk usado en el cifrado.
            disk_order (list[str]): Orden de las partes del Disk
            disk_index (tuple[str,str]): Index de los alfabetos.
            stone_holder (StoneHolder): StoneHolder.
            name (str): Nombre para el archivo como extra.
            source_alphabet (str): Alfabeto original.
            target_alphabet (str): Alfabeto del Disk.
        """

        is_encrypted_suffix = "DECRYPTED" if isEncrypted else "ENCRYPTED"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        try:
            __version__ = version("Magical_Cipher_Disk")
        except PackageNotFoundError:
            __version__ = ""

        _name = name if name else ""

        required = {
                "original_text": original_text,
                "result_text": result_text,
                "disk": disk,
                "disk_order": disk_order,
                "disk_index": disk_index,
                "stone_holder": stone_holder,
                "source_alphabet": source_alphabet,
                "target_alphabet": target_alphabet
            }

        for key, value in required.items():
            if value is None or value == "":
                raise ValueError(f"Missing required: '{key}'")
            
        path = self._unique_path(_name,timestamp,is_encrypted_suffix)

        data = ""

        data += f"###### {is_encrypted_suffix} ######\n"
        data += f"Date: {timestamp}\n"
        data += f"Version: {__version__}\n\n"

        data += f"###### TEXT ######\n"
        data += f"{original_text}\n\n"
        data += f"###### RESULT {is_encrypted_suffix} ######\n"
        data += f"{result_text}\n\n"

        data += f"###### ALPHABETS ######\n"
        data += f"Source Alphabet: {source_alphabet}\n"
        data += f"Target Alphabet: {target_alphabet}\n\n"

        data += f"###### Disk ######\n"
        data += f"Seed: {disk.seed}\n"
        data += f"Splits: {disk.get_splits()}'\n"
        data += f"Ids: {disk.ids}\n"
        data += f"Parts. {disk.parts_list}\n"
        data += f"Order: {disk_order}\n"
        data += f"Index: {disk_index}\n\n"


        data += f"###### Stones ######\n"
        data += f"[STONE] -- [VALUE]\n"

        stones = stone_holder.stones_dict
        for stone in stones:
            _stone = stones.get(stone)
            data += f"{_stone.name} -- {_stone.value}\n"
        
        data += f"\n###### Cipher ######\n"
        data += f"Seed: {cipher_seed}\n"

        _traces = stone_holder.steps
        if _traces:
            data += f"\n###### TRACES ######\n"
            data += f"{_traces}"

        path.write_text(data,encoding="utf-8")