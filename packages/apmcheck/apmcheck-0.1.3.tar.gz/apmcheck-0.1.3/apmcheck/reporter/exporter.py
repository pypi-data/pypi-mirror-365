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

import json
import csv
import sys

def export_json(result):
    content = json.dumps(result, indent=2)
    print(content)

def export_csv(result):
    header = ["File", "Traced", "Total", "Coverage", "Imports Traced", "Inits Traced"]
    rows = []
    skip_keys = [
        "DatadogLibrary", "NoInstrumentationFound",
        "OpentelemetryLibrary", "DatadogGradleDependency",
        "OpentelemetryGradleDependency", "JavaProjectSummary",
        "PythonProjectSummary", "GoProjectSummary"
    ]
    for file in sorted(k for k in result if k not in skip_keys):
        stats = result[file]
        traced = stats.get('traced', 0)
        total = stats.get('total', 0)
        coverage = f"{(traced / total * 100):.1f}%" if total else "0.0%"
        imports_traced = stats.get('traced_imports', 0)
        inits_traced = stats.get('traced_inits', 0)
        rows.append([file, traced, total, coverage, imports_traced, inits_traced])

    writer = csv.writer(sys.stdout, lineterminator='\n')
    writer.writerow(header)
    writer.writerows(rows)
