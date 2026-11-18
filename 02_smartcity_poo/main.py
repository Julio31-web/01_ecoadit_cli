"""SmartCity Mobility: interfaz de consola (CLI) del simulador de flota.

Este módulo SOLO se ocupa de la interacción con el usuario: muestra el
menú, pide datos, captura excepciones y enseña resultados. La lógica de
los vehículos está en vehiculo.py y la de la flota en simulador.py.
"""

from simulador import Flota
from vehiculo import CocheElectrico, PatineteElectrico

RUTA_DATOS: str = "flota.json"


def mostrar_menu() -> None:
    """Imprime el encabezado y las cinco opciones del menú."""
    print("\n" + "=" * 50)
    print(" ⚡ SMARTCITY MOBILITY - GESTIÓN DE FLOTA ⚡")
    print("=" * 50)
    print("1. Listar estado de la flota")
    print("2. Registrar nuevo vehículo")
    print("3. Simular jornada urbana")
    print("4. Recargar vehículos con batería crítica")
    print("5. Guardar estado y salir")


def leer_float(mensaje: str) -> float:
    """Pide un número decimal. Acepta coma o punto (40,5 o 40.5).

    Raises:
        ValueError: si el texto introducido no es un número.
    """
    return float(input(mensaje).strip().replace(",", "."))


def listar_estado(flota: Flota) -> None:
    """Opción 1: muestra la ficha de cada vehículo."""
    vehiculos = flota.obtener_vehiculos()
    if not vehiculos:
        print("ℹ️ La flota está vacía. Registra un vehículo con la opción 2.")
        return
    print(f"\n--- Estado de la flota ({len(vehiculos)} vehículos) ---")
    for vehiculo in vehiculos:
        print(vehiculo.obtener_estado())  # Polimorfismo


def registrar_vehiculo(flota: Flota) -> None:
    """Opción 2: pide los datos de un coche o patinete y lo registra."""
    tipo = input("Tipo de vehículo (coche/patinete): ").strip().lower()
    if tipo not in ("coche", "patinete"):
        print("❌ Tipo no válido. Escribe 'coche' o 'patinete'.")
        return

    matricula = input("Matrícula: ").strip().upper()
    modelo = input("Modelo: ").strip()
    if not matricula or not modelo:
        print("❌ La matrícula y el modelo no pueden estar vacíos.")
        return

    # 1) Lectura de números: int() y float() lanzan ValueError si el texto
    #    no es un número.
    try:
        capacidad = leer_float("Capacidad de la batería (kWh): ")
        if tipo == "coche":
            dato_extra = int(input("Número de plazas: ").strip())
        else:
            dato_extra = leer_float("Velocidad máxima (km/h): ")
    except ValueError:
        print("❌ Debes introducir un número válido.")
        return

    # 2) Creación y registro: las clases lanzan ValueError si los datos son
    #    imposibles (capacidad, plazas, más de 25 km/h, matrícula repetida).
    try:
        if tipo == "coche":
            vehiculo = CocheElectrico(matricula, modelo, capacidad, dato_extra)
        else:
            vehiculo = PatineteElectrico(matricula, modelo, capacidad,
                                         dato_extra)
        flota.agregar_vehiculo(vehiculo)
    except ValueError as error:
        print(f"❌ No se pudo registrar el vehículo: {error}")
        return

    print(f"✅ Vehículo registrado: {vehiculo.obtener_estado()}")


def simular_jornada(flota: Flota) -> None:
    """Opción 3: todos los vehículos intentan recorrer la misma distancia."""
    try:
        distancia = leer_float("Distancia de la jornada (km): ")
    except ValueError:
        print("❌ Debes introducir un número.")
        return
    if distancia <= 0:
        print("❌ La distancia debe ser un número positivo.")
        return

    resultado = flota.simular_jornada(distancia)
    print(f"🚦 Viajes completados: {resultado['exitosos']}")
    print(f"🪫 Viajes fallidos por batería insuficiente: "
          f"{resultado['fallidos']}")


def recargar_criticos(flota: Flota) -> None:
    """Opción 4: recarga los vehículos con batería crítica."""
    recargados = flota.recargar_flota_critica()
    print(f"🔌 Vehículos recargados: {recargados}")


def main() -> None:
    """Carga la flota guardada y ejecuta el bucle del menú."""
    flota = Flota()
    recuperados = flota.cargar_de_archivo(RUTA_DATOS)
    print(f"📂 Vehículos recuperados de '{RUTA_DATOS}': {recuperados}")

    while True:
        mostrar_menu()
        opcion = input("\nSelecciona una opción (1-5): ").strip()

        if opcion == "1":
            listar_estado(flota)
        elif opcion == "2":
            registrar_vehiculo(flota)
        elif opcion == "3":
            simular_jornada(flota)
        elif opcion == "4":
            recargar_criticos(flota)
        elif opcion == "5":
            flota.guardar_en_archivo(RUTA_DATOS)
            print("💾 Cambios guardados correctamente. ¡Hasta pronto!")
            break
        else:
            print("❌ Opción inválida. Introduce un número del 1 al 5.")


if __name__ == "__main__":
    main()


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
   Claude escribió el archivo completo: menú de consola con las cinco
   opciones, lectura defensiva de datos y carga/guardado de flota.json.

3. Aplicación crítica y modificaciones realizadas:
   [PENDIENTE: lo redactan Julio y Diego. Indicad qué habéis revisado,
   qué habéis entendido, qué habéis cambiado y por qué. No lo deis por
   completado hasta que sea verdad.]
==========================================================================
"""
