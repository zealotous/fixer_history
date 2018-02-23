from datetime import datetime, timedelta
import json

import asyncio
from itertools import chain

import aiohttp
from aiohttp import web


CURRENCIES = ['AUD', 'BGN', 'BRL', 'CAD', 'CHF', 'CNY', 'CZK', 'DKK', 'GBP',
              'HKD', 'HRK', 'HUF', 'IDR', 'ILS', 'INR', 'ISK', 'JPY', 'KRW',
              'MXN', 'MYR', 'NOK', 'NZD', 'PHP', 'PLN', 'RON', 'RUB', 'SEK',
              'SGD', 'THB', 'TRY', 'USD', 'ZAR',
              ]

HISTORY_TMPL = '<html><body>{currencies_list}<br>{data_table}</body></html>'
INDEX_TMPL = '<html><body>{currencies_list}</body></html>'


def gen_currencies_list(app, current=None):
    url_for = app.router['history'].url_for
    options = ('<a href={} class="{}">{}</a>' 
               ''.format(url_for(currency=c),
                         'active' if current == c else ''
                         , c)
               for c in CURRENCIES)
    return options


def gen_dates(base_date, days):
    date = base_date + timedelta(days=days)
    step = timedelta(days=1)
    while True:
        if date > base_date:
            break

        yield date.isoformat().split('T')[0]
        date += step


async def fetch(base, date):
    async with aiohttp.ClientSession() as session:
        f = session.get('https://api.fixer.io/{}?base={}'.format(date, base))
        async with f as resp:
            print(resp.status)
            r = await resp.text()
            return json.loads(r)


async def index(request):
    currencies = gen_currencies_list(request.app)
    html = INDEX_TMPL.format(currencies_list='\n'.join(currencies))
    return web.Response(body=html, content_type='text/html')


async def history(request):
    currency = request.match_info['currency']
    currency = currency and currency.upper()
    currencies_list = '\n'.join(gen_currencies_list(request.app, currency))
    dates = list(gen_dates(datetime.today(), days=-30))
    raw_data = await asyncio.gather(*(fetch(currency, d) for d in dates))
    date_rate = {r['date']: r['rates'] for r in raw_data}
    rows = [[r'date\currency', ] + CURRENCIES]
    currencies = sorted(CURRENCIES)
    for d in dates:
        row = [d] + ['-' for _ in currencies]  # we can use `repeat` here
        rates = date_rate.get(d)
        if not rates:
            continue

        for i, c in enumerate(currencies, start=1):
            rate = rates.get(c)
            row[i] = str(rate) if rate else '-'
        rows.append(row)
    # TODO: move table rendering into template
    html_rows = ('</td></tr>\n<tr><td>'.join(chain('</td><td>'.join(r for r in row)
                 for row in rows)))
    data_table = '\n'.join(chain(('<table><tr><td>', ), (html_rows, ),
                                 ('</td></tr></table>', )))
    txt = HISTORY_TMPL.format(currencies_list=currencies_list,
                              data_table=data_table)

    return web.Response(body=txt, content_type='text/html')
