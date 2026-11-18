"""Pruebas automáticas de la persistencia JSON (apartado 5.1).

Ejecución:  python3 test_persistencia.py
Cada prueba trabaja en una carpeta temporal, así que NO toca el
flota.json real del proyecto.
"""

import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout

from simulador import Flota
from vehiculo import CocheElectrico, PatineteElectrico


class TestADiccionario(unittest.TestCase):
    """a_diccionario() en la superclase y las subclases."""

    def test_coche(self) -> None:
        coche = CocheElectrico("1234-BBB", "Urban-E", 40.0, plazas=4)
        self.assertEqual(coche.a_diccionario(), {
            "matricula": "1234-BBB",
            "modelo": "Urban-E",
            "capacidad_kwh": 40.0,
            "nivel_bateria": 100.0,
            "kilometros_totales": 0.0,
            "tipo": "coche",
            "plazas": 4,
        })

    def test_patinete(self) -> None:
        patinete = PatineteElectrico("PAT-99", "EcoKick", 0.5, 20.0)
        datos = patinete.a_diccionario()
        self.assertEqual(datos["tipo"], "patinete")
        self.assertEqual(datos["velocidad_maxima_kmh"], 20.0)
        self.assertEqual(datos["matricula"], "PAT-99")


class TestGuardarYCargar(unittest.TestCase):
    """guardar_en_archivo() y cargar_de_archivo()."""

    def setUp(self) -> None:
        self.carpeta = tempfile.TemporaryDirectory()
        self.ruta = os.path.join(self.carpeta.name, "flota.json")

    def tearDown(self) -> None:
        self.carpeta.cleanup()

    def cargar_en_silencio(self, flota: Flota, ruta: str) -> tuple[int, str]:
        """Carga la flota capturando lo que se imprime por pantalla."""
        salida = io.StringIO()
        with redirect_stdout(salida):
            cantidad = flota.cargar_de_archivo(ruta)
        return cantidad, salida.getvalue()

    def escribir(self, texto: str) -> None:
        with open(self.ruta, mode="w", encoding="utf-8") as archivo:
            archivo.write(texto)

    def test_fase1_y_fase2_del_profesor(self) -> None:
        """El coche conserva sus km y la batería gastada tras recargar."""
        flota = Flota()
        coche = CocheElectrico("1234-BBB", "Urban-E", 40.0)
        flota.agregar_vehiculo(coche)
        flota.agregar_vehiculo(PatineteElectrico("PAT-99", "EcoKick", 0.5))
        coche.conducir(20.0)  # 3 kWh = 7.5 % de 40
        flota.guardar_en_archivo(self.ruta)

        nueva = Flota()
        cantidad, _ = self.cargar_en_silencio(nueva, self.ruta)
        self.assertEqual(cantidad, 2)
        recuperado, patinete = nueva.obtener_vehiculos()
        self.assertIsInstance(recuperado, CocheElectrico)
        self.assertIsInstance(patinete, PatineteElectrico)
        self.assertEqual(recuperado.obtener_estado(), coche.obtener_estado())
        self.assertAlmostEqual(recuperado.nivel_bateria, 92.5)
        self.assertEqual(recuperado.kilometros_totales, 20.0)

    def test_formato_json_indentado(self) -> None:
        """El archivo es una lista JSON con sangría de 4 espacios."""
        flota = Flota()
        flota.agregar_vehiculo(CocheElectrico("1234-BBB", "Urban-E", 40.0))
        flota.guardar_en_archivo(self.ruta)
        with open(self.ruta, encoding="utf-8") as archivo:
            texto = archivo.read()
        self.assertTrue(texto.startswith("[\n    {"))
        self.assertIsInstance(json.loads(texto), list)

    def test_archivo_inexistente(self) -> None:
        """FileNotFoundError: avisa, devuelve 0 y no se cae."""
        flota = Flota()
        cantidad, salida = self.cargar_en_silencio(flota, self.ruta)
        self.assertEqual(cantidad, 0)
        self.assertIn("No existe", salida)
        self.assertEqual(flota.obtener_vehiculos(), [])

    def test_json_danado(self) -> None:
        """JSONDecodeError: avisa, devuelve 0 y conserva la flota actual."""
        self.escribir("[{ esto no es JSON ")
        flota = Flota()
        flota.agregar_vehiculo(CocheElectrico("1234-BBB", "Urban-E", 40.0))
        cantidad, salida = self.cargar_en_silencio(flota, self.ruta)
        self.assertEqual(cantidad, 0)
        self.assertIn("dañado", salida)
        self.assertEqual(len(flota.obtener_vehiculos()), 1)

    def test_json_vacio(self) -> None:
        """Un archivo vacío también se trata como JSON dañado."""
        self.escribir("")
        cantidad, salida = self.cargar_en_silencio(Flota(), self.ruta)
        self.assertEqual(cantidad, 0)
        self.assertIn("dañado", salida)

    def test_json_que_no_es_lista(self) -> None:
        """Un JSON válido pero que no es una lista se rechaza."""
        self.escribir('{"matricula": "1234-BBB"}')
        cantidad, salida = self.cargar_en_silencio(Flota(), self.ruta)
        self.assertEqual(cantidad, 0)
        self.assertIn("no contiene una lista", salida)

    def test_registros_invalidos_se_ignoran(self) -> None:
        """Batería imposible, tipo desconocido o campo ausente: se saltan."""
        datos = [
            {"tipo": "coche", "matricula": "OK-1", "modelo": "A",
             "capacidad_kwh": 40.0, "nivel_bateria": 50.0,
             "kilometros_totales": 10.0, "plazas": 5},
            {"tipo": "coche", "matricula": "MAL-1", "modelo": "B",
             "capacidad_kwh": 40.0, "nivel_bateria": 150.0,
             "kilometros_totales": 0.0, "plazas": 5},
            {"tipo": "camion", "matricula": "MAL-2"},
            {"tipo": "patinete", "matricula": "MAL-3"},
            {"tipo": "patinete", "matricula": "MAL-4", "modelo": "C",
             "capacidad_kwh": 0.5, "nivel_bateria": 50.0,
             "kilometros_totales": -3.0, "velocidad_maxima_kmh": 25.0},
            "texto suelto",
        ]
        self.escribir(json.dumps(datos))
        flota = Flota()
        cantidad, salida = self.cargar_en_silencio(flota, self.ruta)
        self.assertEqual(cantidad, 1)
        self.assertEqual(flota.obtener_vehiculos()[0].matricula, "OK-1")
        self.assertEqual(salida.count("Registro ignorado"), 5)

    def test_cargar_sustituye_flota_actual(self) -> None:
        """Una carga correcta reemplaza los vehículos que había."""
        guardada = Flota()
        guardada.agregar_vehiculo(PatineteElectrico("PAT-99", "EcoKick", 0.5))
        guardada.guardar_en_archivo(self.ruta)

        flota = Flota()
        flota.agregar_vehiculo(CocheElectrico("1234-BBB", "Urban-E", 40.0))
        cantidad, _ = self.cargar_en_silencio(flota, self.ruta)
        self.assertEqual(cantidad, 1)
        self.assertEqual(flota.obtener_vehiculos()[0].matricula, "PAT-99")

    def test_tildes_se_conservan(self) -> None:
        """Los modelos con tildes se guardan y recuperan bien."""
        flota = Flota()
        flota.agregar_vehiculo(CocheElectrico("1234-BBB", "Camión Ñ", 40.0))
        flota.guardar_en_archivo(self.ruta)
        nueva = Flota()
        self.cargar_en_silencio(nueva, self.ruta)
        self.assertEqual(nueva.obtener_vehiculos()[0].modelo, "Camión Ñ")


if __name__ == "__main__":
    unittest.main(verbosity=2)


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
   Claude escribió las pruebas automáticas (unittest) de este archivo,
   incluidos los escenarios que propone el profesor, y las ejecutó.

3. Aplicación crítica y modificaciones realizadas:
   [PENDIENTE: lo redactan Julio y Diego. Indicad qué habéis revisado,
   qué habéis entendido, qué habéis cambiado y por qué. No lo deis por
   completado hasta que sea verdad.]
==========================================================================
"""
