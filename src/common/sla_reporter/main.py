from .reporter import Reporter

from pathlib import Path
def main(config_path="config/regression_config.yaml", output_path="sla_report.html"):
    # Resolve config_path relative to the project root
    project_root = Path(__file__).parent.parent.parent.parent
    absolute_config_path = project_root / config_path
    reporter = Reporter(str(absolute_config_path), output_path)
    reporter.run_cli()


def cli_main():
    import argparse

    parser = argparse.ArgumentParser(description="Generate SLA report.")
    parser.add_argument(
        "--config",
        default="config/regression_config.yaml",
        help="Path to the configuration file.",
    )
    parser.add_argument(
        "--output", default="sla_report.html", help="Path to the output HTML file."
    )
    args = parser.parse_args()

    # Resolve config_path relative to the project root
    project_root = Path(__file__).parent.parent.parent.parent
    absolute_config_path = project_root / args.config

    main(config_path=str(absolute_config_path), output_path=args.output)

if __name__ == "__main__":
    cli_main()