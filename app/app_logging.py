import logging


class HealthCheckAccessFilter(logging.Filter):
    """
    Фильтр для фильтрации access-логов с хелс-чеками от куба

    uvicorn.protocols.http.httptools_impl.py:463
    """

    def __init__(
        self,
        name: str = "",
        filter_health_check: bool = None,
        health_check_path: str = "",
    ):
        super(HealthCheckAccessFilter, self).__init__(name)
        self.filter_health_check = filter_health_check
        self.health_check_path = health_check_path

    def filter(self, record):
        allow = True
        if self.filter_health_check and len(record.args) >= 3 and record.args[2] == self.health_check_path:
            allow = False
        return allow


def get_logging_config(
    debug: bool = False, filter_health_check: bool = None, health_check_path: str = ""
) -> dict:  # pragma: no cover
    """"""

    if debug:
        level_name = logging.getLevelName(logging.DEBUG)
    else:
        level_name = logging.getLevelName(logging.INFO)

    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "uvicorn_default": {
                "()": "uvicorn.logging.DefaultFormatter",
                "fmt": "%(levelname)s\t%(asctime)s\t%(message)s",
                "use_colors": None,
            },
            "uvicorn_access": {
                "()": "uvicorn.logging.AccessFormatter",
                "fmt": '%(levelname)s\t%(asctime)s\t%(client_addr)s\t"%(request_line)s"\t%(status_code)s',
            },
            "verbose": {"format": "%(levelname)s\t%(asctime)s\t%(name)14s\t%(message)s"},
        },
        "filters": {
            "access_health_check": {
                "()": HealthCheckAccessFilter,
                "filter_health_check": filter_health_check,
                "health_check_path": health_check_path,
            }
        },
        "handlers": {
            "uvicorn_default": {
                "formatter": "uvicorn_default",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stderr",
            },
            "uvicorn_access": {
                "formatter": "uvicorn_access",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
                "filters": ["access_health_check"],
            },
            "default": {
                "formatter": "verbose",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stderr",
            },
        },
        "loggers": {
            "uvicorn": {"handlers": ["uvicorn_default"], "level": "INFO"},
            "uvicorn.error": {"level": "INFO"},
            "uvicorn.access": {
                "handlers": ["uvicorn_access"],
                "level": "INFO",
                "propagate": False,
            },
            "sqlalchemy.engine": {"handlers": ["default"], "level": "INFO" if debug else "WARNING"},
            "app": {"handlers": ["default"], "level": level_name},
            "history": {"handlers": ["default"], "level": level_name},
        },
    }

    return logging_config


def create_new_loglevel(logging, lvl_name: str, lvl_value: int):
    """
    Добавить новый log level и метод
    logging - модуль
    level_name - имя уровня
    level_value - значение уровня

    метод создается с таким же именем как имя уровня
    P.S
        - имя уровня приводится к верхнему регистру
        - имя метода к нижнему
    """
    setattr(logging, lvl_name.upper(), lvl_value)
    logging.addLevelName(getattr(logging, lvl_name.upper()), lvl_name)

    def _new_method(logger, message, *args, **kwargs):
        if logger.isEnabledFor(getattr(logging, lvl_name.upper())):
            logger._log(getattr(logging, lvl_name.upper()), message, args, **kwargs)

    setattr(logging.Logger, lvl_name.lower(), _new_method)
