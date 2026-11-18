# SmartCity Mobility — Simulador POO (SDA 2)

Simulador de una flota urbana de vehículos eléctricos (coches y patinetes)
programado con **Programación Orientada a Objetos** en Python 3. Simula
trayectos, consumo de batería y recargas, y guarda el estado en `flota.json`.

Programación y Computación · 2.º de Bachillerato · Prof. Javier García Escobedo
SDA 2: *Simulador Orientado a Objetos: La Ciudad Inteligente*

## Equipo
- Julio
- Diego

Trabajo en pareja con roles de Conductor/Navegante alternos. Cada commit lo
publica, desde su propia cuenta, quien conduce en esa unidad.

## Estructura

| Archivo | Responsabilidad |
|---|---|
| `vehiculo.py` | Clases `Vehiculo`, `CocheElectrico`, `PatineteElectrico` (lógica de cada vehículo) |
| `simulador.py` | Clase `Flota`: colección polimórfica y persistencia JSON |
| `main.py` | Menú de consola: solo interacción con el usuario |
| `flota.json` | Datos guardados de la flota (se actualiza con la opción 5) |
| `test_vehiculo.py` | Pruebas de 3.1, 3.2 y 4.1 |
| `test_simulador.py` | Pruebas de 4.2 (flota y polimorfismo) |
| `test_persistencia.py` | Pruebas de 5.1 (JSON) |
| `test_main.py` | Pruebas del menú (5.2) |
| `docs/` | Texto íntegro de las consultas a IA (evidencia del PROMPT LOG) |

Reto DUA (voluntario, rama `feature/reto-dua-estacion`): `estacion.py` y
`test_estacion.py`.

## Diagrama de clases (resumen)

```
                 Vehiculo
  - _nivel_bateria: float        + conducir(distancia_km) -> bool
  - _kilometros_totales: float   + recargar(energia_kwh) -> float
  + matricula / modelo / capacidad_kwh   + obtener_estado() -> str
                                 + a_diccionario() -> dict
          ▲                               ▲
  CocheElectrico                   PatineteElectrico
  + plazas: int                    + velocidad_maxima_kmh: float (≤ 25)
  obtener_estado() sobrescrito     conducir() sobrescrito (0.02 kWh/km)
                                   obtener_estado() sobrescrito

  Flota  ◇──── 0..* Vehiculo
  - _vehiculos: list
  + agregar_vehiculo()  + simular_jornada()  + recargar_flota_critica()
  + guardar_en_archivo()  + cargar_de_archivo()
```

> Este resumen NO sustituye al UML y a la tabla de traza de la libreta
> técnica, que el profesor exige hechos a mano y sellados.

## Reglas de la simulación

- Estado inicial: batería 100.0 %, 0.0 km.
- Consumo: coche 0.15 kWh/km; patinete 0.02 kWh/km (constantes al principio
  de `vehiculo.py`).
- `porcentaje = energía (kWh) / capacidad (kWh) × 100`.
- Si la batería no alcanza, `conducir()` devuelve `False` y el vehículo no se mueve.
- `recargar()` nunca pasa de 100.0 %.
- Recarga crítica: batería ≤ 20 % → +15 kWh.

## Cómo ejecutarlo en Visual Studio Code

1. `Archivo > Abrir carpeta…` y elegir la carpeta `02_smartcity_poo`.
2. Abrir la terminal (`Terminal > Nuevo terminal`): ya estará en la carpeta.
3. Lanzar el simulador:
   ```bash
   python3 main.py
   ```
4. Lanzar las pruebas (una a una o todas):
   ```bash
   python3 test_vehiculo.py
   python3 test_simulador.py
   python3 test_persistencia.py
   python3 test_main.py
   python3 -m unittest          # todas a la vez
   ```

`main.py` usa `flota.json` de la carpeta actual: ejecutadlo siempre desde
`02_smartcity_poo`. Las pruebas usan archivos temporales y no modifican el
`flota.json` real.

## Decisiones técnicas propias (no las fija el profesor)

El material del profesor no especifica estos casos. Los hemos resuelto así,
y cada uno tiene su prueba:

| Caso | Decisión | Motivo |
|---|---|---|
| Capacidad ≤ 0 | `ValueError` en el constructor | Evita dividir entre 0 en `conducir()`/`recargar()` |
| Distancia negativa en `conducir()` | `ValueError` | Un viaje negativo "cargaría" la batería |
| Energía negativa en `recargar()` | `ValueError` | Una recarga negativa sería un consumo oculto |
| Plazas < 1 / velocidad ≤ 0 | `ValueError` | Estados imposibles |
| Kilómetros negativos | Los bloquea el propio setter antifraude | Empiezan en 0 y no pueden bajar |
| Batería que queda en -0.0000001 por redondeo | `max(..., 0.0)` en `conducir()` | Evitar un `ValueError` falso al gastar justo toda la batería |
| Restaurar batería y km al cargar JSON | Se crea el objeto y luego se asignan con los setters | El constructor no recibe esos datos; así además se validan |
| Registro dañado dentro de `flota.json` | Se ignora con aviso y se cargan los demás | No perder toda la flota por un dato incorrecto |
| JSON válido que no es una lista | Se trata como archivo dañado | Evitar errores al recorrerlo |
| Acceso a la lista desde `main.py` | `Flota.obtener_vehiculos()` devuelve una copia | `main.py` no toca el atributo protegido `_vehiculos` |
| Números con coma (`0,5`) | Se aceptan en el menú | Comodidad con teclado español |

## Uso de IA (protocolo del profesor)

El código de este repositorio se generó con **Claude (Anthropic)** a petición
de Julio y Diego. Cada `.py` termina con su bloque `PROMPT LOG`, y el texto
íntegro de las consultas está en `docs/`. El apartado *"3. Aplicación crítica
y modificaciones realizadas"* de cada bloque lo completan Julio y Diego con lo
que han revisado y cambiado realmente.

## Evidencias pendientes (manuales)

- [ ] Diagrama UML de `Vehiculo` y subclases en la libreta técnica.
- [ ] Tabla de traza (pasos 3 y 4) resuelta a mano.
- [ ] Sello del profesor en la libreta.
- [ ] Apartado 3 de cada PROMPT LOG completado por la pareja.
- [ ] Etiqueta `v1.0` publicada (`git push origin master --tags`).
