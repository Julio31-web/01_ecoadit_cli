"""Pruebas automáticas del menú de main.py (apartado 5.2).

Ejecución:  python3 test_main.py
Se simula lo que escribiría el usuario con unittest.mock (incluido en
Python) y se captura lo que el programa imprime. Se usa un flota.json
temporal, así que el archivo real del proyecto no se modifica.
"""

import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from unittest import mock

import main


class TestMenu(unittest.TestCase):
    """Recorre las cinco opciones del menú."""

    def setUp(self) -> None:
        self.carpeta = tempfile.TemporaryDirectory()
        self.ruta = os.path.join(self.carpeta.name, "flota.json")

    def tearDown(self) -> None:
        self.carpeta.cleanup()

    def ejecutar(self, entradas: list[str]) -> str:
        """Ejecuta main() con las entradas indicadas y devuelve la salida."""
        salida = io.StringIO()
        with mock.patch.object(main, "RUTA_DATOS", self.ruta), \
                mock.patch("builtins.input", side_effect=entradas), \
                redirect_stdout(salida):
            main.main()
        return salida.getvalue()

    def leer_json(self) -> list:
        with open(self.ruta, encoding="utf-8") as archivo:
            return json.load(archivo)

    def test_inicio_sin_archivo_y_salir(self) -> None:
        """Sin flota.json arranca vacío; la opción 5 crea el archivo."""
        salida = self.ejecutar(["5"])
        self.assertIn("recuperados", salida)
        self.assertIn("💾 Cambios guardados correctamente. ¡Hasta pronto!",
                      salida)
        self.assertEqual(self.leer_json(), [])

    def test_opcion_invalida(self) -> None:
        """Opciones fuera de rango o texto muestran el aviso oficial."""
        salida = self.ejecutar(["9", "hola", "", "5"])
        self.assertEqual(
            salida.count("❌ Opción inválida. Introduce un número del 1 al 5."),
            3,
        )

    def test_listar_flota_vacia(self) -> None:
        salida = self.ejecutar(["1", "5"])
        self.assertIn("La flota está vacía", salida)

    def test_registrar_listar_guardar_y_recuperar(self) -> None:
        """Ciclo completo: alta, listado, guardado y recuperación."""
        self.ejecutar([
            "2", "coche", "1234-bbb", "Urban-E", "40", "5",
            "2", "patinete", "PAT-01", "EcoKick", "0,5", "20",
            "1",
            "5",
        ])
        datos = self.leer_json()
        self.assertEqual([d["matricula"] for d in datos],
                         ["1234-BBB", "PAT-01"])
        self.assertEqual(datos[1]["capacidad_kwh"], 0.5)

        salida = self.ejecutar(["1", "5"])
        self.assertIn("Vehículos recuperados", salida)
        self.assertIn(": 2", salida)
        self.assertIn("[1234-BBB] Urban-E | Batería: 100.0%", salida)
        self.assertIn("Vel. Máx: 20.0 km/h", salida)

    def test_registro_con_errores(self) -> None:
        """Tipo, número, velocidad y matrícula duplicada: no se registran."""
        salida = self.ejecutar([
            "2", "moto",
            "2", "coche", "A-1", "X", "mucha",
            "2", "patinete", "P-1", "Y", "0.5", "45",
            "2", "coche", "", "X",
            "2", "coche", "A-2", "X", "40", "5",
            "2", "coche", "A-2", "Z", "50", "4",
            "5",
        ])
        self.assertIn("Tipo no válido", salida)
        self.assertIn("Debes introducir un número válido", salida)
        self.assertIn("La velocidad máxima legal en ciudad es 25 km/h.",
                      salida)
        self.assertIn("no pueden estar vacíos", salida)
        self.assertIn("Ya existe un vehículo con matrícula A-2", salida)
        self.assertEqual(len(self.leer_json()), 1)

    def test_simular_y_recargar(self) -> None:
        """Opciones 3 y 4 con datos válidos e inválidos."""
        salida = self.ejecutar([
            "2", "patinete", "PAT-01", "EcoKick", "0.5", "25",
            "3", "abc",
            "3", "-5",
            "3", "20",
            "4",
            "3", "20",
            "5",
        ])
        self.assertIn("Debes introducir un número", salida)
        self.assertIn("debe ser un número positivo", salida)
        self.assertIn("Viajes completados: 1", salida)
        self.assertIn("Vehículos recargados: 1", salida)
        datos = self.leer_json()
        self.assertEqual(datos[0]["kilometros_totales"], 40.0)

    def test_salir_sin_opcion_5_no_guarda(self) -> None:
        """Los cambios solo se guardan con la opción 5."""
        with self.assertRaises(StopIteration):
            # Se acaban las entradas antes de elegir 5 (simula cerrar).
            self.ejecutar(["2", "coche", "1234-BBB", "Urban-E", "40", "5"])
        self.assertFalse(os.path.exists(self.ruta))


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
