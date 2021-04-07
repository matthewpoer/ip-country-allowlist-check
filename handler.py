"""handler.py can be run directly as a CLI application. See README.md"""

import argparse
import ipaddress
import os
import sys

import flask
from werkzeug.http import HTTP_STATUS_CODES

import geoip2.database
import maxminddb


def ip_in_country_list(ip_address: str, country_list: list) -> dict:
    """primary function handles detection of the country of the passed-in IP
    address and determines if it is in one of the countries in country_list"""

    # Validates ip_address as IPv4 format address
    try:
        ip_object = ipaddress.ip_address(ip_address)
        if ip_object.version != 4 or ip_object.is_unspecified or ip_object.is_private:
            raise ValueError
        print(f'supplied IP address {ip_address} is valid')
    except ValueError:
        print(f'supplied IP address {ip_address} is not a valid IPv4 IP Address')
        return [None, 400]

    # Allows the opportunity of specifying a newer or alternative database file
    maxmind_database_file = os.getenv(
        'MAXMIND_DATABASE_FILE',
        'GeoLite2-Country/GeoLite2-Country.mmdb')

    # Determines which country this IP address resides in, checking for errors
    # with the database, IP Address, and whethor or not the IP exists in the
    # database at all
    # https://github.com/maxmind/GeoIP2-python#database-reader-exceptions
    try:
        with geoip2.database.Reader(maxmind_database_file) as reader:
            country_code = reader.country(ip_address).country.iso_code
            print(f'supplied IP address {ip_address} corresponds with {country_code}')
    except FileNotFoundError:
        print('could not reach database file {maxmind_database_file}')
        return [None, 500]
    except maxminddb.errors.InvalidDatabaseError as err:
        print(f'encountered a problem with the database: {err}')
        return [None, 500]
    except geoip2.errors.AddressNotFoundError:
        print('could not find IP address in ip/country database')
        return [None, 404]
    except Exception: #pylint: disable=broad-except
        print('encountered an unknown problem with the database')
        return [None, 500]

    # Returns boolean on whether or not the country code is in the allow list
    return [(country_code in country_list), 200]


# Sets up default and v1 Flask endpoints for use with `flask run`
app = flask.Flask(__name__)
@app.route('/', methods=['POST'])
@app.route('/v1/', methods=['POST'])
def api_v1_post():
    """Receive IP Address and list of countries from a POST"""

    data = flask.request.get_json()
    print(f"user supplied ip_address {data['ip_address']}")
    print(f"user supplied country list {data['country']}")
    result, status_code = ip_in_country_list(data['ip_address'], data['country'])
    print(f"result: {result}")
    print(f"status_code: {status_code}")

    return {
        "result": result,
        "status_code": status_code,
        "status_msg": f"{status_code} {HTTP_STATUS_CODES[status_code].upper()}",
    }, status_code

def cli():
    """Run the program as a stand-alone CLI application"""
    parser = argparse.ArgumentParser(
        description='Determines if a provided IP Address is located within a set of countries')
    parser.add_argument(
        '--ip_address',help='an IPv4 style IP Address',
        metavar='i',required=True,type=str)
    parser.add_argument(
        '--country',help='ISO Country Code (e.g. US, CA, AU)',
        metavar='c',nargs='+',required=True,type=str)
    args = parser.parse_args()
    print(f"user supplied ip_address {args.ip_address}")
    print(f"user supplied country list {args.country}")

    result, status_code = ip_in_country_list(args.ip_address, args.country) # pylint: disable=invalid-name
    print(f"result: {result}")
    print(f"status_code: {status_code}")

    if status_code == 200:
        print(result)
    else:
        print(status_code)
        sys.exit(1)


# If not running in Flask, function as a CLI application
if __name__ == "__main__":
    cli()
