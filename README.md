# ip-country-allowlist-check

Microservice to determine if a provided IP Address is located within a country from the provided [allow list][1] (fka as "[whitelist][2]"). The IP Address will be expected to be a `string` in IPv4 format and the allow list to be a list of ISO [3166-1 alpha-2][3] (i.e. standard two-digit) Country Codes, as these are referenced from our upstream country database provider.

[1]: https://en.wikipedia.org/wiki/Whitelisting
[2]: https://www.ncsc.gov.uk/blog-post/terminology-its-not-black-and-white
[3]: https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2

The service is written in Python and can be executed as single program, Flask application, or Docker container.

## Program Use (CLI)

```sh
> python handler.py --ip_address 76.97.242.233 --country US AU CA
user supplied ip_address 76.97.242.233
user supplied country list ['US', 'AU', 'CA']
supplied IP address 76.97.242.233 is valid
supplied IP address 76.97.242.233 corresponds with US
result: True
status_code: 200
True
```

## API Use (JSON via Flask)

Invoke the web service with `make run`

POST a JSON call to the endpoint, e.g.
```sh
curl --silent -X POST http://127.0.0.1:5000/v1/ \
  --header "Content-Type: application/json" \
  --data $'{
    "country":[
        "AU",
        "CA",
        "US"
    ],
    "ip_address":"76.97.242.233"
}' | jq
```

This will give you a JSON result like

```json
{
  "result": true,
  "status_code": 200,
  "status_msg": "200 OK"
}
```

## Docker use

Running `make docker-image` will build a Docker image with the current timestamp as the tag. 

Once built, a `make docker-run` will run the application container. The container is using Flask, so the same API Use is followed, e.g.

```sh
curl --silent -X POST http://localhost:5000/v1/ \
  --header "Content-Type: application/json" \
  --data $'{
    "country":[
        "AU",
        "CA",
        "US"
    ],
    "ip_address":"76.97.242.233"
}' | jq
```

## Sourcing Location Data

This service includes GeoLite2 data created by MaxMind, available from https://www.maxmind.com.

This database should be updated on a periodic basis (e.g. once per quarter). The most recent download date of the database is date-stamped in the directory name housing the database.

## Response Codes

There are two potentially valid response codes from the service:
* a `200 Successful` response indicates that the provided IP address does exist in one of the countries from the included allow list.
* a `404 Not Found` response indicates that the provided IP address does not exist in the IP/Country mapping database, and therefore we cannot determine if the address is or is not in one of the allowed countries

Problems with the IP Address, Allow List, or server setup will result in one of the following errors:
* `400 Bad Request`
* `500 Internal Server Error`

When functioning as a web service, all successful and error cases should result in a JSON body with a "result" key of `true`, `false`, or `null`.
