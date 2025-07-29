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
import json
import re

def analyze(path, apm):
    """
    Analyze a Node.js/TypeScript codebase to detect instrumentation coverage for the given APM.

    Args:
        path (str): Root path to the Node.js/TypeScript project.
        apm (str): Name of the APM to analyze (e.g., "datadog", "opentelemetry").

    Returns:
        dict: Analysis results including traced functions, total functions,
              traced imports, and traced init calls.
    """
    result = {}

    # Define APM-specific libraries and instrumentation methods
    apm_definitions = {
        "datadog": {
            "library": "dd-trace",
            "import_pattern": re.compile(r"(import|require)\s.*['\"]dd-trace['\"]"),
            "init_pattern": re.compile(r"\btracer\.init\s*\("),
            "instrumentation_pattern": re.compile(r"\b(tracer\.use|tracer\.trace|startSpan|span\.setTag)\b"),
        },
        "opentelemetry": {
            "library": "@opentelemetry/api",
            "import_pattern": re.compile(r"(import|require)\s.*['\"]@opentelemetry/api['\"]"),
            "init_pattern": re.compile(r"\btrace\.setGlobalTracerProvider\s*\("),
            "instrumentation_pattern": re.compile(r"\b(tracer\.startSpan|span\.setAttribute|context\.with)\b"),
        },
    }

    # Verify that we support the given APM
    if apm not in apm_definitions:
        raise ValueError(f"Unsupported APM '{apm}'. Supported APMs: {list(apm_definitions.keys())}")

    apm_info = apm_definitions[apm]

    # Step 1: Check for APM library presence in package.json
    library_found = False
    package_json_path = os.path.join(path, "package.json")
    if os.path.isfile(package_json_path):
        with open(package_json_path, "r", encoding="utf-8") as f:
            try:
                pkg = json.load(f)
                deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
                if apm_info["library"] in deps:
                    library_found = True
            except json.JSONDecodeError:
                pass

    # Explicitly report library presence
    result[f"{apm.capitalize()}Library"] = {"present": library_found}

    # If library isn't found, no further analysis is needed
    if not library_found:
        return result

    # Step 2: Setup ignored directories and file suffixes
    ignore_dirs = {".git", "test", "tests", "e2e", "scripts", ".docker"}
    ignore_suffixes = (
        ".config.js", ".config.ts", ".spec.js", ".spec.ts",
        ".mock.js", ".mock.ts", ".d.ts", ".stories.ts", ".stories.js"
    )

    # Regex pattern to detect class methods in JS/TS accurately
    method_regex = re.compile(r'''
        ^\s*                                             # Leading whitespace
        (?:public|protected|private)?\s*                 # Visibility modifier (optional)
        (?:async\s+)?                                    # Async keyword (optional)
        (\w+)\s*                                         # Method name
        \([^)]*\)\s*                                     # Parameters
        :?\s*[\w<>\[\],\s]*\s*                           # Return type annotation (optional)
        \{                                               # Opening brace of method body
        ''', re.VERBOSE)

    detected_files = []

    # Step 3: Traverse directory to find relevant JS/TS files
    for root, dirs, files in os.walk(path):
        # Filter out ignored directories
        dirs[:] = [d for d in dirs if d not in ignore_dirs and not d.startswith('.')]
        for file in files:
            if file.endswith((".ts", ".js")) and not file.endswith(ignore_suffixes):
                detected_files.append(os.path.join(root, file))

    # Step 4: Analyze each detected file individually
    for detected_file in detected_files:
        with open(detected_file, "r", encoding="utf-8") as src:
            lines = src.readlines()

        traced_imports = 0  # Counts how many imports of the APM library
        traced_inits = 0    # Counts APM initialization calls
        traced_methods = 0  # Counts methods/functions instrumented at least once
        total_methods = 0   # Counts total methods/functions found

        in_function = False                 # Flag indicating we're inside a method
        brace_count = 0                     # Tracks nesting level to detect method boundaries
        instrumented_current_method = False # Flags if current method has instrumentation

        for line in lines:
            stripped_line = line.strip()

            # Count import statements of the APM library
            if apm_info["import_pattern"].search(stripped_line):
                traced_imports += 1

            # Count initialization calls for the APM
            if apm_info["init_pattern"].search(stripped_line):
                traced_inits += 1

            # Detect if the current line starts a new method
            method_match = method_regex.match(line)
            if method_match:
                total_methods += 1                 # Increment total methods counter
                in_function = True                 # Set flag that we're inside a method
                brace_count = line.count('{') - line.count('}') # Initialize brace count
                instrumented_current_method = False
                continue

            if in_function:
                # Adjust brace count to detect method end
                brace_count += line.count('{') - line.count('}')

                # If instrumentation found and hasn't been counted yet for this method
                if not instrumented_current_method and apm_info["instrumentation_pattern"].search(line):
                    traced_methods += 1
                    instrumented_current_method = True

                # When brace count reaches 0 or below, we've exited the method
                if brace_count <= 0:
                    in_function = False

        # Relative path used for cleaner reporting
        rel_path = os.path.relpath(detected_file, path)

        # Store analysis results for the current file
        result[rel_path] = {
            "traced": traced_methods,       # Number of instrumented methods
            "total": total_methods,         # Total number of methods found
            "traced_imports": traced_imports,
            "traced_inits": traced_inits,
        }

    # If no files analyzed (just the library info present), mark explicitly
    if len(result) == 1:
        result["NoInstrumentationFound"] = {"traced": 0, "total": 0}

    return result
