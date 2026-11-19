"""Pruebas automáticas de simulador.py: clase Flota y polimorfismo (4.2).

Ejecución:  python3 test_simulador.py
"""

import unittest

from simulador import Flota
from vehiculo import CocheElectrico, PatineteElectrico


class TestFlota(unittest.TestCase):
    """Escenario del profesor: dos coches y dos patinetes."""

    def setUp(self) -> None:
        self.flota = Flota()
        self.flota.agregar_vehiculo(
            CocheElectrico("1111-AAA", "Urban-E", 50.0))
        self.flota.agregar_vehiculo(CocheElectrico("2222-BBB", "EcoVan", 75.0,
                                                   plazas=7))
        self.flota.agregar_vehiculo(
            PatineteElectrico("PAT-01", "EcoKick", 0.5))
        self.flota.agregar_vehiculo(PatineteElectrico("PAT-02", "CityRoll",
                                                      0.5, 20.0))

    def test_registro_lista_heterogenea(self) -> None:
        """La flota guarda coches y patinetes en la misma lista."""
        vehiculos = self.flota.obtener_vehiculos()
        self.assertEqual(len(vehiculos), 4)
        self.assertIsInstance(vehiculos[0], CocheElectrico)
        self.assertIsInstance(vehiculos[2], PatineteElectrico)

    def test_jornada_polimorfica_20_km(self) -> None:
        """Mismo conducir(20.0), consumo distinto según el tipo."""
        resultado = self.flota.simular_jornada(20.0)
        self.assertEqual(resultado, {"exitosos": 4, "fallidos": 0})
        coche, furgo, pat1, pat2 = self.flota.obtener_vehiculos()
        self.assertAlmostEqual(coche.nivel_bateria, 94.0)  # 3 kWh de 50
        self.assertAlmostEqual(furgo.nivel_bateria, 96.0)  # 3 kWh de 75
        self.assertAlmostEqual(pat1.nivel_bateria, 20.0)   # 0.4 kWh de 0.5
        self.assertAlmostEqual(pat2.nivel_bateria, 20.0)
        for vehiculo in self.flota.obtener_vehiculos():
            self.assertEqual(vehiculo.kilometros_totales, 20.0)

    def test_jornada_con_fallos(self) -> None:
        """2.ª jornada de 20 km: fallan los patinetes (están al 20 %)."""
        self.flota.simular_jornada(20.0)
        resultado = self.flota.simular_jornada(20.0)
        self.assertEqual(resultado, {"exitosos": 2, "fallidos": 2})
        pat1 = self.flota.obtener_vehiculos()[2]
        self.assertEqual(pat1.kilometros_totales, 20.0)  # No se movió

    def test_recarga_critica_escenario_profesor(self) -> None:
        """umbral 25 % y 10 kWh: se recargan solo los dos patinetes."""
        self.flota.simular_jornada(20.0)
        recargados = self.flota.recargar_flota_critica(umbral_bateria=25.0,
                                                       kwh_carga=10.0)
        self.assertEqual(recargados, 2)
        coche, _, pat1, pat2 = self.flota.obtener_vehiculos()
        self.assertEqual(pat1.nivel_bateria, 100.0)
        self.assertEqual(pat2.nivel_bateria, 100.0)
        self.assertAlmostEqual(coche.nivel_bateria, 94.0)

    def test_recarga_critica_valores_por_defecto(self) -> None:
        """Por defecto: umbral 20 % (incluido) y 15 kWh."""
        self.flota.simular_jornada(20.0)  # Patinetes justo al 20 %
        self.assertEqual(self.flota.recargar_flota_critica(), 2)

    def test_sin_vehiculos_criticos(self) -> None:
        """Si nadie está bajo el umbral, no se recarga ninguno."""
        self.assertEqual(self.flota.recargar_flota_critica(), 0)

    def test_matricula_duplicada(self) -> None:
        """Registrar otra vez PAT-01 lanza ValueError y no se añade."""
        with self.assertRaises(ValueError) as contexto:
            self.flota.agregar_vehiculo(
                PatineteElectrico("PAT-01", "Clon", 0.5)
            )
        self.assertEqual(str(contexto.exception),
                         "Ya existe un vehículo con matrícula PAT-01")
        self.assertEqual(len(self.flota.obtener_vehiculos()), 4)

    def test_lista_protegida(self) -> None:
        """Modificar la copia devuelta no altera la flota."""
        copia = self.flota.obtener_vehiculos()
        copia.clear()
        self.assertEqual(len(self.flota.obtener_vehiculos()), 4)

    def test_flota_vacia(self) -> None:
        """Una flota vacía simula sin errores."""
        vacia = Flota()
        self.assertEqual(vacia.simular_jornada(10.0),
                         {"exitosos": 0, "fallidos": 0})
        self.assertEqual(vacia.recargar_flota_critica(), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)


