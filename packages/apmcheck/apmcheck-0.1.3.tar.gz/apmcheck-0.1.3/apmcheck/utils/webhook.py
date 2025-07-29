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

import requests

def send_report_webhook(webhook_url, report, global_coverage):
    """
    Send the report as a JSON payload to the provided webhook URL.
    Includes the global coverage as a top-level field.
    """
    payload = {
        "global_coverage": global_coverage,
        "report": report,
    }
    try:
        resp = requests.post(webhook_url, json=payload, timeout=10)
        resp.raise_for_status()
        return True, resp.text
    except Exception as e:
        return False, str(e)
