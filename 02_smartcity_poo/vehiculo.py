"""Módulo vehiculo: modelo de los vehículos eléctricos de la Smart City.

Contiene la superclase Vehiculo y sus subclases CocheElectrico y
PatineteElectrico. Solo incluye lógica de negocio:
no pide datos por teclado ni escribe en pantalla.
"""

# Constantes de la simulación (material del profesor).
# Cambiarlas aquí afecta a todo el programa (útil en el Refactor en Caliente).
CONSUMO_COCHE_KWH_KM: float = 0.15
CONSUMO_PATINETE_KWH_KM: float = 0.02
VELOCIDAD_MAXIMA_PATINETE_KMH: float = 25.0


class Vehiculo:
    """Molde que representa un vehículo eléctrico en el simulador municipal."""

    def __init__(self, matricula: str, modelo: str,
                 capacidad_kwh: float) -> None:
        """Crea un vehículo con la batería llena y el odómetro a cero.

        Args:
            matricula: identificador del vehículo.
            modelo: nombre comercial del modelo.
            capacidad_kwh: capacidad de la batería en kWh.

        Raises:
            ValueError: si la capacidad de la batería no es mayor que 0.
        """
        # Sin esta comprobación, conducir() y recargar() dividirían entre 0.
        if capacidad_kwh <= 0:
            raise ValueError(
                f"Capacidad de batería inválida: {capacidad_kwh} kWh. "
                "Debe ser mayor que 0."
            )
        # Guardamos los datos recibidos dentro del propio objeto usando self
        self.matricula: str = matricula
        self.modelo: str = modelo
        self.capacidad_kwh: float = capacidad_kwh
        self._nivel_bateria: float = 100.0  # Atributo protegido (%)
        self._kilometros_totales: float = 0.0  # Atributo protegido (km)

    # ------------------------------------------------------------------
    # Encapsulamiento: propiedades con validación (apartado 3.2)
    # ------------------------------------------------------------------
    @property
    def nivel_bateria(self) -> float:
        """Devuelve el porcentaje de batería (de 0.0 a 100.0)."""
        return self._nivel_bateria

    @nivel_bateria.setter
    def nivel_bateria(self, nuevo_nivel: float) -> None:
        """Asigna el nivel de batería solo si está entre 0 y 100.

        Raises:
            ValueError: si el nivel es negativo o mayor que 100.
        """
        if nuevo_nivel < 0.0 or nuevo_nivel > 100.0:
            raise ValueError(
                f"Nivel de batería inválido: {nuevo_nivel}%. "
                "Debe estar entre 0 y 100."
            )
        self._nivel_bateria = nuevo_nivel

    @property
    def kilometros_totales(self) -> float:
        """Devuelve los kilómetros acumulados (odómetro)."""
        return self._kilometros_totales

    @kilometros_totales.setter
    def kilometros_totales(self, nuevos_km: float) -> None:
        """Asigna los kilómetros solo si no disminuyen.

        Como el odómetro empieza en 0.0 y nunca puede bajar, esta regla
        también impide que haya kilómetros negativos.

        Raises:
            ValueError: si los nuevos kilómetros son menores que los actuales.
        """
        if nuevos_km < self._kilometros_totales:
            raise ValueError(
                "Los kilómetros no pueden disminuir (fraude de odómetro)."
            )
        self._kilometros_totales = nuevos_km

    # ------------------------------------------------------------------
    # Comportamiento
    # ------------------------------------------------------------------
    def conducir(self, distancia_km: float) -> bool:
        """Simula un trayecto. Consume 0.15 kWh por cada km recorrido.

        Args:
            distancia_km: kilómetros que se quieren recorrer.

        Returns:
            True si el trayecto se realiza; False si la batería no alcanza
            (en ese caso el vehículo no se mueve y su estado no cambia).

        Raises:
            ValueError: si la distancia es negativa.
        """
        if distancia_km < 0:
            raise ValueError(
                f"Distancia inválida: {distancia_km} km. "
                "No puede ser negativa."
            )
        energia_necesaria = distancia_km * CONSUMO_COCHE_KWH_KM
        porcentaje_consumido = (energia_necesaria / self.capacidad_kwh) * 100.0

        # Comprobamos si la batería actual cubre el consumo
        if self.nivel_bateria >= porcentaje_consumido:
            # max() evita valores como -0.0000001 por el redondeo de los float
            self.nivel_bateria = max(
                self.nivel_bateria - porcentaje_consumido, 0.0
            )
            self.kilometros_totales = self.kilometros_totales + distancia_km
            return True  # Trayecto realizado
        return False  # Batería insuficiente: no se mueve

    def recargar(self, energia_kwh: float) -> float:
        """Añade energía a la batería sin superar el 100 %.

        Args:
            energia_kwh: energía que se entrega al vehículo, en kWh.

        Returns:
            El nivel de batería final (%).

        Raises:
            ValueError: si la energía es negativa.
        """
        if energia_kwh < 0:
            raise ValueError(
                f"Energía inválida: {energia_kwh} kWh. "
                "No puede ser negativa."
            )
        porcentaje_cargado = (energia_kwh / self.capacidad_kwh) * 100.0
        # min() actúa de "freno": nunca se pasa de 100.0
        self.nivel_bateria = min(
            self.nivel_bateria + porcentaje_cargado, 100.0
        )
        return self.nivel_bateria

    def obtener_estado(self) -> str:
        """Devuelve una ficha legible con la telemetría del vehículo."""
        return (
            f"[{self.matricula}] {self.modelo} | "
            f"Batería: {self.nivel_bateria:.1f}% | "
            f"Total: {self.kilometros_totales} km"
        )

    def a_diccionario(self) -> dict:
        """Convierte el vehículo en un diccionario apto para JSON."""
        return {
            "matricula": self.matricula,
            "modelo": self.modelo,
            "capacidad_kwh": self.capacidad_kwh,
            "nivel_bateria": self.nivel_bateria,
            "kilometros_totales": self.kilometros_totales,
        }


class CocheElectrico(Vehiculo):
    """Subclase que representa un automóvil eléctrico de pasajeros.

    Hereda conducir() de Vehiculo, con un consumo de 0.15 kWh/km.
    """

    def __init__(self, matricula: str, modelo: str, capacidad_kwh: float,
                 plazas: int = 5) -> None:
        """Crea un coche eléctrico.

        Raises:
            ValueError: si la capacidad no es positiva o si hay menos
                de 1 plaza.
        """
        # 1. Delegamos en la superclase para inicializar los atributos comunes
        super().__init__(matricula, modelo, capacidad_kwh)
        # 2. Inicializamos el atributo exclusivo de esta subclase
        if plazas < 1:
            raise ValueError(
                f"Número de plazas inválido: {plazas}. Debe ser al menos 1."
            )
        self.plazas: int = plazas

    def obtener_estado(self) -> str:
        """Sobrescribe obtener_estado() añadiendo las plazas del vehículo."""
        estado_base = super().obtener_estado()
        return f"{estado_base} | Plazas: {self.plazas}"

    def a_diccionario(self) -> dict:
        """Amplía el diccionario base con el tipo y las plazas."""
        datos = super().a_diccionario()
        datos["tipo"] = "coche"
        datos["plazas"] = self.plazas
        return datos


class PatineteElectrico(Vehiculo):
    """Subclase que representa un patinete eléctrico urbano."""

    def __init__(self, matricula: str, modelo: str, capacidad_kwh: float,
                 velocidad_maxima_kmh: float = 25.0) -> None:
        """Crea un patinete eléctrico.

        Raises:
            ValueError: si la capacidad no es positiva, o si la velocidad
                máxima no es positiva o supera el límite legal de 25 km/h.
        """
        super().__init__(matricula, modelo, capacidad_kwh)
        # Esta comprobación impide configurar un patinete a más de 25 km/h
        if velocidad_maxima_kmh > VELOCIDAD_MAXIMA_PATINETE_KMH:
            raise ValueError("La velocidad máxima legal en ciudad es 25 km/h.")
        if velocidad_maxima_kmh <= 0:
            raise ValueError(
                f"Velocidad máxima inválida: {velocidad_maxima_kmh} km/h. "
                "Debe ser mayor que 0."
            )
        self.velocidad_maxima_kmh: float = velocidad_maxima_kmh

    def conducir(self, distancia_km: float) -> bool:
        """Sobrescribe conducir(): el patinete consume 0.02 kWh por km.

        Returns:
            True si el trayecto se realiza; False si la batería no alcanza.

        Raises:
            ValueError: si la distancia es negativa.
        """
        if distancia_km < 0:
            raise ValueError(
                f"Distancia inválida: {distancia_km} km. "
                "No puede ser negativa."
            )
        energia_necesaria = distancia_km * CONSUMO_PATINETE_KWH_KM
        porcentaje_consumido = (energia_necesaria / self.capacidad_kwh) * 100.0

        if self.nivel_bateria >= porcentaje_consumido:
            self.nivel_bateria = max(
                self.nivel_bateria - porcentaje_consumido, 0.0
            )
            self.kilometros_totales = self.kilometros_totales + distancia_km
            return True
        return False

    def obtener_estado(self) -> str:
        """Sobrescribe obtener_estado() añadiendo la velocidad máxima."""
        estado_base = super().obtener_estado()
        return f"{estado_base} | Vel. Máx: {self.velocidad_maxima_kmh} km/h"

    def a_diccionario(self) -> dict:
        """Amplía el diccionario base con el tipo y la velocidad máxima."""
        datos = super().a_diccionario()
        datos["tipo"] = "patinete"
        datos["velocidad_maxima_kmh"] = self.velocidad_maxima_kmh
        return datos



