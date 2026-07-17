#!/usr/bin/env python
from tipi_tasks import alerts


if __name__ == '__main__':
    task = alerts.send_alerts.apply_async()
