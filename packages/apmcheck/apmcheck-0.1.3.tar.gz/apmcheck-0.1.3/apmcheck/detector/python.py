# Copyright (C) 2025 Matías Salinas (support@fenden.com)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http:#www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import re

def analyze(path, apm):
    """
    Analiza un proyecto Python para detectar instrumentación APM.

    Args:
        path (str): Ruta raíz del proyecto Python.
        apm (str): APM a analizar ("datadog", "opentelemetry").

    Returns:
        dict: Resultados incluyendo funciones instrumentadas, totales, imports e inicializaciones.
    """

    # Resultado final
    result = {}

    # Definiciones específicas para cada APM
    apm_definitions = {
        "datadog": {
            "library": "ddtrace",
            "import_pattern": re.compile(r"(from\s+ddtrace|import\s+ddtrace)"),
            "init_pattern": re.compile(r"ddtrace\.patch_all\(\)|tracer\.configure\("),
            "instrumentation_pattern": re.compile(r"(tracer\.trace|@tracer\.wrap|span\.set_tag)"),
        },
        "opentelemetry": {
            "library": "opentelemetry",
            "import_pattern": re.compile(r"(from|import)\s+opentelemetry"),
            "init_pattern": re.compile(r"(trace\.set_tracer_provider|TracerProvider\()"),
            "instrumentation_pattern": re.compile(r"(tracer\.start_as_current_span|@trace\.decorator|span\.set_attribute)"),
        },
    }

    # Valida soporte al APM especificado
    if apm not in apm_definitions:
        raise ValueError(f"Unsupported APM '{apm}'. Supported: {list(apm_definitions.keys())}")

    apm_info = apm_definitions[apm]

    # Flags para verificar presencia
    library_found = False
    traced_imports = 0
    traced_inits = 0
    total_functions = 0
    traced_functions = 0

    # Directorios ignorados
    ignore_dirs = {".git", "__pycache__", "tests", "test", "scripts", "venv", "env", ".venv"}

    # Archivos Python relevantes
    python_files = []

    for root, dirs, files in os.walk(path):
        # Ignora directorios irrelevantes
        dirs[:] = [d for d in dirs if d not in ignore_dirs and not d.startswith('.')]
        for file in files:
            if file.endswith(".py"):
                python_files.append(os.path.join(root, file))

    # Regex precisa para detectar funciones/métodos Python
    func_regex = re.compile(r'^\s*def\s+\w+\s*\(.*?\):')

    for py_file in python_files:
        with open(py_file, "r", encoding="utf-8") as f:
            lines = f.readlines()

        in_function = False
        indentation_level = None
        instrumented_current_function = False

        for idx, line in enumerate(lines):
            stripped = line.strip()

            # Detectar importación del APM
            if apm_info["import_pattern"].search(stripped):
                traced_imports += 1
                library_found = True

            # Detectar inicialización del tracer APM
            if apm_info["init_pattern"].search(stripped):
                traced_inits += 1

            # Detectar inicio de función
            if func_regex.match(line):
                total_functions += 1
                in_function = True
                indentation_level = len(line) - len(line.lstrip())
                instrumented_current_function = False
                continue

            # Si dentro de una función, buscar instrumentación
            if in_function:
                current_indentation = len(line) - len(line.lstrip())

                # Instrumentación encontrada y no previamente contada para esta función
                if (not instrumented_current_function and
                        apm_info["instrumentation_pattern"].search(stripped)):
                    traced_functions += 1
                    instrumented_current_function = True

                # Salir de función al reducir indentación (final de función)
                if stripped and current_indentation <= indentation_level and not stripped.startswith('#'):
                    in_function = False
                    indentation_level = None

    # Reportar explícitamente la presencia de la librería
    result[f"{apm.capitalize()}Library"] = {"present": library_found}

    # Retornar inmediatamente si no está la librería
    if not library_found:
        return result

    # Resultado global del análisis
    result["PythonProjectSummary"] = {
        "traced": traced_functions,
        "total": total_functions,
        "traced_imports": traced_imports,
        "traced_inits": traced_inits,
    }

    # Si no hay funciones ni instrumentación encontrada
    if total_functions == 0 and traced_functions == 0:
        result["NoInstrumentationFound"] = {"traced": 0, "total": 0}

    return result
