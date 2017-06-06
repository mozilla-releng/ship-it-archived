from datetime import datetime, timedelta


def parse_iso8601_to_date_time(string):
    # XXX Only supports the 'YYYY-mm-ddTHH:MM:SS+ZZ:ZZ' format
    if not isinstance(string, str):
        raise TypeError('"%s" is not a string' % string)

    datetime_without_timezone = string[0:19]
    timezone_sign = string[19]
    timezone_offset_hours = int(string[20:22])
    timezone_offset_minutes = int(string[23:])

    local_date_time = datetime.strptime(datetime_without_timezone,'%Y-%m-%dT%H:%M:%S')
    timezone_delta = timedelta(hours=timezone_offset_hours, minutes=timezone_offset_minutes)

    if timezone_sign == '+':
        utc_date_time = local_date_time - timezone_delta
    elif timezone_sign == '-':
        utc_date_time = local_date_time + timezone_delta
    else:
        raise ValueError('Unknown timezone sign "%s"' % timezone_sign)

    return utc_date_time
