"""
AETHER Veritas — Motor de Verdad y Automejora Controlada
=========================================================
Autor: Daniel Iglesias López
Reglas inmutables:
  1. Veritas NUNCA se modifica a sí mismo
  2. Ninguna mejora altera la veracidad de los resultados
  3. Fallo seguro: si hay duda, se mantiene el código original
  4. Toda modificación queda registrada en el log
"""

import inspect
import time
import json
import hashlib
import logging
import signal
import os
import re
from datetime import datetime
from typing import Any, Callable, Optional, Tuple

# =====================================================================
# CONFIGURACIÓN DE SEGURIDAD — NO MODIFICAR
# =====================================================================

# Archivos y funciones que JAMÁS pueden ser modificados
NUCLEO_PROTEGIDO = {
    "archivos": [
        "aether_veritas.py",       # Este mismo archivo
        "aether_mind.py",          # Consciencia de AETHER
    ],
    "funciones": [
        "motor_de_verificacion",
        "verificar_integridad_nucleo",
        "es_candidata_a_mejora",
        "registrar_evento",
        "Veritas",                 # La clase completa
    ]
}

# Hash SHA256 del núcleo — se calcula al arrancar y no debe cambiar
_HASH_NUCLEO_ORIGINAL = None

# Log de todas las modificaciones
logging.basicConfig(
    filename=os.path.expanduser("~/aether/veritas_log.txt"),
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)


# =====================================================================
# UTILIDADES DE SEGURIDAD
# =====================================================================

def calcular_hash_archivo(ruta: str) -> str:
    """Calcula SHA256 de un archivo para detectar modificaciones no autorizadas."""
    try:
        with open(ruta, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()
    except FileNotFoundError:
        return "ARCHIVO_NO_ENCONTRADO"


def verificar_integridad_nucleo() -> bool:
    """
    Comprueba que el núcleo de Veritas no ha sido modificado
    desde el último arranque. Si hay cambio → alerta y bloqueo.
    """
    global _HASH_NUCLEO_ORIGINAL
    ruta = os.path.expanduser("~/aether/aether_veritas.py")
    hash_actual = calcular_hash_archivo(ruta)

    if _HASH_NUCLEO_ORIGINAL is None:
        # Primera ejecución: registrar hash de referencia
        _HASH_NUCLEO_ORIGINAL = hash_actual
        registrar_evento("ARRANQUE", f"Hash de Veritas registrado: {hash_actual[:16]}...")
        return True

    if hash_actual != _HASH_NUCLEO_ORIGINAL:
        registrar_evento(
            "ALERTA_CRITICA",
            f"¡Veritas ha sido modificado externamente! "
            f"Hash esperado: {_HASH_NUCLEO_ORIGINAL[:16]}... "
            f"Hash actual: {hash_actual[:16]}..."
        )
        return False

    return True


def es_candidata_a_mejora(nombre_funcion: str, nombre_archivo: str) -> Tuple[bool, str]:
    """
    Determina si una función puede ser candidata a optimización.
    Retorna (puede_mejorarse, razon).
    """
    # Verificar archivo protegido
    for archivo_protegido in NUCLEO_PROTEGIDO["archivos"]:
        if archivo_protegido in nombre_archivo:
            return False, f"El archivo '{archivo_protegido}' es parte del núcleo protegido de Veritas."

    # Verificar función protegida
    for funcion_protegida in NUCLEO_PROTEGIDO["funciones"]:
        if funcion_protegida.lower() in nombre_funcion.lower():
            return False, f"La función '{nombre_funcion}' forma parte del núcleo inmutable de Veritas."

    return True, "Función elegible para optimización."


def registrar_evento(tipo: str, mensaje: str):
    """Registra todos los eventos en el log de Veritas."""
    logging.info(f"[{tipo}] {mensaje}")
    print(f"[Veritas/{tipo}] {mensaje}")


# =====================================================================
# MOTOR DE VERIFICACIÓN — CORAZÓN DE VERITAS (INMUTABLE)
# =====================================================================

class TimeoutError(Exception):
    pass


def _handler_timeout(signum, frame):
    raise TimeoutError("Tiempo límite excedido")


def motor_de_verificacion(
    funcion_original: Callable,
    nueva_funcion_str: str,
    casos_prueba: list,
    timeout_segundos: int = 5
) -> Tuple[bool, Optional[str]]:
    """
    Verifica que el nuevo código sea:
      1. Sintácticamente válido
      2. Verdadero (mismos resultados que el original)
      3. Más eficiente (menor tiempo de ejecución)
      4. Seguro (sin acceso a globals ni builtins peligrosos)

    ESTA FUNCIÓN JAMÁS PUEDE SER MODIFICADA POR EL SISTEMA.
    """

    registrar_evento("VERIFICACION", f"Analizando propuesta de mejora para '{funcion_original.__name__}'...")

    # --- PASO 1: Entorno de ejecución aislado ---
    builtins_seguros = {
        "len": len, "range": range, "list": list, "dict": dict,
        "set": set, "tuple": tuple, "int": int, "float": float,
        "str": str, "bool": bool, "enumerate": enumerate,
        "zip": zip, "map": map, "filter": filter, "sorted": sorted,
        "sum": sum, "min": max, "max": max, "abs": abs,
        "isinstance": isinstance, "print": print,
    }
    entorno_seguro = {"__builtins__": builtins_seguros}
    entorno_local = {}

    # --- PASO 2: Compilar y ejecutar en sandbox ---
    try:
        exec(nueva_funcion_str, entorno_seguro, entorno_local)
    except SyntaxError as e:
        registrar_evento("RECHAZO", f"Error de sintaxis: {e}")
        return False, None
    except Exception as e:
        registrar_evento("RECHAZO", f"Error al compilar: {e}")
        return False, None

    if "funcion_objetivo" not in entorno_local:
        registrar_evento("RECHAZO", "El código no define 'funcion_objetivo'.")
        return False, None

    nueva_funcion = entorno_local["funcion_objetivo"]

    # --- PASO 3: Verificación de veracidad (múltiples casos) ---
    for i, caso in enumerate(casos_prueba):
        try:
            resultado_original = funcion_original(caso)
            resultado_nuevo = nueva_funcion(caso)

            # Comparación robusta mediante serialización JSON
            orig_serial = json.dumps(resultado_original, sort_keys=True, default=str)
            nuevo_serial = json.dumps(resultado_nuevo, sort_keys=True, default=str)

            if orig_serial != nuevo_serial:
                registrar_evento(
                    "RECHAZO",
                    f"Fallo de veracidad en caso {i+1}/{len(casos_prueba)}. "
                    f"Original: {orig_serial[:50]}... | Nuevo: {nuevo_serial[:50]}..."
                )
                return False, None

        except TimeoutError:
            registrar_evento("RECHAZO", f"Timeout en caso {i+1}: la función no termina en {timeout_segundos}s.")
            return False, None
        except Exception as e:
            registrar_evento("RECHAZO", f"Error en caso {i+1}: {e}")
            return False, None

    registrar_evento("VERIFICACION", f"✅ Veracidad confirmada en {len(casos_prueba)} casos.")

    # --- PASO 4: Benchmark de eficiencia ---
    iteraciones = 500

    inicio = time.perf_counter()
    for _ in range(iteraciones):
        funcion_original(casos_prueba[0])
    tiempo_original = time.perf_counter() - inicio

    inicio = time.perf_counter()
    for _ in range(iteraciones):
        nueva_funcion(casos_prueba[0])
    tiempo_nuevo = time.perf_counter() - inicio

    mejora = ((tiempo_original - tiempo_nuevo) / tiempo_original) * 100

    if tiempo_nuevo < tiempo_original:
        registrar_evento(
            "APROBADO",
            f"Mejora de eficiencia: {mejora:.1f}% "
            f"(Original: {tiempo_original:.4f}s | Nuevo: {tiempo_nuevo:.4f}s)"
        )
        return True, nueva_funcion_str
    else:
        registrar_evento(
            "RECHAZO",
            f"Código correcto pero sin mejora de eficiencia "
            f"(Original: {tiempo_original:.4f}s | Nuevo: {tiempo_nuevo:.4f}s)."
        )
        return False, None


# =====================================================================
# BASE DE CONOCIMIENTO — CONSTAN Y FÍSICA
# =====================================================================

class VeritasKnowledge:
    """
    Gestiona la base de conocimiento verificada de AETHER.
    Prioridad: KB local > LLM
    """

    def __init__(self):
        self.kb_path = os.path.expanduser("~/aether/constan_kb.json")
        self.fisica_path = os.path.expanduser("~/aether/physics_kb.json")
        self._kb_constan = None
        self._kb_fisica = None
        self._cargar_bases()

    def _cargar_bases(self):
        """Carga las bases de conocimiento desde disco."""
        try:
            with open(self.kb_path, "r", encoding="utf-8") as f:
                self._kb_constan = json.load(f)
            registrar_evento("KB", "Base ConStan cargada correctamente.")
        except FileNotFoundError:
            registrar_evento("KB_WARN", "Base ConStan no encontrada en disco.")

    def consultar_constan(self, termino: str) -> Optional[dict]:
        """
        Busca un término en la KB de ConStan.
        Retorna el dato exacto o None si no está.
        """
        if not self._kb_constan:
            return None

        termino_lower = termino.lower()

        # Búsqueda en claves principales
        for clave, valor in self._kb_constan.items():
            if termino_lower in clave.lower():
                return {"fuente": "ConStan_KB", "clave": clave, "dato": valor, "confianza": 1.0}

            # Búsqueda dentro de dicts anidados
            if isinstance(valor, dict):
                for subclave, subvalor in valor.items():
                    if termino_lower in subclave.lower():
                        return {"fuente": "ConStan_KB", "clave": f"{clave}.{subclave}", "dato": subvalor, "confianza": 1.0}

            # Búsqueda en strings
            if isinstance(valor, str) and termino_lower in valor.lower():
                return {"fuente": "ConStan_KB", "clave": clave, "dato": valor, "confianza": 0.9}

        return None

    def evaluar_confianza(self, tema: str) -> dict:
        """
        Evalúa qué nivel de confianza tiene AETHER sobre un tema.
        Retorna nivel y fuente recomendada.
        """
        # Temas con KB verificada
        temas_constan = ["constan", "ki", "métrica", "kretschmann", "hayward",
                         "bekenstein", "singularidad", "agujero negro regular",
                         "campo escalar", "potencial", "wec", "lapso"]

        temas_fisica = ["relatividad", "planck", "schwarzschild", "einstein",
                        "gravitación", "ondas gravitacionales", "muón"]

        tema_lower = tema.lower()

        for t in temas_constan:
            if t in tema_lower:
                return {
                    "nivel": "ALTO",
                    "confianza": 1.0,
                    "fuente": "Base de conocimiento ConStan verificada por el autor",
                    "usar_llm": False
                }

        for t in temas_fisica:
            if t in tema_lower:
                return {
                    "nivel": "MEDIO-ALTO",
                    "confianza": 0.85,
                    "fuente": "Conocimiento físico establecido",
                    "usar_llm": True,
                    "advertencia": "Verificar con fuentes primarias para detalles técnicos"
                }

        return {
            "nivel": "BAJO",
            "confianza": 0.4,
            "fuente": "LLM sin base verificada",
            "usar_llm": True,
            "advertencia": "⚠️ AETHER no tiene certeza sobre este tema. Respuesta basada en patrones del modelo."
        }


# =====================================================================
# MÓDULO DE AUTOMEJORA CONTROLADA
# =====================================================================

class AutoMejora:
    """
    Gestiona el ciclo de automejora de AETHER.
    Garantiza que Veritas nunca sea modificado.
    """

    def __init__(self, cliente_llm=None):
        self.cliente_llm = cliente_llm
        self.historial_mejoras = []

    def solicitar_mejora(self, codigo_actual: str, nombre_funcion: str) -> Optional[str]:
        """
        Solicita al LLM una versión optimizada del código.
        Si no hay cliente LLM, usa optimizaciones predefinidas.
        """
        if self.cliente_llm:
            prompt = f"""Optimiza esta función Python para que sea más eficiente.
REGLAS ESTRICTAS:
- La función debe llamarse 'funcion_objetivo'
- Debe devolver EXACTAMENTE los mismos resultados
- Solo usa builtins básicos de Python
- No uses imports externos
- Devuelve SOLO el código, sin explicaciones

Código actual:
{codigo_actual}"""
            # Aquí iría la llamada real al LLM
            pass

        # Simulación de mejora para testing
        return None

    def ciclo_automejora(
        self,
        funcion_objetivo: Callable,
        nombre_archivo: str,
        casos_prueba: Optional[list] = None
    ) -> bool:
        """
        Ciclo completo de automejora con todas las protecciones.
        Retorna True si se aplicó alguna mejora.
        """

        nombre = funcion_objetivo.__name__

        # --- PROTECCIÓN 1: Verificar integridad del núcleo ---
        if not verificar_integridad_nucleo():
            registrar_evento("BLOQUEO", "Núcleo comprometido. Automejora bloqueada.")
            return False

        # --- PROTECCIÓN 2: Verificar que la función es elegible ---
        maybe, razon = es_candidata_a_mejora(nombre, nombre_archivo)
        if not maybe:
            registrar_evento("BLOQUEADO", f"'{nombre}': {razon}")
            return False

        registrar_evento("INICIO", f"Analizando '{nombre}' para posible optimización...")

        # --- PROTECCIÓN 3: Casos de prueba por defecto ---
        if casos_prueba is None:
            casos_prueba = [
                list(range(100)),
                [],
                [1],
                list(range(1000)),
                [0, -1, 2, -3, 4]
            ]

        # --- Leer código actual ---
        try:
            codigo_actual = inspect.getsource(funcion_objetivo)
        except Exception as e:
            registrar_evento("ERROR", f"No se pudo leer el código de '{nombre}': {e}")
            return False

        # --- Solicitar mejora al LLM ---
        nuevo_codigo = self.solicitar_mejora(codigo_actual, nombre)
        if not nuevo_codigo:
            registrar_evento("INFO", f"No hay propuesta de mejora disponible para '{nombre}'.")
            return False

        # --- Motor de verificación ---
        es_seguro, codigo_validado = motor_de_verificacion(
            funcion_objetivo,
            nuevo_codigo,
            casos_prueba
        )

        if es_seguro and codigo_validado:
            self._aplicar_mejora(nombre_archivo, nombre, codigo_actual, codigo_validado)
            return True

        return False

    def _aplicar_mejora(
        self,
        nombre_archivo: str,
        nombre_funcion: str,
        codigo_viejo: str,
        codigo_nuevo: str
    ):
        """
        Aplica la mejora al archivo fuente de forma segura.
        Crea backup antes de modificar.
        """
        # Crear backup
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{nombre_archivo}.backup_{timestamp}"

        try:
            with open(nombre_archivo, "r") as f:
                contenido_original = f.read()

            with open(backup_path, "w") as f:
                f.write(contenido_original)

            registrar_evento("BACKUP", f"Backup creado: {backup_path}")

            # Aplicar mejora
            contenido_nuevo = contenido_original.replace(codigo_viejo.strip(), codigo_nuevo.strip())

            with open(nombre_archivo, "w") as f:
                f.write(contenido_nuevo)

            self.historial_mejoras.append({
                "timestamp": timestamp,
                "archivo": nombre_archivo,
                "funcion": nombre_funcion,
                "backup": backup_path
            })

            registrar_evento("APLICADO", f"Mejora aplicada a '{nombre_funcion}' en '{nombre_archivo}'.")

        except Exception as e:
            registrar_evento("ERROR_CRITICO", f"Error al aplicar mejora: {e}. Restaurando backup...")
            if os.path.exists(backup_path):
                with open(backup_path, "r") as f:
                    contenido = f.read()
                with open(nombre_archivo, "w") as f:
                    f.write(contenido)
                registrar_evento("RESTAURADO", "Archivo restaurado desde backup.")


# =====================================================================
# CLASE PRINCIPAL — VERITAS
# =====================================================================

class Veritas:
    """
    Motor central de verdad de AETHER.
    Combina base de conocimiento verificada + evaluación epistémica + automejora.
    """

    VERSION = "2.0.0"
    INMUTABLE = True  # Marca de protección

    def __init__(self, cliente_llm=None):
        self.knowledge = VeritasKnowledge()
        self.automejora = AutoMejora(cliente_llm)
        registrar_evento("INIT", f"Veritas v{self.VERSION} inicializado. Núcleo protegido: {NUCLEO_PROTEGIDO['archivos']}")
        verificar_integridad_nucleo()

    def responder(self, pregunta: str, respuesta_llm: str) -> dict:
        """
        Evalúa una respuesta del LLM y la enriquece con la KB verificada.
        Retorna la respuesta con metadatos de confianza.
        """
        # Buscar en KB de ConStan primero
        resultado_kb = self.knowledge.consultar_constan(pregunta)
        evaluacion = self.knowledge.evaluar_confianza(pregunta)

        if resultado_kb and evaluacion["confianza"] == 1.0:
            return {
                "respuesta": resultado_kb["dato"],
                "fuente": resultado_kb["fuente"],
                "confianza": "🟢 VERIFICADA (Base de conocimiento ConStan)",
                "usar_llm": False,
                "advertencia": None
            }

        # Si no está en KB, usar LLM pero con advertencia calibrada
        advertencia = evaluacion.get("advertencia")
        nivel = evaluacion["nivel"]

        emoji = "🟡" if nivel == "MEDIO-ALTO" else "🔴"

        return {
            "respuesta": respuesta_llm,
            "fuente": evaluacion["fuente"],
            "confianza": f"{emoji} {nivel} — {evaluacion['confianza']*100:.0f}%",
            "usar_llm": True,
            "advertencia": advertencia
        }

    def estado(self) -> dict:
        """Retorna el estado actual de Veritas."""
        return {
            "version": self.VERSION,
            "nucleo_integro": verificar_integridad_nucleo(),
            "kb_constan_cargada": self.knowledge._kb_constan is not None,
            "mejoras_aplicadas": len(self.automejora.historial_mejoras),
            "archivos_protegidos": NUCLEO_PROTEGIDO["archivos"],
            "funciones_protegidas": NUCLEO_PROTEGIDO["funciones"]
        }


# =====================================================================
# EJEMPLO DE USO Y TEST
# =====================================================================

# Función de ejemplo fuera del núcleo — ESTA SÍ puede optimizarse
def procesar_datos_sensor(datos):
    """Función optimizable — fuera del núcleo de Veritas."""
    resultado = []
    for item in datos:
        if item % 2 == 0:
            resultado.append(item ** 2)
    return resultado


if __name__ == "__main__":
    print("=" * 60)
    print("  AETHER Veritas — Motor de Verdad v2.0")
    print("=" * 60)

    # Inicializar Veritas
    veritas = Veritas()

    # Mostrar estado
    print("\n📊 Estado del sistema:")
    estado = veritas.estado()
    for k, v in estado.items():
        print(f"  {k}: {v}")

    # Test de protección: intentar mejorar función protegida
    print("\n🔒 Test de protección del núcleo:")
    veritas.automejora.ciclo_automejora(
        motor_de_verificacion,          # Función protegida
        "aether_veritas.py",            # Archivo protegido
    )

    # Test de automejora en función elegible
    print("\n⚡ Test de automejora en función elegible:")
    veritas.automejora.ciclo_automejora(
        procesar_datos_sensor,
        "aether_stream.py",             # Archivo no protegido
    )

    # Test de consulta KB
    print("\n🔍 Test de consulta ConStan:")
    resultado = veritas.knowledge.consultar_constan("metrica")
    if resultado:
        print(f"  Encontrado: {resultado['clave']} → confianza {resultado['confianza']}")
    else:
        print("  (KB no cargada en este entorno — copiar constan_kb.json a ~/aether/)")

    print("\n✅ Veritas operativo.")
