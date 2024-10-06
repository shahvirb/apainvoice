from apainvoice import controller
import logging

logger = logging.getLogger(__name__)


def main():
    logging.basicConfig(level=logging.DEBUG)
    controller.update_invoices()


if __name__ == "__main__":
    main()
