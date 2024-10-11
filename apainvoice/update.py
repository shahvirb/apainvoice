from apainvoice import controller
import logging
import logging.config
import yaml

logger = logging.getLogger(__name__)


def main():
    with open("log_conf.yaml", "r") as stream:
        config = yaml.load(stream, Loader=yaml.FullLoader)
    logging.config.dictConfig(config)

    controller.update_invoices()


if __name__ == "__main__":
    main()
