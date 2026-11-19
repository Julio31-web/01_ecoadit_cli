
from calculadora import estimar_consumo_wh, calcular_huella_co2

print("EcoAudit CLI")
print("    Version de Auditoria Segura")

# =====================================================================
# EcoAudit CLI - Módulo Principal
# =====================================================================

while True:
    print("\n=========================================")
    print(" 🌿 ECOAUDIT CLI - MENÚ PRINCIPAL 🌿 ")
    print("=========================================")
    print("1. Realizar nueva auditoría")
    print("2. Consultar histórico")
    print("3. Salir")

    entrada = input("\nSeleccione una opción (1-3): ").strip()

    # Validación de la opción introducida
    try:
        opcion = int(entrada)
    except ValueError:
        print("⚠️ Error: Debe introducir un número entero.")
        continue

    if opcion == 1:
        print("\n[OPCIÓN 1] Iniciando proceso de auditoría...")

        entrada_iteraciones = input(
            "Introduzca el número de iteraciones: "
        ).strip()

        try:
            iteraciones = int(entrada_iteraciones)
        except ValueError:
            print("⚠️ Error: Debe introducir un número entero.")
            continue

        if iteraciones > 0:
            print(f"Número de iteraciones válido: {iteraciones}")

            proceso = input("Nombre del equipo/proceso: ").strip()

            try:
                potencia = float(
                    input("Potencia consumida en Vatios (W): ")
                )
                horas = float(
                    input("Horas de uso diario: ")
                )
            except ValueError:
                print("⚠️ Error: Introduzca valores numéricos válidos.")
                continue

            # Cálculo original del consumo total y la huella de carbono
            consumo = estimar_consumo_wh(
                potencia, horas, iteraciones
            )
            huella = calcular_huella_co2(consumo)

            # =========================================================
            # SIMULACIÓN ITERATIVA PASO A PASO
            # (PARA INSPECCIÓN EN DEPURADOR)
            # =========================================================

            print("\nIniciando simulación ciclo a ciclo...")

            consumo_ciclo = estimar_consumo_wh(
                potencia, horas, 1
            )  # Consumo de un solo ciclo

            consumo_acumulado = 0.0
            ciclo = 1

            while ciclo <= iteraciones:
                consumo_acumulado = consumo_acumulado + consumo_ciclo  # <-- PON AQUÍ EL PUNTO ROJO

                print(
                    f" [Ciclo {ciclo}] Consumo acumulado parcial: "
                    f"{consumo_acumulado:.2f} Wh"
                )

                ciclo = ciclo + 1

            # =========================================================
            # RESULTADOS FINALES
            # =========================================================

            print(f"\n✅ Resultados calculados para '{proceso}':")
            print(f"   • Consumo total: {consumo:.2f} Wh")
            print(
                f"   • Huella de carbono estimada: "
                f"{huella:.4f} g CO2"
            )

            # Guardado persistente en el archivo CSV
            with open(
                "auditorias.csv",
                mode="a",
                encoding="utf-8"
            ) as archivo:
                archivo.write(
                    f"{proceso},{potencia},{horas},{iteraciones},"
                    f"{consumo:.2f},{huella:.4f}\n"
                )

            print(
                "💾 Registro guardado con éxito en 'auditorias.csv'."
            )

        else:
            print(
                "⚠️ Error: El número de iteraciones debe ser mayor que 0."
            )

    elif opcion == 2:
        print("\n================ HISTORIAL DE AUDITORÍAS ================")

        try:
            # Leer el archivo CSV completo
            with open(
                "auditorias.csv",
                mode="r",
                encoding="utf-8"
            ) as archivo:
                contenido = archivo.read()

            # Mostrar el contenido del histórico
            if contenido:
                print(contenido)
            else:
                print("ℹ️ El histórico está vacío.")

        except FileNotFoundError:
            print(
                "ℹ️ Aún no existen registros. "
                "Realiza una auditoría primero."
            )

    elif opcion == 3:
        print("\nSaliendo de EcoAudit CLI. ¡Hasta pronto!")
        break

    else:
        print("⚠️ Opción no válida. Elija un número entre 1 y 3.")
