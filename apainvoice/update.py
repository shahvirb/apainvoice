from apainvoice.controller import update_invoices
import logging

logger = logging.getLogger(__name__)


def main():
    logging.basicConfig(level=logging.DEBUG)
    update_invoices()


if __name__ == "__main__":
    main()
