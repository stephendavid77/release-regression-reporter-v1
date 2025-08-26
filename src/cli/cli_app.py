import click
from common.sla_reporter.main import main as sla_main


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    """
    A CLI tool for SLA reporting.
    """
    if ctx.invoked_subcommand is None:
        ctx.invoke(sla_report)


@cli.command(name="sla-report", help="Generate a SLA report based on predefined JQLs.")
@click.option(
    "--config",
    default="config/regression_config.yaml",
    help="Path to the regression config file.",
)
@click.option(
    "--output", default="sla_report.html", help="Path to save the HTML report."
)
def sla_report(config, output):
    """
    Generate an SLA report.
    """
    sla_main(config_path=config, output_path=output)
