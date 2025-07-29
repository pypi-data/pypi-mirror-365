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

import click
from apmcheck.detector import python as detector_python
from apmcheck.detector import nodejs as detector_nodejs
from apmcheck.detector import go as detector_go
from apmcheck.detector import java as detector_java
from apmcheck.reporter.formatter import format as format_table
from apmcheck.reporter.exporter import export_json, export_csv
from apmcheck.utils.coverage import compute_global_coverage
from apmcheck.utils.webhook import send_report_webhook

@click.command()
@click.argument('path')
@click.option('--language', type=click.Choice(['python', 'nodejs', 'go', 'java']), required=True)
@click.option('--apm', type=click.Choice(['datadog', 'opentelemetry']), required=True)
@click.option('--format', type=click.Choice(['table', 'json', 'csv']), default='table', help="Output format")
@click.option('--min-coverage', type=float, default=0.0, help="Minimum global coverage percent required")
@click.option('--webhook', type=str, default=None, help="Webhook URL to send the JSON report")
def main(path, language, apm, format, min_coverage, webhook):
    """Detect APM instrumentation coverage in the given codebase."""

    # Run the appropriate analyzer
    if language == "python":
        result = detector_python.analyze(path, apm)
    elif language == "nodejs":
        result = detector_nodejs.analyze(path, apm)
    elif language == "go":
        result = detector_go.analyze(path, apm)
    elif language == "java":
        result = detector_java.analyze(path, apm)
    else:
        result = {"UnknownLanguage": {"traced": 0, "total": 0}}

    # Output to console
    if format == 'json':
        export_json(result)
    elif format == 'csv':
        export_csv(result)
    else:  # table
        output_content = format_table(result)
        click.echo("Results:")
        click.echo(output_content)

    # Always compute coverage
    global_coverage = compute_global_coverage(result)

    if min_coverage > 0:
        click.echo(f"Coverage {global_coverage:.1f}% is below the required minimum of {min_coverage}%")

    # Always send webhook if set, even if coverage is too low
    if webhook:
        click.echo(f"Sending report to webhook: {webhook}")
        ok, resp = send_report_webhook(webhook, result, global_coverage)
        if ok:
            click.echo("Webhook sent successfully.")
        else:
            click.echo(f"Webhook failed: {resp}")

    # Fail if under required minimum

    if global_coverage < min_coverage:
        import sys
        sys.exit(1)

if __name__ == "__main__":
    main()
