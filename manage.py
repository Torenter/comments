import click as click
from app.settings import settings
from app.app_logging import get_logging_config


@click.group()
def cli():
    pass


@cli.command()
def runserver():
    import uvicorn

    uvicorn.run(
        "app.application:app",
        host="0.0.0.0",
        loop="uvloop",
        port=settings.PORT,
        access_log=settings.ACCESS_LOG,
        log_config=get_logging_config(settings.DEBUG, settings.FILTER_HEALTH_CHECK_LOG, settings.HEALTH_CHECK_PATH),
    )


if __name__ == "__main__":
    cli()
