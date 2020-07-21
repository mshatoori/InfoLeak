import csv

from scapy.all import *
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.firefox.options import Options

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

PAGE_LOAD_WAIT = 30
HOSTS_COUNT = 1000


def ping(data, id=0):
    for i in range(10):
        try:
            ans, _ = sr(IP(dst="doh") / ICMP(id=id, seq=i + 1) / data)
            if len(ans) > 0:
                return
        except Exception as _:
            logger.exception(f"Ping try {i + 1} failed.")
    logger.error("Couldn't ping proxy!")


def read_hosts():
    f = open('hosts.csv')
    reader = csv.reader(f)

    hosts = []

    for _, host in reader:
        hosts.append(host)

    return hosts


def main():
    time.sleep(10)

    options = Options()
    options.set_preference('network.captive-portal-service.enabled', False)
    options.set_preference('captivedetect.canonicalURL', '')
    options.set_preference('privacy.trackingprotection.enabled', False)
    options.set_preference('security.OCSP.enabled', False)

    # Trying to start a DoH connection
    visit_page('example.com', options)

    host_list = read_hosts()[:HOSTS_COUNT]
    for idx, host in enumerate(host_list):
        ping(host, id=idx + 1)
        try:
            visit_page(host, options)
        except Exception as _:
            logger.exception('Host unavailable')
            ping('ERROR')
    ping('DONE')


def visit_page(host, options):
    firefox = webdriver.Remote(
        command_executor='http://selenium-hub:4444/wd/hub',
        desired_capabilities=DesiredCapabilities.FIREFOX,
        options=options,
    )
    for _ in range(3):
        try:
            firefox.get(f'https://{host}')
            print(firefox.title)
            time.sleep(PAGE_LOAD_WAIT)
            break
        except Exception as _:
            logger.exception('Error while loading page')
            time.sleep(5)
    firefox.close()


if __name__ == '__main__':
    main()
