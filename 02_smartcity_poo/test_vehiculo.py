"""Pruebas automáticas de vehiculo.py (apartados 3.1, 3.2 y 4.1).

Ejecución:  python3 test_vehiculo.py
Incluyen los escenarios del profesor (Pruebas 1 a 5 y comparativa de
consumo) convertidos en comprobaciones automáticas con unittest.
"""

import unittest

from vehiculo import CocheElectrico, PatineteElectrico, Vehiculo


class TestVehiculoBase(unittest.TestCase):
    """3.1: constructor, conducir() y obtener_estado()."""

    def setUp(self) -> None:
        self.coche1 = Vehiculo("1234-BBB", "Urban-E", 40.0)
        self.coche2 = Vehiculo("5678-FFF", "EcoVan", 75.0)

    def test_estado_inicial(self) -> None:
        """Al crearse: batería 100.0 % y 0.0 km."""
        self.assertEqual(self.coche1.matricula, "1234-BBB")
        self.assertEqual(self.coche1.modelo, "Urban-E")
        self.assertEqual(self.coche1.capacidad_kwh, 40.0)
        self.assertEqual(self.coche1.nivel_bateria, 100.0)
        self.assertEqual(self.coche1.kilometros_totales, 0.0)

    def test_prueba1_consumo_e_independencia(self) -> None:
        """Prueba 1: 100 km = 15 kWh (37.5 % de 40); coche2 no cambia."""
        self.assertTrue(self.coche1.conducir(100.0))
        self.assertAlmostEqual(self.coche1.nivel_bateria, 62.5)
        self.assertEqual(self.coche1.kilometros_totales, 100.0)
        self.assertEqual(self.coche2.nivel_bateria, 100.0)
        self.assertEqual(self.coche2.kilometros_totales, 0.0)

    def test_traza_fase_cero(self) -> None:
        """Pasos 1 y 2 de la traza del profesor (50 kWh, 100 km -> 70 %)."""
        sedan = Vehiculo("5678-ECO", "Sedan", 50.0)
        sedan.conducir(100.0)
        self.assertAlmostEqual(sedan.nivel_bateria, 70.0)
        self.assertEqual(sedan.kilometros_totales, 100.0)

    def test_bateria_insuficiente_no_se_mueve(self) -> None:
        """300 km necesitan 45 kWh > 40 kWh: devuelve False y nada cambia."""
        self.assertFalse(self.coche1.conducir(300.0))
        self.assertEqual(self.coche1.nivel_bateria, 100.0)
        self.assertEqual(self.coche1.kilometros_totales, 0.0)

    def test_gastar_bateria_exacta(self) -> None:
        """Se puede gastar justo toda la batería sin errores de redondeo."""
        exacto = Vehiculo("0000-AAA", "Test", 15.0)  # 100 km = 15 kWh
        self.assertTrue(exacto.conducir(100.0))
        self.assertEqual(exacto.nivel_bateria, 0.0)
        self.assertFalse(exacto.conducir(1.0))

    def test_distancia_negativa(self) -> None:
        """Una distancia negativa lanza ValueError."""
        with self.assertRaises(ValueError):
            self.coche1.conducir(-10.0)

    def test_capacidad_invalida(self) -> None:
        """Capacidad 0 o negativa lanza ValueError."""
        with self.assertRaises(ValueError):
            Vehiculo("9999-ZZZ", "Roto", 0.0)
        with self.assertRaises(ValueError):
            Vehiculo("9999-ZZZ", "Roto", -5.0)

    def test_formato_obtener_estado(self) -> None:
        """Formato: [matricula] modelo | Batería: X.X% | Total: Y km."""
        self.assertEqual(
            self.coche1.obtener_estado(),
            "[1234-BBB] Urban-E | Batería: 100.0% | Total: 0.0 km",
        )


class TestRecarga(unittest.TestCase):
    """3.1: recargar()."""

    def setUp(self) -> None:
        self.coche1 = Vehiculo("1234-BBB", "Urban-E", 40.0)
        self.coche1.conducir(100.0)  # Queda al 62.5 %

    def test_prueba2_recarga_parcial(self) -> None:
        """Prueba 2: 10 kWh son +25 % de 40 kWh -> 87.5 %."""
        resultado = self.coche1.recargar(10.0)
        self.assertAlmostEqual(resultado, 87.5)
        self.assertAlmostEqual(self.coche1.nivel_bateria, 87.5)

    def test_prueba3_freno_en_100(self) -> None:
        """Prueba 3: una sobrecarga se queda exactamente en 100.0 %."""
        resultado = self.coche1.recargar(100.0)
        self.assertEqual(resultado, 100.0)
        self.assertEqual(self.coche1.nivel_bateria, 100.0)

    def test_recarga_no_cambia_kilometros(self) -> None:
        """Recargar no modifica el odómetro."""
        self.coche1.recargar(5.0)
        self.assertEqual(self.coche1.kilometros_totales, 100.0)

    def test_recarga_negativa(self) -> None:
        """Una energía negativa lanza ValueError."""
        with self.assertRaises(ValueError):
            self.coche1.recargar(-5.0)


class TestEncapsulamientoBateria(unittest.TestCase):
    """3.2: propiedad nivel_bateria con setter defensivo."""

    def setUp(self) -> None:
        self.coche1 = Vehiculo("1234-BBB", "Urban-E", 40.0)

    def test_atributo_protegido(self) -> None:
        """El dato real se guarda en _nivel_bateria."""
        self.assertEqual(self.coche1._nivel_bateria, 100.0)

    def test_prueba4_bateria_negativa(self) -> None:
        """Prueba 4: asignar -25.0 lanza ValueError y no cambia el valor."""
        with self.assertRaises(ValueError) as contexto:
            self.coche1.nivel_bateria = -25.0
        self.assertIn("Nivel de batería inválido", str(contexto.exception))
        self.assertEqual(self.coche1.nivel_bateria, 100.0)

    def test_bateria_mayor_que_100(self) -> None:
        """Asignar 150.0 lanza ValueError."""
        with self.assertRaises(ValueError):
            self.coche1.nivel_bateria = 150.0

    def test_limites_validos(self) -> None:
        """0.0 y 100.0 son valores permitidos."""
        self.coche1.nivel_bateria = 0.0
        self.assertEqual(self.coche1.nivel_bateria, 0.0)
        self.coche1.nivel_bateria = 100.0
        self.assertEqual(self.coche1.nivel_bateria, 100.0)


class TestEncapsulamientoOdometro(unittest.TestCase):
    """3.2 (reto autónomo): propiedad kilometros_totales."""

    def setUp(self) -> None:
        self.coche1 = Vehiculo("1234-BBB", "Urban-E", 40.0)
        self.coche1.conducir(100.0)

    def test_atributo_protegido(self) -> None:
        """El dato real se guarda en _kilometros_totales."""
        self.assertEqual(self.coche1._kilometros_totales, 100.0)

    def test_prueba5_fraude_odometro(self) -> None:
        """Prueba 5: bajar de 100 km a 10 km lanza ValueError."""
        with self.assertRaises(ValueError) as contexto:
            self.coche1.kilometros_totales = 10.0
        self.assertIn("fraude de odómetro", str(contexto.exception))
        self.assertEqual(self.coche1.kilometros_totales, 100.0)

    def test_kilometros_negativos(self) -> None:
        """Un kilometraje negativo también se bloquea."""
        nuevo = Vehiculo("2222-CCC", "City", 40.0)
        with self.assertRaises(ValueError):
            nuevo.kilometros_totales = -1.0

    def test_aumentar_kilometros(self) -> None:
        """Aumentar el odómetro sí está permitido."""
        self.coche1.kilometros_totales = 150.0
        self.assertEqual(self.coche1.kilometros_totales, 150.0)


class TestHerencia(unittest.TestCase):
    """4.1: CocheElectrico y PatineteElectrico."""

    def setUp(self) -> None:
        self.coche = CocheElectrico("3456-LMN", "Urban-SUV", 50.0, plazas=5)
        self.patinete = PatineteElectrico("PAT-001", "EcoKick", 0.5,
                                          velocidad_maxima_kmh=25.0)

    def test_son_vehiculos(self) -> None:
        """Ambas subclases heredan de Vehiculo."""
        self.assertIsInstance(self.coche, Vehiculo)
        self.assertIsInstance(self.patinete, Vehiculo)
        self.assertTrue(issubclass(CocheElectrico, Vehiculo))
        self.assertTrue(issubclass(PatineteElectrico, Vehiculo))

    def test_super_inicializa_atributos_comunes(self) -> None:
        """super().__init__() deja la batería al 100 % y 0 km."""
        for vehiculo in (self.coche, self.patinete):
            self.assertEqual(vehiculo.nivel_bateria, 100.0)
            self.assertEqual(vehiculo.kilometros_totales, 0.0)
        self.assertEqual(self.coche.matricula, "3456-LMN")
        self.assertEqual(self.patinete.capacidad_kwh, 0.5)

    def test_atributos_propios_y_valores_por_defecto(self) -> None:
        """Plazas 5 y velocidad 25.0 por defecto."""
        self.assertEqual(CocheElectrico("A", "B", 40.0).plazas, 5)
        self.assertEqual(
            PatineteElectrico("C", "D", 0.5).velocidad_maxima_kmh, 25.0
        )

    def test_comparativa_consumo_10_km(self) -> None:
        """Coche: 1.5 kWh (3 % de 50). Patinete: 0.2 kWh (40 % de 0.5)."""
        self.assertTrue(self.coche.conducir(10.0))
        self.assertTrue(self.patinete.conducir(10.0))
        self.assertAlmostEqual(self.coche.nivel_bateria, 97.0)
        self.assertAlmostEqual(self.patinete.nivel_bateria, 60.0)
        self.assertEqual(self.patinete.kilometros_totales, 10.0)
        energia_coche = 50.0 * (100.0 - self.coche.nivel_bateria) / 100.0
        energia_patinete = 0.5 * (100.0 - self.patinete.nivel_bateria) / 100.0
        self.assertGreater(energia_coche, energia_patinete)

    def test_patinete_bateria_insuficiente(self) -> None:
        """30 km necesitan 0.6 kWh > 0.5 kWh: no se mueve."""
        self.assertFalse(self.patinete.conducir(30.0))
        self.assertEqual(self.patinete.nivel_bateria, 100.0)

    def test_patinete_trucado(self) -> None:
        """Un patinete a 45 km/h lanza ValueError."""
        with self.assertRaises(ValueError) as contexto:
            PatineteElectrico("PAT-FAST", "SpeedMaster", 1.0,
                              velocidad_maxima_kmh=45.0)
        self.assertEqual(str(contexto.exception),
                         "La velocidad máxima legal en ciudad es 25 km/h.")

    def test_valores_imposibles_subclases(self) -> None:
        """0 plazas o velocidad 0 lanzan ValueError."""
        with self.assertRaises(ValueError):
            CocheElectrico("A", "B", 40.0, plazas=0)
        with self.assertRaises(ValueError):
            PatineteElectrico("C", "D", 0.5, velocidad_maxima_kmh=0.0)

    def test_sobrescritura_obtener_estado(self) -> None:
        """Cada subclase amplía la ficha base con su dato propio."""
        self.assertEqual(
            self.coche.obtener_estado(),
            "[3456-LMN] Urban-SUV | Batería: 100.0% | Total: 0.0 km"
            " | Plazas: 5",
        )
        self.assertEqual(
            self.patinete.obtener_estado(),
            "[PAT-001] EcoKick | Batería: 100.0% | Total: 0.0 km"
            " | Vel. Máx: 25.0 km/h",
        )

    def test_setters_heredados(self) -> None:
        """Las subclases heredan también las validaciones de los setters."""
        with self.assertRaises(ValueError):
            self.patinete.nivel_bateria = -1.0


if __name__ == "__main__":
    unittest.main(verbosity=2)



