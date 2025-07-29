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

def compute_global_coverage(result):
    """
    Compute the global coverage percentage, skipping project metadata keys.
    Returns a float between 0 and 100.
    """
    skip_keys = [
        "DatadogLibrary", "NoInstrumentationFound",
        "OpentelemetryLibrary", "DatadogGradleDependency",
        "OpentelemetryGradleDependency", "JavaProjectSummary",
        "PythonProjectSummary", "GoProjectSummary"
    ]
    total_traced = 0
    total_functions = 0
    for k, stats in result.items():
        if k in skip_keys:
            continue
        traced = stats.get('traced', 0)
        total = stats.get('total', 0)
        if total > 0:
            total_traced += traced
            total_functions += total
    if total_functions == 0:
        return 0.0
    return (total_traced / total_functions) * 100
