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

def format(result):
    header = "{:<70} {:>7} {:>7} {:>10} {:>15} {:>15}".format(
        "File", "Traced", "Total", "Coverage", "Imports Traced", "Inits Traced"
    )
    lines = [header, "-" * len(header)]

    total_traced = 0
    total_functions = 0
    total_imports_traced = 0
    total_inits_traced = 0

    if "DatadogLibrary" in result:
        presence = "Yes" if result["DatadogLibrary"].get("present") else "No"
        lines.append("{:<70} {:>7} {:>7} {:>10} {:>15} {:>15}".format(
            "DatadogLibrary", presence, "-", "-", "-", "-"
        ))

    for file in sorted(k for k in result if k not in ["DatadogLibrary", "NoInstrumentationFound"]):
        stats = result[file]
        traced = stats.get('traced', 0)
        total = stats.get('total', 0)
        imports_traced = stats.get('traced_imports', 0)
        inits_traced = stats.get('traced_inits', 0)

        percent = f"{(traced / total * 100):.1f}%" if total > 0 else "-"

        lines.append("{:<70} {:>7} {:>7} {:>10} {:>15} {:>15}".format(
            file, traced, total, percent, imports_traced, inits_traced
        ))

        if total > 0:
            total_traced += traced
            total_functions += total

        total_imports_traced += imports_traced
        total_inits_traced += inits_traced

    global_percent = (total_traced / total_functions * 100) if total_functions > 0 else 0.0

    lines.append("")
    lines.append("{:<70} {:>7} {:>7} {:>10} {:>15} {:>15}".format(
        "Total",
        total_traced,
        total_functions,
        f"{global_percent:.1f}%" if total_functions else "0.0%",
        total_imports_traced,
        total_inits_traced
    ))

    return "\n".join(lines)
