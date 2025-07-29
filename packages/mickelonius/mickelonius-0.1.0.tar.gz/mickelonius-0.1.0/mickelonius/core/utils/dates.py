from datetime import datetime
from typing import Union

import pandas as pd
from pandas._libs.tslibs.offsets import Easter, Day
from pandas.tseries.holiday import AbstractHolidayCalendar, Holiday, sunday_to_monday, nearest_workday
from pandas.tseries.offsets import CustomBusinessDay


class ExampleBusinessCalendar(AbstractHolidayCalendar):
   rules = [
     Holiday('New Year', month=1, day=1, observance=sunday_to_monday),
     Holiday('Groundhog Day', month=1, day=6, observance=sunday_to_monday),
     Holiday('St. Patricks Day', month=3, day=17, observance=sunday_to_monday),
     Holiday('April Fools Day', month=4, day=1),
     Holiday('Good Friday', month=1, day=1, offset=[Easter(), Day(-2)]),
     Holiday('Labor Day', month=5, day=1, observance=sunday_to_monday),
     Holiday('Canada Day', month=7, day=1, observance=sunday_to_monday),
     Holiday('July 4th', month=7, day=4, observance=nearest_workday),
     Holiday('All Saints Day', month=11, day=1, observance=sunday_to_monday),
     Holiday('Christmas', month=12, day=25, observance=nearest_workday),
     Holiday('Juneteenth', month=6, day=19, observance=nearest_workday)
   ]


def get_bus_days(d0_str: Union[datetime, str],
                 d1_str: Union[datetime, str] = None,
                 holidays: CustomBusinessDay = None) -> pd.DatetimeIndex:
    if holidays is None:
        holidays = CustomBusinessDay(calendar=ExampleBusinessCalendar())

    # TODO: check for type and pre-process to '%Y-%m-%d' str, both d0 and d1
    if d1_str is None:
        d1_str = datetime.now().strftime('%Y-%m-%d')

    dt_index = pd.date_range(d0_str, end=d1_str, freq=holidays)
    return dt_index
    # ts = pd.Series(range(len(idx)), index=idx)
