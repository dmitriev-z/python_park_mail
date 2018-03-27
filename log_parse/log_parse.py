# -*- encoding: utf-8 -*-
import re
import datetime
import collections
main_pattern = re.compile(r'^\[(?P<request_date>\d{1,2}/?[a-zA-Z]+/?\d{1,4} \d{2}:\d{2}:\d{2})?\] ?\"?'
                          r'(?P<request_type>[A-Z]*)? ?(?P<request>[\w:/.\-=?&#% ]*[^ A-Z]) ?(?P<protocol>[A-Z]*)?/'
                          r'(?P<protocol_version>[\d.]*)?\"? ?(?P<response_code>\d{3})? ?(?P<response_time>\d*)?$')
date_pattern = re.compile(r'^(?P<day>\d{1,2})/(?P<month>[a-zA-Z]*)/(?P<year>\d{4}) (?P<hour>\d{1,2}):'
                          r'(?P<minute>\d{1,2}):(?P<second>\d{1,2})$')
request_pattern = re.compile(r'^(?P<scheme>[a-z]*)://(?P<auth_params>|[\w:-]*@)(?P<host>[\w\-.]*):?(?P<port>\d*)?'
                             r'(?P<url_path>|/[\w\-/.]*)\??(?P<parameters>[\w\-=&.%]*)?#?(?P<anchor>[\w\-=&.]*)$')
auth_pattern = re.compile(r'^(?P<login>[\w-]*)?:?(?P<password>[\w-]*)?@?$')
months = {'january': 1, 'february': 2, 'march': 3, 'april': 4, 'may': 5, 'june': 6, 'july': 7, 'august': 8,
          'september': 9, 'october': 10, 'november': 11, 'december': 12}


def parse_log_string(log_string) -> dict:
    try:
        main_pattern.fullmatch(log_string).groupdict()
    except AttributeError:
        pass
    else:
        parsed_log_string = main_pattern.fullmatch(log_string).groupdict()
        parsed_log_string['request_date'] = parse_date_string(parsed_log_string['request_date'])
        parsed_log_string['request'] = parse_request_string(parsed_log_string['request'])
        return parsed_log_string


def parse_date_string(date_string):
    return date_pattern.fullmatch(date_string).groupdict()


def parse_request_string(request_string):
    parsed_request_string = request_pattern.fullmatch(request_string).groupdict()
    parsed_request_string['auth_params'] = parse_auth_params_string(parsed_request_string['auth_params'])
    return parsed_request_string


def parse_auth_params_string(auth_params_string):
    return auth_pattern.fullmatch(auth_params_string).groupdict()


def make_datetime_from_log_date(date):
    for month, month_number in months.items():
        if date['month'].lower() in month:
            date['month'] = month_number
            break
    return datetime.datetime(date['year'], date['month'], date['day'], date['hour'], date['minute'], date['second'])


def make_url_statistics_from_logs(logs, count=False, response=False):
    operated_item = [] if count else collections.defaultdict(list)
    for log in logs:
        url_string = log['request']['host'] + log['request']['url_path']
        if count:
            operated_item.append(url_string)
        elif response:
            operated_item[url_string].append(int(log['response_time']))
    return collections.Counter(operated_item) if count else operated_item


def parse(
        ignore_files=False,
        ignore_urls=None,
        start_at=None,
        stop_at=None,
        request_type=None,
        ignore_www=False,
        slow_queries=False
):
    if ignore_urls is None:
        ignore_urls = []
    parsed_logs = []
    with open('log.log', 'r') as r:
        for line in r.readlines():
            line = line.strip('\n')
            parsed_log = parse_log_string(line.strip('\n'))
            if parsed_log:
                if ignore_files:
                    file_pattern = re.compile(r'\.[a-z]*')
                    if file_pattern.findall(parsed_log['request']['url_path']):
                        continue
                if ignore_urls:
                    url = parsed_log['request']['host'] + parsed_log['request']['url_path']
                    if url in ignore_urls:
                        continue
                if start_at:
                    log_datetime = make_datetime_from_log_date(parsed_log['date'])
                    if log_datetime < start_at:
                        continue
                if stop_at:
                    log_datetime = make_datetime_from_log_date(parsed_log['date'])
                    if log_datetime > start_at:
                        continue
                if request_type:
                    if parsed_log['request']['request_type'].lower() != request_type.lower():
                        continue
                if ignore_www:
                    parsed_log['request']['host'] = parsed_log['request']['host'].replace('www.', '')
                parsed_logs.append(parsed_log)
    if not slow_queries:
        urls_statistics = make_url_statistics_from_logs(parsed_logs, count=True)
    else:
        urls_statistics = make_url_statistics_from_logs(parsed_logs, response=True)
        for url, times in urls_statistics.items():
            urls_statistics[url] = int(sum(times) / len(times))
    urls_statistics_list = list(urls_statistics.values())
    urls_statistics_list.sort(reverse=True)
    return urls_statistics_list[0:5]
