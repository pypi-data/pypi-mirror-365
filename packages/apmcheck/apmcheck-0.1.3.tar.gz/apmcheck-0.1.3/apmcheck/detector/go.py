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
    Analyze a Go codebase to detect instrumentation coverage for the given APM.

    Args:
        path (str): Root path to the Go project.
        apm (str): Name of the APM to analyze (e.g., "datadog", "opentelemetry").

    Returns:
        dict: Analysis results including traced functions, total functions,
              traced imports, and traced init calls.
    """
    result = {}

    # Definición específica por APM: importaciones, inicialización e instrumentación
    apm_definitions = {
        "datadog": {
            "library": "gopkg.in/DataDog/dd-trace-go.v1",
            "import_pattern": re.compile(r'"gopkg\.in/DataDog/dd-trace-go\.v\d.*?"'),
            "init_pattern": re.compile(r"tracer\.Start\("),
            "instrumentation_pattern": re.compile(r"(tracer\.StartSpan|span\.SetTag|tracer\.Trace)"),
        },
        "opentelemetry": {
            "library": "go.opentelemetry.io/otel",
            "import_pattern": re.compile(r'"go\.opentelemetry\.io/otel.*?"'),
            "init_pattern": re.compile(r"(sdktrace\.NewTracerProvider|otel\.SetTracerProvider)\("),
            "instrumentation_pattern": re.compile(r"(tracer\.Start|span\.SetAttributes|otel\.Tracer)"),
        },
    }

    # Verificar soporte del APM especificado
    if apm not in apm_definitions:
        raise ValueError(f"Unsupported APM '{apm}'. Supported APMs: {list(apm_definitions.keys())}")

    apm_info = apm_definitions[apm]

    # Flags para reporte de presencia del APM
    library_found = False

    # Archivos Go relevantes
    go_files = []
    ignore_dirs = {".git", "vendor", "test", "tests", "scripts", ".docker"}

    for root, dirs, files in os.walk(path):
        # Ignorar directorios irrelevantes
        dirs[:] = [d for d in dirs if d not in ignore_dirs and not d.startswith('.')]
        for file in files:
            if file.endswith(".go"):
                go_files.append(os.path.join(root, file))

    traced_imports = 0
    traced_inits = 0
    total_functions = 0
    traced_functions = 0

    # Regex precisa para detectar funciones en Go
    func_regex = re.compile(r'^func\s+(?:\([\w\*\s]+\)\s+)?(\w+)\s*\(.*?\)\s*\{')

    for go_file in go_files:
        with open(go_file, "r", encoding="utf-8") as f:
            lines = f.readlines()

        in_function = False
        brace_count = 0
        instrumented_current_function = False

        for line in lines:
            stripped = line.strip()

            # Detectar import del APM
            if apm_info["import_pattern"].search(stripped):
                traced_imports += 1
                library_found = True

            # Detectar inicialización del APM
            if apm_info["init_pattern"].search(stripped):
                traced_inits += 1

            # Detectar inicio de una función
            if match := func_regex.match(stripped):
                total_functions += 1
                in_function = True
                brace_count = line.count('{') - line.count('}')
                instrumented_current_function = False
                continue

            if in_function:
                brace_count += line.count('{') - line.count('}')

                # Contar instrumentación una vez por función
                if not instrumented_current_function and apm_info["instrumentation_pattern"].search(stripped):
                    traced_functions += 1
                    instrumented_current_function = True

                # Cerrar función al balancear las llaves
                if brace_count <= 0:
                    in_function = False

    # Reportar la presencia explícitamente
    result[f"{apm.capitalize()}Library"] = {"present": library_found}

    # Si no hay librería encontrada, terminar aquí
    if not library_found:
        return result

    # Reporte general para el proyecto
    result["GoProjectSummary"] = {
        "traced": traced_functions,
        "total": total_functions,
        "traced_imports": traced_imports,
        "traced_inits": traced_inits,
    }

    # Si no se encuentran funciones instrumentadas ni imports, indicar explícitamente
    if total_functions == 0 and traced_functions == 0:
        result["NoInstrumentationFound"] = {"traced": 0, "total": 0}

    return result
