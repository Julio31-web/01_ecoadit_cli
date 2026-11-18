"""Módulo simulador: gestión de la flota de vehículos (clase Flota).

Agrupa vehículos de cualquier tipo en una misma lista y les aplica las
operaciones de forma polimórfica, sin comprobar de qué clase es cada uno.
También guarda y recupera la flota en formato JSON.
"""

import json

from vehiculo import CocheElectrico, PatineteElectrico, Vehiculo


class Flota:
    """Colección de vehículos eléctricos gestionada como una unidad."""

    def __init__(self) -> None:
        """Crea una flota vacía."""
        self._vehiculos: list[Vehiculo] = []  # Atributo protegido

    def agregar_vehiculo(self, vehiculo: Vehiculo) -> None:
        """Añade un vehículo (de cualquier subclase de Vehiculo).

        Raises:
            ValueError: si ya existe un vehículo con la misma matrícula.
        """
        for existente in self._vehiculos:
            if existente.matricula == vehiculo.matricula:
                raise ValueError(
                    f"Ya existe un vehículo con matrícula {vehiculo.matricula}"
                )
        self._vehiculos.append(vehiculo)

    def obtener_vehiculos(self) -> list[Vehiculo]:
        """Devuelve una copia de la lista de vehículos.

        Es una copia para que, desde fuera, nadie pueda añadir o borrar
        vehículos saltándose agregar_vehiculo().
        """
        return list(self._vehiculos)

    def simular_jornada(self, distancia_km: float) -> dict:
        """Hace que todos los vehículos intenten recorrer la misma distancia.

        Polimorfismo: cada objeto ejecuta SU versión de conducir()
        (el coche consume 0.15 kWh/km y el patinete 0.02 kWh/km).

        Returns:
            Diccionario {"exitosos": int, "fallidos": int}.
        """
        total_ok = 0
        total_fallos = 0
        for vehiculo in self._vehiculos:
            if vehiculo.conducir(distancia_km):
                total_ok += 1
            else:
                total_fallos += 1  # Batería insuficiente
        return {"exitosos": total_ok, "fallidos": total_fallos}

    def recargar_flota_critica(self, umbral_bateria: float = 20.0,
                               kwh_carga: float = 15.0) -> int:
        """Recarga los vehículos cuya batería está en el umbral o por debajo.

        Returns:
            Número de vehículos recargados.
        """
        recargados = 0
        for vehiculo in self._vehiculos:
            if vehiculo.nivel_bateria <= umbral_bateria:
                vehiculo.recargar(kwh_carga)
                recargados += 1
        return recargados

    # ------------------------------------------------------------------
    # Persistencia JSON (apartado 5.1)
    # ------------------------------------------------------------------
    def guardar_en_archivo(self, ruta: str = "flota.json") -> None:
        """Guarda todos los vehículos en un archivo JSON."""
        lista_datos = []
        for vehiculo in self._vehiculos:
            lista_datos.append(vehiculo.a_diccionario())
        with open(ruta, mode="w", encoding="utf-8") as archivo:
            # ensure_ascii=False: guarda las tildes tal cual (legible)
            json.dump(lista_datos, archivo, indent=4, ensure_ascii=False)

    def cargar_de_archivo(self, ruta: str = "flota.json") -> int:
        """Recupera la flota desde un archivo JSON.

        Si el archivo no existe o está dañado, avisa y no cambia la flota.
        Si la lectura es correcta, sustituye la flota actual por la del
        archivo. Los registros con datos incorrectos se ignoran con aviso.

        Returns:
            Número de vehículos restaurados (0 si no se pudo leer).
        """
        try:
            with open(ruta, mode="r", encoding="utf-8") as archivo:
                lista_datos = json.load(archivo)
        except FileNotFoundError:
            print(f"ℹ️ No existe '{ruta}'. Se parte de una flota vacía.")
            return 0
        except json.JSONDecodeError:
            print(f"⚠️ El archivo '{ruta}' está dañado (JSON incorrecto). "
                  "Se parte de una flota vacía.")
            return 0

        if not isinstance(lista_datos, list):
            print(f"⚠️ El archivo '{ruta}' no contiene una lista de "
                  "vehículos. Se parte de una flota vacía.")
            return 0

        self._vehiculos = []
        for datos in lista_datos:
            try:
                self.agregar_vehiculo(crear_vehiculo_desde_diccionario(datos))
            except KeyError as error:
                print(f"⚠️ Registro ignorado: falta el campo {error}.")
            except (TypeError, ValueError) as error:
                print(f"⚠️ Registro ignorado: {error}")
        return len(self._vehiculos)


def crear_vehiculo_desde_diccionario(datos: dict) -> Vehiculo:
    """Reconstruye el objeto adecuado según el campo "tipo".

    Primero se crea el vehículo con el constructor (batería 100 % y 0 km)
    y después se restauran batería y kilómetros mediante los setters, que
    validan que los valores guardados sean posibles.

    Raises:
        KeyError: si falta algún campo obligatorio.
        ValueError: si el tipo es desconocido o algún valor es inválido.
    """
    tipo = datos["tipo"]
    if tipo == "coche":
        vehiculo = CocheElectrico(datos["matricula"], datos["modelo"],
                                  datos["capacidad_kwh"], datos["plazas"])
    elif tipo == "patinete":
        vehiculo = PatineteElectrico(datos["matricula"], datos["modelo"],
                                     datos["capacidad_kwh"],
                                     datos["velocidad_maxima_kmh"])
    else:
        raise ValueError(f"Tipo de vehículo desconocido: {tipo}")

    vehiculo.nivel_bateria = datos["nivel_bateria"]
    vehiculo.kilometros_totales = datos["kilometros_totales"]
    return vehiculo


"""
==========================================================================
REGISTRO DE INTERACCIÓN CON IA (PROMPT LOG)
==========================================================================
Herramienta consultada: Claude (Anthropic), modelo Claude Opus 5.5
Fecha y hora: 18/11/2026 - 19:55

1. Consulta exacta planteada:
   "INSTRUCCIÓN DEFINITIVA: EJECUTA Y DESARROLLA LA SDA 2 COMPLETA.
   [...] Desarrollar la SDA 2 completa siguiendo los requisitos
   oficiales del profesor."
   Texto íntegro en docs/02_prompt_desarrollo.txt (la consulta previa de
   auditoría, sin código, está en docs/01_prompt_auditoria.txt).

2. Síntesis de la respuesta recibida:
   Claude escribió todo el código de este archivo. La versión final
   contiene: clase Flota con agregar_vehiculo,
   simular_jornada, recargar_flota_critica, guardar_en_archivo,
   cargar_de_archivo y la función crear_vehiculo_desde_diccionario.

3. Aplicación crítica y modificaciones realizadas:
   [PENDIENTE: lo redactan Julio y Diego. Indicad qué habéis revisado,
   qué habéis entendido, qué habéis cambiado y por qué. No lo deis por
   completado hasta que sea verdad.]
==========================================================================
"""
