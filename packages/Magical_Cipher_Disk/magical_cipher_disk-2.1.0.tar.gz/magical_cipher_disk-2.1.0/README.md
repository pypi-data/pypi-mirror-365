# Magical Cipher Disk

## Tabla de Contenido

- [Errores Conocidos](#errores-conocidos)
    - [Caracteres Especiales](#caracteres-especiales) 
- [Inspiración](#inspiración)
- [Mécanicas](#mécanicas)
    - [Stones](#stones)
    - [Stone Holder](#stone-holder)
    - [Disk](#disk)
    - [Cipher](#cipher)
- [Ejemplo Completo](#ejemplo-completo)
- [CipherIO](#cipherio)
- [Changelog](#changelog)

## Errores Conocidos

### Caracteres Especiales

Si el mensaje de entrada contiene caracteres especiales que no existen en el source alphabet pero si en el target alphabet, este no podra encriptar o desencriptar del todo corrrectamente los mensajes, aunque no es un efecto que rompe el cifrado, si genera ruido o pequeños errores.
Un ejemplo de esto es tener los alfabetos asi al configurar el 'Cipher':

```python
source_alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
target_alphabet = "123456789?[]&,BCDEFGHIJKLM"

... (Resto de la configuracion)

Mensaje = "Hola, Buenás tardes, o es de dia?"

save_result = True

cipher_text = cipher.Encrypt(Mensaje,save_result)
# resultado = J18&, 4]5[?4 E&BG54, M 23 G5 GL&?

decipher_text = cipher.Decrypt(cipher_text,save_result)
# resultado = HOLAK SDVWRB KJIMVBB O ES DE DIAA

# La , paso a ser K y las demas igual cambiaron
```
El resultado seria un cifrado normal, pero si se quiere desencriptar es cuando el problema sucederia.
Pues caracteres como , o ? existirian en el mensaje cifrado, pero tambien en el alfabeto creando un bug porque el programa no sabe si estos pertenecian al mensaje original o son parte del cifrado.

Se esta buscando una manera de resolver / manejar esto.

## Inspiración

Este proyecto surgio por la necesidad de tener que encriptar mensajes para mis jugadores de D&D, queria hacer cifrados pero con añadidos de fantasia, si bien podria haberlos hecho a mano, teniendo este proyecto todo eso me resutlaria mas facil.

Esta basado en el Cifrado de César, simples discos que rotan y usan un Index para determinar el cifrado.

Las mecanicas añadidas son en base a fantasia, con piedras magicas que actuan como transformadores extra o aplican reglas especiales.

## Mécanicas

Este cifrado tiene 4 mecanicas.

### Stones

Las mas importantes, definen mayormente las reglas y comportamiento del cifrado, desde si debe hacerse o debe saltarse, debe cambiarse la letra ciertas posiciones, o incluso cambiarse por la letra al lado contrario del disco.

Por ahora hay 3 tipos de colores, y este color es el que dicta esas reglas.

- YELLOW: Bateria del cifrado, si esta no esta presente entonces ninguna otra piedra se activara.

- RED-GREEN: Es como una moneda de 2 caras, cambiara la letra por una posicion en sentido del reloj o a la inversa.

- BLUE: Cambiara la letra por la opuesta en el disco.

Cada piedra puede tener un valor, que servira para una u otra cosa en esa piedra.

- YELLOW: Cada cuanto se activaran las demas piedras, si su valor es 3 entonces cada 3 letras aplicaran las demas piedras. Su valor maximo sera 4 y si sobrepasa este numero sera como comenzar el conteo denuevo. Por ejemplo 7 sera 3 y 9 sera 1. Este servira como un Tempo.

- RED-GREEN: Cuantas posiciones se añadiran a la letra para cambiar su valor. Puede ser negavito o positivo.

- Blue: Sera un Tempo propio, cada vez que se cumpla ese tempo la letra se cambiara por su opuesto en el disco.

De esta manera, cada 2 letras se aplicaran las piedras.

```python
stone_yellow = YellowStone(2)
stone_redgreen = RedGreenStone(3)
stone_blue = BlueStone(4)
```

## Stone Holder

Encargado de aplicar las piedras y de llevar un control sobre cada paso realizado.

Aqui se guardaran todas las piedras que quieras aplicar a cierto cifrado.

```python
stone_holder_1 = StoneHolder([
    stone_yellow,
    stone_redgreen,
    stone_blue
])
```

## Disk

Representa uno de los discos del cifrado, especificamente el disco con los caracteres que seran el resultado de la encriptacion.

Un añadido propio a esta mecanica basada en la de César, es que cada disco es como un rompecabezas, que puede estar separado en partes y ordenarse de la manera que se guste despues. como si pasaras de la A-Z en un solo disco a tener A-G, P-Z, H-O. y asi tener un disco de 3 partes y ordenado de manera diferente.

Cada disco que quieras crear tendra que constar con 3 ajustes, el alfabeto, los splits y la seed.

- Alfabeto: El alfabeto que sera el que sustituira las letras del texto original, ya sea de A-Z o con caracteres especiales como  "#?![}.," y demas.

- Splits: Es una lista de int, cada int dentro de esta lista sera la cantidad de caracteres que determinaran el tamaño de esa parte del disco, si el alfabeto es mas grande y sobras letras entonces se creara un loop usando esa misma lista repetidamente, hasta que no queden mas.

seed: Una semilla para que la parte randomizada pueda replicarse si se necesita.

```python
disk_1 = Disk(
    alphabet = "¿#CDEFGHIJK[}*OPQRSTU?!XYZ",
    splits = [6,7],
    seed = 2025
)
```

## Cipher

La base de todo, no hay mucho que decir de esta parte mas alla de que es donde configuraras el cifrado para su encriptacion o desencriptacion.

Aqui le daras todo lo creado anteriormente para que el cipher este completo.

```python
cipher = Cipher(
    disk = disk_1,
    stone_holder = stone_holder_1,
    seed = 2025,
)
```

Ademas para configurar el alfabeto que se usara en el mensaje original, y el orden del Disk asi como su Index. Esto es necesario para el cifrado aunque por default tiene valores aleatorios, exceptuando el alfabeto que por default sera el normal de A-Z.

```python
cipher.config_cipher(
    source_alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
    disk_order = ['XS', '¿R', 'O[', 'J#'],
    disk_index = ('Q', 'X')
)
```

De esta manera el cipher ya habria quedado configurado para su uso, solo quedaria darle un mensaje para encriptarlo o desencriptarlo.

Ademas de decidir si ese mensaje se guarda o no, usando un True o False.

Lo cual podria quedar asi.

```python
mensaje = "Good Morning/Evening GitHub user"

mensaje_encriptado = cipher.Encrypt(mensaje,True)

mensaje_desencriptado = cipher.Decrypt(mensaje_encriptado,False)
```

Esto procederia a guardarse en un log, para poder ver toda la configuracion del cifrado, tanto las piedras como el disco.

## Ejemplo Completo 
```python
stone_yellow = YellowStone(2)
stone_redgreen = RedGreenStone(3)
stone_blue = BlueStone(4)

stone_holder_1 = StoneHolder([
    stone_yellow,
    stone_redgreen,
    stone_blue
])

disk_1 = Disk(
    alphabet = "¿#CDEFGHIJK[}*OPQRSTU?!XYZ",
    splits = [6,7],
    seed = 2025
)

cipher = Cipher(
    disk = disk_1,
    stone_holder = stone_holder_1,
    seed = 2025,
)

cipher.config_cipher(
    source_alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
    disk_order = ['XS', '¿R', 'O[', 'J#'],
    disk_index = ('Q', 'X')
)

mensaje = "Good Morning/Evening GitHub user"

mensaje_encriptado = cipher.Encrypt(mensaje)

mensaje_desencriptado = cipher.Decrypt(mensaje_encriptado)
```

## CipherIO

Al final el mensaje sera guardado en un Log, por default en una carpeta que creara llamada "Messages/Encrypted" o "Messages/Decrypted"

Aqui se guardaran las configuraciones usadas tanto de las Piedras como del Cifrado y sus alfabetos y demas.

usando el CipherIO puedes configurar esta ruta, aunque solo hace esto por ahora, a futuro añadire mas funciones a esta parte.

Ademas tendra que ser añadido a la configuracion del cipher para que este comience a usarlo.

```python
logger_1 = CipherIO(
    base_path = "./Messages"
)

cipher = Cipher(
    disk = disk_1,
    stone_holder = stone_holder_1,
    seed = 2025,
    logger = logger_1
)
```


## Changelog

Puedes consultar los cambios y versiones en el archivo [CHANGELOG.md](./CHANGELOG.md).
