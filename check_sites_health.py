import argparse
import sys
from urllib.error import HTTPError
from urllib.parse import urlparse
from urllib.request import urlopen
from datetime import datetime

import whois

EXPIRATION_THRESHOLD = 30


def get_args():
    parser = argparse.ArgumentParser(description='Check site health: status code and expiration date.')
    parser.add_argument('filepath', help='Path to file with urls')
    args = parser.parse_args()
    return args


def load_urls4check(path):
    try:
        with open(path) as urlsfile:
            urlsfile_data = urlsfile.read()
            urls = [url.strip() for url in urlsfile_data.split('\n') if url != ""]
        return urls
    except FileNotFoundError:
        sys.exit('Wrong filename or path to file.')


def is_server_respond_with_200(url):
    try:
        request = urlopen(url)
        status_code = request.getcode()
        return status_code == 200
    except HTTPError:
        return False


def get_domain_name(url):
    domain_names = urlparse(url).netloc
    return domain_names


def get_server_expiration_in_days(domain_name):
    domain_whois = whois.whois(domain_name)
    expiration_date = domain_whois['expiration_date']
    # get first date if value is a list with multiple dates
    if type(expiration_date) is list:
        expiration_date = expiration_date[0]
    days_to_expire = (expiration_date - datetime.now()).days
    return days_to_expire


def print_healt_status(url_list):
    print("Starting health status check...")
    for num, url in enumerate(url_list):
        print('\nProcessing {num}/{total} url: {url}:'.format(
            num=num + 1,
            total=len(url_list),
            url=url
        ))
        print("Status code 200: {}".format(is_server_respond_with_200(url)))

        domain_name = get_domain_name(url)
        days_to_expire = get_server_expiration_in_days(domain_name)
        if days_to_expire > EXPIRATION_THRESHOLD:
            print("Domain name is paid for one month ahead. It will expire in {} days".format(days_to_expire))
        else:
            print(
                "Domain name will expire in less than one month. It is left less than {} days!".format(days_to_expire))


if __name__ == '__main__':
    args = get_args()
    urls = load_urls4check(args.filepath)
    print_healt_status(urls)
