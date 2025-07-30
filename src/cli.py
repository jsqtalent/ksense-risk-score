import json
import os

import click
from dotenv import load_dotenv
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from collector import Collector
from fever_detector import FeverDetector
from high_risk_detector import HighRiskDetector
from quality_issue_detector import QualityIssueDetector

console = Console()


@click.group()
def cli():
    pass


@cli.command()
def run():
    load_dotenv()
    api_token = os.getenv("API_KEY")

    with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
    ) as progress:
        task = progress.add_task("Collecting patients", total=None)

        collection = Collector(
            "https://assessment.ksensetech.com/api",
            api_token,
            lambda message: progress.update(task, description=f"Collecting patients: {message}")
        ).collect()

        quality_issues = QualityIssueDetector(collection).detect()
        fevers = FeverDetector(collection).detect()
        high_risks = HighRiskDetector(collection).detect()

        print(
            json.dumps(
                dict(
                    high_risk_patients=[patient.patient_id for patient in high_risks],
                    fever_patients=[patient.patient_id for patient in fevers],
                    data_quality_issues=[patient.patient_id for patient in quality_issues]
                )
            )
        )


if __name__ == '__main__':
    cli()
