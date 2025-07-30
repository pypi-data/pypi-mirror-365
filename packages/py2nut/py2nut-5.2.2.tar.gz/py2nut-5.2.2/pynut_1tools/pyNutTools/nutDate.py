try:
    from pynut_1tools.pyNutTools import _lib as lib
except:
    try:
        from pyNutTools import _lib as lib
    except:
        try:
            from . import _lib as lib
        except:
            import _lib as lib
np =        lib.numpy()
pd =        lib.pandas()
BDay =      lib.BDay()
relativedelta = lib.relativedelta()
dateutil =  lib.dateutil()
parse =     lib.dateutil_parse()
import datetime as dt
from datetime import timezone
logger =    lib.logger()


#------------------------------------------------------------------------------
# Today
#------------------------------------------------------------------------------
def fDte_Today():
    return dt.date.today()
def fDte_Now():
    return dt.datetime.today()
def fDte_Now_GMT():
    return dt.datetime.now(timezone.utc)



#------------------------------------------------------------------------------
# Date Difference
#------------------------------------------------------------------------------
def fBl_TimeIsBetween(tm_start, tm_end, tm_toTest):
    """ fBl_TimeIsBetween let you know if a certain datetime is well between 2 others datetime """
    if tm_start <= tm_end:  bl_result = tm_start <= tm_toTest <= tm_end
    else:                   bl_result = tm_start <= tm_toTest or tm_toTest <= tm_end
    return bl_result

def fInt_dateDifference(dte_bigger, dte_lower, bl_business_days = False):
    """ fInt_dateDifference give you the difference in days between 2 dates"""
    try:
        dte_bigger =    fDte_formatToDate(dte_bigger)
        dte_lower =     fDte_formatToDate(dte_lower)
        if bl_business_days is True:
            int_dateDifference = np.busday_count(dte_lower, dte_bigger)
        else:
            int_dateDifference = (dte_bigger - dte_lower).days
    except Exception as err:
        logger.error('  ERROR in fInt_dateDifference : |{}| - |{}| - |{}|'.format(dte_bigger, dte_lower, err))
        logger.error('   ** type : |{}| - |{}|'.format(type(dte_bigger), type(dte_lower)))
        raise
    return int_dateDifference



#------------------------------------------------------------------------------
# Date Conversion / Format
#------------------------------------------------------------------------------
def fStr_DateToString(dte_date, str_dateFormat = '%Y-%m-%d'):
    try:
        if type(dte_date) == str:   return dte_date
        else:                       str_date = dte_date.strftime(str_dateFormat)
    except Exception as err:
        logger.error('  ERROR in fStr_DateToString : |{}| - |{}| - |{}|'.format(dte_date, str_dateFormat, err))
        logger.error('   ** type : |{}|'.format(type(dte_date)))
        raise
    return str_date

def fDt_formatToDateTime_numpydatetime64(numpyDateTime, str_dateFormat = '%Y-%m-%d %H:%M' ):
    try:
        dt_date = pd.to_datetime(str(numpyDateTime)).replace(tzinfo = None).strftime(str_dateFormat)
    except Exception as err:
        print('  ERROR in formatToDateTime_numpydatetime64: {}'.format(err))
        raise
    return dt_date

def fDte_formatToDate(dte_date, str_dateFormat = '%Y-%m-%d', bl_stopLoop = False):
    """ fDte_formatToDate makes sure you will have a variable with a date format
    The first Argument is the Variable (date), and the format of the string if it is a sting
    It allows you to avoid testing the type of the variable and get your get Date anyhow"""
    try:
        if type(dte_date) == str:
            dte_date = dt.datetime.strptime(dte_date, str_dateFormat)
        elif 'numpy' in str(type(dte_date)) and 'datetime' in str(type(dte_date)):
            dte_date = pd.to_datetime(str(dte_date)).replace(tzinfo = None)
        #elif type(dte_date).__module__ == np.__name__:
            #np.datetime64(dte_date).astype(datetime)
        # FINAL
        if type(dte_date) == dt.date:           dte_formatToDate = dte_date
        elif isinstance(dte_date, dt.date):     dte_formatToDate = dte_date
        else:                                   dte_formatToDate = dte_date.date()
    except Exception as err:
        if bl_stopLoop:
            logger.error('  ERROR in fDte_formatToDate : |{}|'.format(err))
            logger.error('   ** ARGS : |{}|-|{}|-|{}|-|{}|'.format(dte_date, str_dateFormat, type(dte_date), bl_stopLoop))
        else:
            try:    return fDte_formatToDate(dte_date, '%Y-%m-%d', True)
            except: logger.error('   ** ARGS : |{}|-|{}|-|{}|-|{}|'.format(dte_date, str_dateFormat, type(dte_date), bl_stopLoop))
        raise
    return dte_formatToDate

def fDte_formatToTimeStamp(dte_date):
    try:
        dte_formatToDate = dt.datetime.fromtimestamp(dte_date)
    except Exception as err:
        logger.error('  ERROR in fDte_formatToTimeStamp : |{}| - |{}|'.format(dte_date, err))
        raise
    return dte_formatToDate

def fDte_formatToDatetime(str_date, str_dateFormat = '%Y-%m-%d'):
    """ fDte_formatToDatetime makes sure you will have a variable with a datetime format
        The first Argument is the Variable (date in string), and the format of the string"""
    try:
        if type(str_date) == str:
            dte_formatToDate = dt.datetime.strptime(str_date, str_dateFormat)
        else:
            dte_formatToDate = str_date
    except Exception as err:
        logger.error('  ERROR in fDte_formatToDatetime : |{}|'.format(err))
        logger.error('   ** ARGS : |{}|-|{}|-|{}|'.format(str_date, str_dateFormat, type(str_date)))
        raise
    return dte_formatToDate

def fDte_formatToDate_auto(str_date):
    """ fDte_formatToDate_auto makes sure you will have a variable with a datetime format
    Automatically with the python-dateutil library
    The first Argument is the Variable (date in string)"""
    try:
        dte_formatToDate = dateutil.parser.parse(str_date)
    except Exception as err:
        logger.error('  ERROR in fDte_formatToDate_auto : |{}|'.format(err))
        logger.error('   ** ARGS : |{}|-|{}|'.format(str_date, type(str_date)))
        raise
    return dte_formatToDate

def fDte_timeStamp_to_epochTime(dte_timestamp):
    """ fDte_timeStamp_to_epochTime convert Datetime into epoch Time (integer seconds)"""
    try:
        try:        epochTime =     dte_timestamp.timestamp()
        except:     epochTime =     dte_timestamp.strftime('%S')
    except Exception as err:
        logger.error('  ERROR in fDte_timeStamp_to_epochTime : |{}|'.format(err))
        logger.error('   ** ARGS : |{}|-|{}|'.format(dte_timestamp, type(dte_timestamp)))
        raise
    return epochTime

def fDte_convertExcelInteger(int_dateEexcel, bl_formatDate_tuple = False):
    """ fDte_convertExcelInteger takes an integer as input,
    This is the integer you can find in Excel when it is a date
    And return the associated date  """
    try:
        dte_base1900 = dt.datetime(1900, 1, 1)
        dte_excel = dte_base1900.toordinal() + int_dateEexcel - 2
        dte_Date = dt.datetime.fromordinal(dte_excel)
        if bl_formatDate_tuple is True:
            dte_Date = dte_Date.timetuple()
    except Exception as err:
        logger.error('  ERROR in fDte_convertExcelInteger : |{}|'.format(err))
        logger.error('   ** int_dateEexcel : |{}|'.format(int_dateEexcel))
        raise
    return dte_Date

def fDte_formatMoisAnnee(dte_date):
    try:
        if type(dte_date) == str: dte_date = dt.datetime.strptime(dte_date, '%Y-%m-%d')
        dte_formatMoisAnnee = dte_date.date().strftime('%b %Y').upper()
    except Exception as err:
        logger.error('  ERROR in fDte_formatMoisAnnee : |{}|'.format(err))
        logger.error('   ** ARGS : |{}|-|{}|'.format(dte_date, type(dte_date)))
        raise
    return dte_formatMoisAnnee

def fDte_formatMoisAn(dte_date):
    try:
        if type(dte_date) == str: dte_date = dt.datetime.strptime(dte_date, '%Y-%m-%d')
        dte_formatMoisAn = dte_date.date().strftime('%b %y').upper()
    except Exception as err:
        logger.error('  ERROR in fDte_formatMoisAn : |{}|'.format(err))
        logger.error('   ** ARGS : |{}|-|{}|'.format(dte_date, type(dte_date)))
        raise
    return dte_formatMoisAn

def fStr_ConvertToString(in_var, str_DateFormat=None):
    # --------------------------------------------------------------------------
    # DATE
    if str_DateFormat is not None:
        if isinstance(in_var, dt.datetime):
            str_date = fStr_DateToString(in_var, str_DateFormat)
        elif isinstance(in_var, dt.date):
            str_date = fStr_DateToString(in_var, str_DateFormat)
        # We set a Date format but the variable is set as a string ???
        else:
            # try several conversion
            while True:
                try:
                    dt_convert = fDte_formatToDate_auto(in_var)
                    break
                except: logger.warning(f' WARNING: fDte_formatToDate_auto did not work to detect the date |{in_var}|')
                try:
                    dt_convert = fDte_convertExcelInteger(in_var)
                    break
                except: logger.warning(f' WARNING: fDte_convertExcelInteger did not work to detect the date |{in_var}|')
                try:
                    dt_convert = fDte_formatToDatetime(in_var, str_dateFormat='%Y-%m-%d')
                    break
                except: logger.warning(f' WARNING: fDte_formatToDatetime did not work to detect the date |{in_var}|')
                try:
                    dt_convert = fDte_formatToDatetime(in_var, str_dateFormat='%d/%m/%Y')
                    break
                except: logger.warning(f' WARNING: fDte_formatToDatetime did not work to detect the date |{in_var}|')
                # -----------------------------------------------------
                # END: Nothing has worked: we should try as a NON-DATE
                if fBl_isDate(in_var) is False:
                    logger.warning(f' WARNING: fBl_isDate did not work to detect the date |{in_var}|')
                    logger.warning('  PLEASE REMOVE THE DATE FORMAT Param to avoid those checks in the future !!!')
                else:
                    logger.warning(f' WARNING: fBl_isDate DETECT the date out of |{in_var}|')
                    logger.warning('  PLEASE SEND REQUEST to Dev to analysis the DATE FORMAT and treat it  !!!')
                str_date = fStr_ConvertToString(in_var, str_DateFormat=None)
                return str_date
                # -----------------------------------------------------
            str_date = fStr_DateToString(dt_convert, str_DateFormat)
        # Return for all Date
        return str_date
    # --------------------------------------------------------------------------
    elif isinstance(in_var, dt.datetime):
        logger.warning(' WARNING ConvToStr: the Var is a DATETIME but u didnt define a format to convert it to STRING')
        logger.warning(in_var)
        return fStr_DateToString(in_var, '%Y-%m-%d')
    elif isinstance(in_var, dt.date):
        logger.warning(' WARNING ConvToStr: the Var is a DATE but u didnt define a format to convert it to STRING')
        logger.warning(in_var)
        return fStr_DateToString(in_var, '%Y-%m-%d')
    elif isinstance(in_var, int):
        return str(in_var)
    elif isinstance(in_var, float):
        return str(in_var)
    elif isinstance(in_var, str):
        return in_var
    else:
        return in_var

def fFlt_transformTimeDelta_intoFloat(tm_delta, bl_day = False, bl_hour = False, bl_minutes = False ):
    try:
        if bl_day is True:
            flt_time = tm_delta.days + tm_delta.seconds/3600/24
        elif bl_hour is True:
            flt_time = 24*tm_delta.days + tm_delta.seconds/3600
        elif bl_minutes is True:
            flt_time = 24*60*tm_delta.days + tm_delta.seconds/60
        else:
            raise ValueError('transformTimeDelta_Float needs a day, hour or minutes')
    except Exception as err:
        print('  ERROR in transformTimeDelta_Float: {}'.format(err))
        raise
    return flt_time

def fDf_transformTimeDelta_intoFloat(df_data, str_col_timeDelta, str_col_float, int_divider = 86_400_000_000_000):
    try:
        df_data[str_col_float] = df_data[str_col_timeDelta].astype(np.int64) / int_divider
    except Exception as err:
        print('  ERROR in transformTimeDelta_Float: {}'.format(err))
        raise
    return df_data


#------------------------------------------------------------------------------
# Date Boolean
#------------------------------------------------------------------------------
def fBl_isDate(dte_date, fuzzy=False):
    """
    Return whether the string can be interpreted as a date.
    :param inpt: str, string to check for date
    :param fuzzy: bool, ignore unknown tokens in string if True
    """
    try:
        parse(dte_date, fuzzy = fuzzy)
        return True
    except ValueError:
        return False

def fBl_dteFirstDayMonth(dte_date):
    try:
        if type(dte_date) == str: dte_date = dt.datetime.strptime(dte_date, '%Y-%m-%d')
        if (dte_date - BDay(1)).month == dte_date.month:
            return False
    except Exception as err:
        logger.error('  ERROR in fBl_dteFirstDayMonth : |{}|'.format(err))
        logger.error('   ** ARGS : |{}|-|{}|'.format(dte_date, type(dte_date)))
        raise
    return True

def fBl_dteLastDayMonth(dte_date):
    try:
        if type(dte_date) == str: dte_date = dt.datetime.strptime(dte_date, '%Y-%m-%d')
        if (dte_date + BDay(1)).month == dte_date.month:
            return False
    except Exception as err:
        logger.error('  ERROR in fBl_dteLastDayMonth : |{}|'.format(err))
        logger.error('   ** ARGS : |{}|-|{}|'.format(dte_date, type(dte_date)))
        raise
    return True

def is_second_friday(dte_date):
    try:
        bl_is_second_friday = dte_date.weekday() == 4 and 8 <= dte_date.day <= 14
    except Exception as err:
        logger.error('  ERROR in is_second_friday : |{}|'.format(err))
        logger.error('   ** ARGS : |{}|-|{}|'.format(dte_date, type(dte_date)))
        raise
    return bl_is_second_friday

def fDte_lastFriday(dte_date):
    int_weekDay = dte_date.weekday()
    dte_last_friday = (dte_date - dt.timedelta(days = int_weekDay) + dt.timedelta(days = 4, weeks = -1))
    return dte_last_friday

def fDte_lastThursday(dte_date):
    int_weekDay = dte_date.weekday()
    dte_lastThursday = (dte_date - dt.timedelta(days = int_weekDay) + dt.timedelta(days = 3, weeks = -1))
    return dte_lastThursday


#------------------------------------------------------------------------------
# Date Calculation
#------------------------------------------------------------------------------
def fDte_AddMonth(dte_date, int_Month = 1):
    try:
        if type(dte_date) == str: dte_date = dt.datetime.strptime(dte_date, '%Y-%m-%d')
        dte_AddMonth = dte_date + relativedelta(months = int_Month)
    except Exception as err:
        logger.error('  ERROR in fDte_AddMonth : |{}|'.format(err))
        logger.error('   ** ARGS : |{}|-|{}|-|{}|-|{}|'.format(dte_date, type(dte_date), int_Month, type(int_Month) ))
        raise
    return dte_AddMonth

def fDte_AddDay(dte_date, int_Day = 1):
    try:
        if type(dte_date) == str: dte_date = dt.datetime.strptime(dte_date, '%Y-%m-%d')
        dte_AddDay = dte_date + dt.timedelta(days = int_Day)
    except Exception as err:
        logger.error('  ERROR in fDte_AddDay : |{}|'.format(err))
        logger.error('   ** ARGS : |{}|-|{}|-|{}|-|{}|'.format(dte_date, type(dte_date), int_Day, type(int_Day) ))
        raise
    return dte_AddDay 

def fDte_datePast(int_dayHisto = 1):
    _datePast = fDte_AddDay(dt.datetime.now(), - int_dayHisto)
    return _datePast

def fDte_AddBusinessDay(dte_date, int_Day = 1):
    try:
        if type(dte_date) == str: dte_date = dt.datetime.strptime(dte_date, '%Y-%m-%d')
        dte_AddDay = dte_date + BDay(int(int_Day))
    except Exception as err:
        logger.error('  ERROR in fDte_AddBusinessDay : |{}|'.format(err))
        logger.error('   ** ARGS : |{}|-|{}|-|{}|-|{}|'.format(dte_date, type(dte_date), int_Day, type(int_Day) ))
        raise
    return dte_AddDay 

def fDte_AddHour(dte_date, int_hour = 1):
    try:
        if type(dte_date) == str: dte_date = dt.datetime.strptime(dte_date, '%Y-%m-%d %H:%M %p')
        if type(dte_date) == dt.time:
            dte_AddHour = dt.time(dte_date.hour + int_hour, dte_date.minute, dte_date.second, dte_date.microsecond)
        else:
            dte_AddHour = dte_date + dt.timedelta(hours = int_hour)
    except Exception as err:
        logger.error('  ERROR in fDte_AddHour : |{}|'.format(err))
        logger.error('   ** ARGS : |{}|-|{}|-|{}|-|{}|'.format(dte_date, type(dte_date), int_hour, type(int_hour) ))
        raise
    return dte_AddHour 

def fDte_businessDay_OutOfWeekEnd(dte_date, bl_Backward = True):
    if bl_Backward is True:     # Got to friday basically
        dte_OffsetDate = fDte_AddBusinessDay(dte_date, 1)
        dte_OffsetDate = fDte_AddBusinessDay(dte_OffsetDate, -1)
    else:                       # Got to monday basically
        dte_OffsetDate = dte_date + BDay(0)
    return dte_OffsetDate


def fDte_EOM(dte_date, offset_month=0, bl_businessDay=True):
    """Function that returns the end of a month
    We can offset to select another month
    """
    dte_date = fDte_AddMonth(dte_date, int_Month=offset_month)
    return fDte_get_end_of_month_date(dte_date, bl_businessDay=bl_businessDay)

def fDte_get_end_of_month_date(dte_date, bl_businessDay: bool = True):
    """ Function that takes a Date and return the last Day of the Month """
    dte_date = fDte_AddMonth(dte_date, 1)
    first_day_of_the_month = fDte_get_first_day_of_month(dte_date, bl_businessDay=False)
    if bl_businessDay is True:
        last_day_of_month = fDte_AddBusinessDay(first_day_of_the_month, int_Day=-1)
    else:
        last_day_of_month = fDte_AddDay(first_day_of_the_month, int_Day=-1)
    return last_day_of_month

def fDte_get_first_day_of_month(dte_date, bl_businessDay: bool = True) -> dt.datetime:
    """ Function that takes a Date and return the 1st day of the Month"""
    try:
        if type(dte_date) == str:
            dte_date = dt.datetime.strptime(dte_date, '%Y-%m-%d')
        first_day_of_the_month = fDte_AddDay(dte_date, 1 - dte_date.day)
        if bl_businessDay is True:
            last_day_of_previous_month = fDte_AddDay(dte_date, dte_date.day)
            first_day_of_the_month = fDte_AddBusinessDay(last_day_of_previous_month, int_Day=1)
        else:
            first_day_of_the_month = fDte_AddDay(dte_date, 1 - dte_date.day)
    except Exception as err:
        logger.error('  ERROR in get first-day-of-month : |{}|'.format(err))
        logger.error('   ** ARGS : |{}|-|{}|'.format(dte_date, type(dte_date)))
        raise err
    return first_day_of_the_month


#------------------------------------------------------------------------------
# Offsetting Date with a Calendar
#------------------------------------------------------------------------------
def fDat_GetOffsetDate_wCalendar(dte_date, str_pyFormat, int_offset, df_Calendar = None,
                                 bl_Backward = None, bl_formatDate = False):
    try:
        if type(dte_date) == str: dte_date = dt.datetime.strptime(dte_date, '%Y-%m-%d')
        
        # 1. Treatment with No Calendar defined
        if df_Calendar is None:
            # 1.1 If no Calendar + No Offset: only do sth if DATE is week end
            if int_offset == 0:
                dte_OffsetDate = fDte_businessDay_OutOfWeekEnd(dte_date, bl_Backward = bl_Backward)
            # 1.2 Simple Offset on Business Day
            else:
                dte_OffsetDate = fDte_AddBusinessDay(dte_date, int_offset)

        # 2. We have a Calendar in a Dataframe form (we need to have the columns: |HolidayDate, PrevBusDate, NextBusDate|
        else:
            # 2.1 If no Offset, just take into account vacations
            if int_offset == 0:
                # Even with Vacation in the Calendar, we dont know where to go (D-1, D+1?) - Just get out of week end
                if bl_Backward is None:
                    dte_OffsetDate = fDte_businessDay_OutOfWeekEnd(dte_date, bl_Backward = True)
                # if Vacation, we go to D-1 or D+1
                else:
                    dte_OffsetDate = fDte_OffsetWCalendar(df_Calendar, dte_date, int_offset = 0, bl_Backward = bl_Backward)
            # 2.2 - We have a Calendar and an Offset
            else:
                dte_OffsetDate = fDte_OffsetWCalendar(df_Calendar, dte_date, int_offset)
                
        # Finally: format
        if bl_formatDate is True:
            str_OffsetDate = dte_OffsetDate
        else:
            str_OffsetDate = dte_OffsetDate.strftime(str_pyFormat)            
        # return pd.to_datetime(str_OffsetDate)
    except Exception as err:
        logger.error(' ERROR in fDat_GetOffsetDate_wCalendar: |{}|'.format(err))
        logger.error('   ** ARGS : |{}|-|{}|'.format(dte_date, type(dte_date)))
        logger.error('   ** ARGS : |{}|-|{}|'.format(str_pyFormat, type(str_pyFormat)))
        logger.error('   ** ARGS : |{}|-|{}|'.format(int_offset, type(int_offset)))
        logger.error('   ** ARGS : |{}|-|{}|'.format(bl_Backward, type(bl_Backward)))
        logger.error(df_Calendar)
        raise
    return str_OffsetDate

def fDte_OffsetWCalendar(df_Calendar, dte_date, int_offset = 0, bl_Backward = True):
    if int_offset == 0:
        if bl_Backward == False:    str_ChangeDate = 'NextBusDate'
        else:                       str_ChangeDate = 'PrevBusDate'
        dte_OffsetDate =    fDte_HolidayDate(df_Calendar, dte_date, str_ChangeDate)
    else:
        if int_offset > 0:
            bl_Backward = False
            str_ChangeDate = 'NextBusDate'
            i_offset_start = 1
        else:
            bl_Backward = True
            str_ChangeDate = 'PrevBusDate'
            i_offset_start = -1

        # loop on all day until the final Offset defined
        for _offset in range(i_offset_start, i_offset_start + int_offset, i_offset_start):
            dte_OffsetDate =    fDte_AddBusinessDay(dte_date, _offset)
            dte_OffsetDate =    fDte_HolidayDate(df_Calendar, dte_OffsetDate, str_ChangeDate)
            dte_date =          fDte_AddBusinessDay(dte_OffsetDate, - _offset)
    return dte_OffsetDate

def fDte_HolidayDate(df_Calendar, dte_date, str_ChangeDate):
    str_sqlDate = dte_date.strftime('%Y-%m-%d')
    if str_sqlDate in df_Calendar['HolidayDate'].values:
        str_OffsetDate =        df_Calendar.loc[df_Calendar['HolidayDate'] == str_sqlDate, str_ChangeDate].iloc[0]
        dte_OffsetDate =        dt.datetime.strptime(str_OffsetDate, '%Y-%m-%d')
    else:
        dte_OffsetDate = dte_date
    return dte_OffsetDate

