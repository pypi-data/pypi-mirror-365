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
    Analyzes a Java project to detect APM instrumentation coverage,
    including detection of dependencies defined in Gradle build files.

    Args:
        path (str): Root path of the Java project.
        apm (str): Name of the APM to analyze ("datadog", "opentelemetry").

    Returns:
        dict: Results including instrumented methods, total methods,
              import statements, initialization calls, and Gradle dependency presence.
    """

    # Final analysis result dictionary
    result = {}

    # APM-specific definitions for Java projects
    apm_definitions = {
        "datadog": {
            "library": "com.datadoghq:dd-java-agent",
            "gradle_pattern": re.compile(r'com\.datadoghq:dd-java-agent'),
            "import_pattern": re.compile(r'import\s+datadog\.trace\.api'),
            "init_pattern": re.compile(r'DDTracer\.builder\(\)|GlobalTracer\.registerIfAbsent'),
            "instrumentation_pattern": re.compile(r'(@Trace|GlobalTracer\.get\(\)\.buildSpan|span\.setTag)'),
        },
        "opentelemetry": {
            "library": "io.opentelemetry:opentelemetry-api",
            "gradle_pattern": re.compile(r'io\.opentelemetry:opentelemetry-api'),
            "import_pattern": re.compile(r'import\s+io\.opentelemetry'),
            "init_pattern": re.compile(r'OpenTelemetrySdk\.builder\(\)|SdkTracerProvider\.builder\('),
            "instrumentation_pattern": re.compile(r'(tracer\.spanBuilder|@WithSpan|span\.setAttribute)'),
        },
    }

    # Validate that the requested APM is supported
    if apm not in apm_definitions:
        raise ValueError(f"Unsupported APM '{apm}'. Supported APMs: {list(apm_definitions.keys())}")

    apm_info = apm_definitions[apm]

    # Flags to indicate APM detection
    library_found = False
    gradle_dependency_found = False
    traced_imports = 0
    traced_inits = 0
    total_methods = 0
    traced_methods = 0

    # Common directories to ignore in Java projects
    ignore_dirs = {".git", "target", "build", ".idea", ".docker"}

    # Step 1: Detect the presence of the APM library in Gradle files
    gradle_files = ["build.gradle", "build.gradle.kts"]
    for root, _, files in os.walk(path):
        for gradle_file in gradle_files:
            if gradle_file in files:
                gradle_path = os.path.join(root, gradle_file)
                with open(gradle_path, 'r', encoding='utf-8') as gf:
                    gradle_content = gf.read()
                    if apm_info["gradle_pattern"].search(gradle_content):
                        gradle_dependency_found = True
                        library_found = True
                        break  # Dependency found; no need to continue searching
        if gradle_dependency_found:
            break

    result[f"{apm.capitalize()}GradleDependency"] = {"present": gradle_dependency_found}

    # Step 2: Collect all Java files (.java) for analysis
    java_files = []
    for root, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if d not in ignore_dirs and not d.startswith('.')]
        for file in files:
            if file.endswith(".java"):
                java_files.append(os.path.join(root, file))

    # Regex pattern for detecting Java method declarations
    method_regex = re.compile(r'''
        ^\s*(public|protected|private)?\s*           # Optional visibility
        (static\s+)?                                 # Optional static modifier
        [\w\<\>\[\]]+\s+                             # Return type
        (\w+)\s*                                     # Method name
        \([^\)]*\)\s*                                # Method parameters
        (\{?|throws\s+\w+[\s\w,]*\{?)                # Opening brace or throws declaration
    ''', re.VERBOSE)

    # Step 3: Analyze each Java file individually
    for java_file in java_files:
        with open(java_file, "r", encoding="utf-8") as jf:
            lines = jf.readlines()

        in_method = False
        brace_count = 0
        instrumented_current_method = False

        for line in lines:
            stripped = line.strip()

            # Detect import statements for the APM library
            if apm_info["import_pattern"].search(stripped):
                traced_imports += 1

            # Detect initialization calls for the APM tracer
            if apm_info["init_pattern"].search(stripped):
                traced_inits += 1

            # Detect Java method declarations
            method_match = method_regex.match(stripped)
            if method_match:
                total_methods += 1
                in_method = True
                brace_count = line.count('{') - line.count('}')
                instrumented_current_method = False
                continue

            if in_method:
                brace_count += line.count('{') - line.count('}')

                # Count instrumentation only once per method
                if (not instrumented_current_method and
                        apm_info["instrumentation_pattern"].search(stripped)):
                    traced_methods += 1
                    instrumented_current_method = True

                # Method ends when brace count is balanced
                if brace_count <= 0:
                    in_method = False

    # Explicitly report APM library presence
    result[f"{apm.capitalize()}Library"] = {"present": library_found}

    # Global summary of analyzed Java project
    result["JavaProjectSummary"] = {
        "traced": traced_methods,
        "total": total_methods,
        "traced_imports": traced_imports,
        "traced_inits": traced_inits,
    }

    # Explicitly report if no instrumentation was found
    if total_methods == 0 and traced_methods == 0:
        result["NoInstrumentationFound"] = {"traced": 0, "total": 0}

    return result
