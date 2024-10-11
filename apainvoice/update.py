from apainvoice import controller, logconf
import logging
import logging.config

logger = logging.getLogger(__name__)


def main():
    logging.config.dictConfig(logconf.get_config_dict())
    controller.update_invoices()


if __name__ == "__main__":
    main()
