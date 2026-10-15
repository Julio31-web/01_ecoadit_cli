from calculadora import estimar_consumo_wh, calcular_huella_co2
print("EcoAudit CLI")
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

    # Validación robusta de la opción introducida
    try:
        opcion = int(entrada)
    except ValueError:
        print("⚠️ Error: Debe introducir un número entero.")
        continue

    if opcion == 1:
        print("\n[OPCIÓN 1] Iniciando proceso de auditoría...")

        # Solicitar el número de iteraciones y convertirlo a entero
        entrada_iteraciones = input(
            "Introduzca el número de iteraciones: "
        ).strip()

        try:
            iteraciones = int(entrada_iteraciones)
        except ValueError:
            print("⚠️ Error: Debe introducir un número entero.")
            continue

        # Validar que el número de iteraciones sea mayor que 0
        if iteraciones > 0:
            print(f"Número de iteraciones válido: {iteraciones}")

            proceso = input("Nombre del equipo/proceso: ").strip()
            potencia = float(input("Potencia consumida en Vatios (W): "))
            horas = float(input("Horas de uso diario: "))

            consumo = estimar_consumo_wh(potencia, horas, iteraciones)
            huella = calcular_huella_co2(consumo)

            print(f"\n✅ Resultados calculados para '{proceso}':")
            print(f"   • Consumo total: {consumo:.2f} Wh")
            print(f"   • Huella de carbono estimada: {huella:.4f} g CO2")

        else:
            print("⚠️ Error: El número de iteraciones debe ser mayor que 0.")

    elif opcion == 2:
        print("\n[OPCIÓN 2] Consultando registros históricos...")

    elif opcion == 3:
        print("\nSaliendo de EcoAudit CLI. ¡Hasta pronto!")
        break

    else:
        print("⚠️ Opción no válida. Elija un número entre 1 y 3.")