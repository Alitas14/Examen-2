import heapq
import json
import unicodedata

# Que las cadenas solo tengan minúsculas y estén sin acentos
def normalizar_cadena(cadena):
    return ''.join(c for c in unicodedata.normalize('NFD', cadena.lower()) if unicodedata.category(c) != 'Mn')

class SistemaTareas:
    def __init__(self, archivo_persistencia="tareas.json"):
        self.tareas = []  
        self.completadas = set() 
        self.tareas_dict = {}
        self.archivo_persistencia = archivo_persistencia
        self.cargar_tareas()

    def guardar_tareas(self):
        with open(self.archivo_persistencia, "w") as archivo:
            json.dump([{
                "prioridad": tarea["prioridad"],
                "nombre": tarea["nombre"],
                "dependencias": tarea["dependencias"]
            } for tarea in self.tareas_dict.values()], archivo)

    def cargar_tareas(self):
        try:
            with open(self.archivo_persistencia, "r") as archivo:
                tareas_guardadas = json.load(archivo)
                self.tareas_dict = {
                    normalizar_cadena(t["nombre"]): {
                        "prioridad": t["prioridad"],
                        "nombre": t["nombre"],
                        "dependencias": t["dependencias"]
                    } for t in tareas_guardadas
                }
                self.tareas = [(t["prioridad"], t["nombre"], t["dependencias"]) for t in self.tareas_dict.values()]
                heapq.heapify(self.tareas)
        except (FileNotFoundError, json.JSONDecodeError):
            self.tareas_dict = {}

    def agregar_tarea(self, nombre, prioridad, dependencias=[]):
        nombre_normalizado = normalizar_cadena(nombre)
        dependencias = [normalizar_cadena(dep) for dep in dependencias]
        if not nombre or not isinstance(prioridad, int):
            raise ValueError("El nombre debe ser no vacío y la prioridad un número entero.")

        # Verificar si la tarea ya existe
        if nombre_normalizado in self.tareas_dict:
            respuesta = input(f"La tarea '{nombre}' ya existe. ¿Deseas sobreescribirla o descartar la nueva? (sobreescribir/descartar): ").strip().lower()
            if respuesta == 'sobreescribir':
                tarea_actual = self.tareas_dict[nombre_normalizado]
                self.tareas.remove((tarea_actual["prioridad"], tarea_actual["nombre"], tarea_actual["dependencias"]))
                heapq.heapify(self.tareas)
            elif respuesta == 'descartar':
                print("Se descartó la nueva tarea.")
                return
            else:
                print("Opción no válida. No se realizó ningún cambio.")
                return

        nueva_tarea = {
            "prioridad": prioridad,
            "nombre": nombre,
            "dependencias": dependencias
        }
        self.tareas_dict[nombre_normalizado] = nueva_tarea
        heapq.heappush(self.tareas, (prioridad, nombre, dependencias))
        self.guardar_tareas()

    def mostrar_tareas(self):
        if not self.tareas:
            print("No hay tareas pendientes.")
            return
        print("Tareas pendientes ordenadas por prioridad:")
        for prioridad, nombre, dependencias in sorted(self.tareas):
            print(f"- {nombre} (Prioridad: {prioridad}, Dependencias: {dependencias})")

    def completar_tarea(self, nombre):
        nombre_normalizado = normalizar_cadena(nombre)
        if nombre_normalizado in self.tareas_dict:
            tarea = self.tareas_dict[nombre_normalizado]
            # Verificar las dependencias
            if all(dep in self.completadas for dep in tarea["dependencias"]):
                self.tareas.remove((tarea["prioridad"], tarea["nombre"], tarea["dependencias"]))
                heapq.heapify(self.tareas)
                self.completadas.add(nombre_normalizado)
                del self.tareas_dict[nombre_normalizado]
                self.guardar_tareas()
                print(f"Tarea '{nombre}' completada y eliminada del sistema.")
            else:
                dependencias_pendientes = [dep for dep in tarea["dependencias"] if dep not in self.completadas]
                print(f"No se puede completar la tarea '{nombre}'. Aún hay dependencias pendientes: {dependencias_pendientes}.")
        else:
            print(f"Tarea '{nombre}' no encontrada.")

    def obtener_tarea_mayor_prioridad(self):
        if not self.tareas:
            print("No hay tareas pendientes.")
            return None
        tarea = self.tareas[0]
        print(f"Tarea de mayor prioridad: {tarea[1]} (Prioridad: {tarea[0]})")
        return tarea

sistema = SistemaTareas()
while True:
    print("\nSistema de Gestión de Tareas con Prioridades")
    print("1. Añadir una nueva tarea")
    print("2. Mostrar tareas pendientes")
    print("3. Marcar tarea como completada")
    print("4. Obtener tarea de mayor prioridad")
    print("5. Salir")
    opcion = input("Selecciona una opción: ")

    if opcion == "1":
        nombre = input("Nombre de la tarea: ")
        prioridad = int(input("Prioridad de la tarea (número entero, menor = mayor prioridad): "))
        dependencias = input("Dependencias (separadas por comas, si las hay): ").split(",")
        dependencias = [d.strip() for d in dependencias if d.strip()]
        try:
            sistema.agregar_tarea(nombre, prioridad, dependencias)
            print("Tarea añadida correctamente.")
        except ValueError as e:
            print(f"Error: {e}")
    elif opcion == "2":
        sistema.mostrar_tareas()
    elif opcion == "3":
        nombre = input("Nombre de la tarea a completar: ")
        sistema.completar_tarea(nombre)
    elif opcion == "4":
        sistema.obtener_tarea_mayor_prioridad()
    elif opcion == "5":
        print("Saliendo del sistema.")
        break
    else:
        print("Opción no válida. Inténtalo de nuevo.")
