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
np =    lib.numpy()
pd =    lib.pandas()
import math
logger = lib.logger()


#==============================================================================
# Create Dataframe
#==============================================================================
def fBl_isDataframeEmpty(df):
    """ Test if a Dataframe is empty"""
    return df.empty

def fDf_createSimpleDataframe(l_column = None, l_values = None):
    """ Create a simple dataframe to make test"""
    if l_column == None:    l_column = ['Empty_Dataframe']
    if l_values == None:    l_values = [0]
    df_data = pd.DataFrame(l_values, columns = l_column)
    return df_data

def fDf_dataframe_fromSeries(d_series):
    df_df = pd.DataFrame(d_series)
    return df_df


#==============================================================================
# Apply Style to Dataframe
#==============================================================================
def fDf_applyStyle(df_in, str_style = 'GreenRed'):
    """
    # df_whatev = fDf_createSimpleDataframe(l_column = ['a', 'b'], l_values = [[0,1], [-1,2]])
    # fDf_applyStyle(df_whatev)
    """
    # List of Function : TO BE DEFINED 1 by 1
    def highlightNumber_GreenRed(row):
        l_stylePerRow = ["background-color: red; color:white" if cell < 0
                         else "background-color: orange; color:white"  if cell == 0
                         else "background-color: green; color:white"
                         for cell in row ]        
        return l_stylePerRow
    # Condition
    if str_style == 'GreenRed':
        o_func = highlightNumber_GreenRed
    else:
        o_func = None
    return df_in.style.apply(o_func)


#--------------------------------------------------------------
# Check Dataframe are the same (identical)
#--------------------------------------------------------------
def fBl_DfAreEquals(df1, df2):
    return df1.equals(df2)

def fBl_compareDfCol(d_1, d_2, str_how = 'inner'):
    """ compare 2 dataframe (only a column)
    one a numeric column by joining the df and returning the difference """
    # Param
    df1 =           d_1['df']
    str_colJoin1 =  d_1['colJoin']
    str_col1 =      d_1['colToCompare']
    df2 =           d_2['df']
    str_colJoin2 =  d_2['colJoin']
    str_col2 =      d_2['colToCompare']
    # In case ColJoin is not the same
    df = df2[[str_colJoin2, str_col2]].copy()
    if str_colJoin1 != str_colJoin2:
        df[str_colJoin1] = df[str_colJoin2]
    # In case colToCompare are named the same
    if str_col2 == str_col1:
        df.rename(columns = {str_col2: str_col2 + '_col2'}, inplace = True)
        str_col2 = str_col2 + '_col2'
    # Join the df
    df = fDf_JoinDf(df1, df, str_colJoin1, str_how)
    # Compare, make the difference
    df['Diff'] = (df[str_col1] - df[str_col2]).apply(lambda x: round_corectPythonFlaws(x))
    # Prepare the case its not numbers to compare
    df_compare = df.loc[ df['Diff'] != 0, [str_colJoin1, str_col1, str_col2,'Diff'] ]
    int_nbRowDiff = len(df_compare)
    if int_nbRowDiff == 0:  return True, None
    else:                   return False, df_compare


#==============================================================================
# Special rounding treatment
#==============================================================================
def round_down(nb_in, decimals = 0):
    """ Use the Math Function floor() - Able to add a decimals like in Excel
    floor() rounds down. int() truncates.
    The difference is clear when you use negative numbers
    math.floor(-3.5)    -4
    int(-3.5)           -3"""
    multiplier = 10 ** int(decimals)
    Result = math.floor(nb_in * multiplier) / multiplier
    return Result

def round_up(nb_in, decimals = 0):
    """ Use the Math Function ceil() - Able to add a decimals like in Excel"""
    multiplier = 10 ** int(decimals)
    Result = math.ceil(nb_in * multiplier) / multiplier
    return Result

def round_Correction(nb_in, decimals = 0):
    try:
        nb_in = float(nb_in)
        if nb_in != 0:      flt_add = 0.5 * (nb_in/abs(nb_in))
        else:               return 0
        multiplier = 10 ** int(decimals)
        Result = int((nb_in * multiplier) + flt_add) / multiplier
    except Exception as err:    
        logger.error('  ERRROR in round_Correction: {}'.format(str(err)))
        logger.error('  - nb_in: |{}|'.format(str(nb_in)))
        logger.error('  - decimals: |{}|'.format(str(decimals)))
        try:
            logger.error('  - flt_add: |{}|'.format(str(flt_add)))
            logger.error('  - multiplier: |{}|'.format(str(multiplier)))
        except: pass
        raise
    return Result

def round_corectPythonFlaws(nb_in):
    return round_Correction(nb_in, 10)

def round_myRound(nb_in, base = 1):
    try:
        # Special treatment as 0.5 needs to be round up and not down
        if nb_in != 0:      flt_add = 10**(-6) * (nb_in / abs(nb_in))
        else:               return 0
        MyRound = base * round((nb_in + flt_add) / base)
    except Exception as err:    
        logger.error('  ERRROR in round_myRound: {}'.format(str(err)))
        logger.error('  - nb_in: |{}|'.format(str(nb_in)))
        logger.error('  - base: |{}|'.format(str(base)))
        try:
            logger.error('  - flt_add: |{}|'.format(str(flt_add)))
        except: pass
        raise
    return MyRound
    
  
#==============================================================================
# Nan
#==============================================================================
def fBl_empty_or_nan(inputValue):
    if fBl_IsNan(inputValue) is True:
        return True
    elif inputValue == '':
        return True
    elif inputValue is None:
        return True
    else:
        return False

def fBl_IsNan(inputValue):
    """ Test if a value is Nan
    Mainly from Dataframe and used with apply / lambda"""
    if isinstance(inputValue, float):
        if np.isnan(inputValue):
            return True
        if math.isnan(inputValue):
            return True
    if inputValue != inputValue:
        return True
    try:
        if str(float(inputValue)).lower() == 'nan':
            return True
    except: pass
    return False
    

#==============================================================================
# Read file for Dataframe
#==============================================================================
def fDf_readCsv_enhanced(str_path, bl_header = 'infer', str_sep = ',', l_names = None, str_encoding = None,
                         bl_parse = False, bl_unicode = False, int_quoting = 0, str_errMsg = ''):
    """ Use the pandas method read_csv
     but resolving Parse Error and will try again after displaying a message
     Also resolving UnicodeDecodeError by detecting the encoding and trying again accordingly """
    try:
        df_data = pd.read_csv(str_path, header = bl_header, sep = str_sep, names = l_names,
                              encoding = str_encoding, quoting = int_quoting)
    # -------------------------------------------------------------
    # RECURSIVE solution if second row has more columns or encoding does not recognize special Symbol like EUR
    except pd.errors.ParserError as err:
        if bl_parse is True:
            return None
        else:
            str_err =   str(err)[:-1]
            str_find =  'saw '
            str_errMsg =    str_errMsg + ' ParserError (fDf_readCsv_enhnced): |{}| \n'.format(str_err)
            int_position =  int(str_err.find(str_find)) + len(str_find)
            str_nbCol =     str_err[int_position:]
            str_errMsg =    str_errMsg + ' - Nb of columns we should have: |{}| \n'.format(str_nbCol)
            int_nbCol =     int(str_nbCol)
            df_data =       fDf_readCsv_enhanced(str_path, bl_header, str_sep, l_names = range(int_nbCol), bl_parse = True,
                                                 int_quoting = int_quoting)
            if df_data is not None:
                str_errMsg = str_errMsg + ' - Error Solved \n\n'
                logger.info(str_errMsg)
            else:
                for i_nbCol in range(int_nbCol, int_nbCol + 20):
                    df_data =   fDf_readCsv_enhanced(str_path, bl_header, str_sep, l_names = range(i_nbCol), bl_parse = True,
                                                     int_quoting = int_quoting)
                    if df_data is not None:
                        str_errMsg = str_errMsg + f' - Error Solved with {str(i_nbCol)} columns \n\n'
                        logger.info(str_errMsg)
                        break
                    else:
                        continue
                # it never worked ....
                if df_data is None:
                    str_errMsg = str_errMsg + f' - Error NEVER Solved after {str(i_nbCol)} columns \n\n'
                    logger.warning(str_errMsg)
                    str_errMsg = ''
                    raise
    except UnicodeDecodeError as err:
        if bl_unicode is True:
            return None
        else:
            str_errMsg =    str_errMsg + f' UnicodeDecodeError (fDf_readCsv_enhnced):|{err}| \n'
            with open(str_path, 'r') as f:
                str_encoding = f.encoding
                str_errMsg =    str_errMsg + f'  - Encoding of the file is actually: |{str_encoding}| \n'
            df_data =       fDf_readCsv_enhanced(str_path, bl_header, str_sep, l_names = l_names, str_encoding = str_encoding,
                                                 bl_unicode = True, int_quoting = int_quoting)
            if df_data is not None:
                str_errMsg = str_errMsg + ' - Error Solved \n\n'
                logger.info(str_errMsg)
            else:
                logger.warning(str_errMsg)
    except Exception as err:
        logger.error('   ERROR in fDf_readCsv_enhnced: other undetected: |{}|'.format(str(err)))
        logger.error('   - str_errMsg: |{}|'.format(str_errMsg))
        logger.error('   - str_path: |{}|'.format(str(str_path)))
        logger.error('   - bl_header: |{}|'.format(str(bl_header)))
        logger.error('   - str_sep: |{}|'.format(str(str_sep)))
        logger.error('   - l_names: |{}|'.format(str(l_names)))
        logger.error('   - str_encoding: |{}|'.format(str(str_encoding)))
        logger.error('   - int_quoting: |{}| - |{}|'.format(str(int_quoting), type(int_quoting) ))
        return None
    return df_data


#==============================================================================
# Operation on Dataframe
#==============================================================================
def fDf_removeDoublons(df_in, l_subset=None, bl_first=True, bl_last=False):
    """ Remove all rows that are exactly the same"""
    df = df_in.copy()
    if bl_last is True:
        df.drop_duplicates(subset=l_subset, keep='last', inplace=True)
    elif bl_first is True:
        df.drop_duplicates(subset=l_subset, keep='first', inplace=True)
    else:
        df.drop_duplicates(subset=l_subset, keep=False, inplace=True)
    return df

def fDf_showDuplicate(df_in, l_subset=None, bl_first=True, bl_last=False):
    """ Function shows duplicate"""
    df = df_in.copy()
    if bl_last is True:
        df = df[df.duplicated(l_subset, keep='last')]
    elif bl_first is True:
        df = df[df.duplicated(l_subset, keep='first')]
    else:
        df = df[df.duplicated(l_subset, keep=False)]
    # df = pd.concat(g for _, g in df.groupby(str_colID) if len(g) > 1)
    return df

def fBl_checkDfColumn_isNumber(df, str_colName):
    if df[str_colName].dtype == object:
        return False
    return True

def fDf_replaceEmptyByNan(df_in):
    df = df_in.copy()
    df.replace('', np.nan, inplace=True)
    return df

def fDf_CleanPrepareDF(df_in, l_colToBeFloat = [], l_colToDropNA = [], o_fillNA_by = -404, l_colSort = [], bl_ascending = True):
    df = df_in.copy()
    # Change Null to NA (if directly out of DB)
    df.fillna(value = np.nan, inplace = True)
    # Drop NA & fill NA to avoid any issue and bug
    if l_colToDropNA:
        df.dropna(axis = 'index', subset = l_colToDropNA, inplace = True)
    if o_fillNA_by != -404:
         df.fillna(value = o_fillNA_by, inplace = True)
    # Make sure column is float
    if l_colToBeFloat:
        for str_colToBeFloat in l_colToBeFloat:
            df[str_colToBeFloat] = df[str_colToBeFloat].astype(float)
    # Sort
    if l_colSort:
        df.sort_values(by = l_colSort, ascending = bl_ascending, inplace = True)
    return df

def fDf_DropRowsIfNa_resetIndex(df, l_colToDropNA = []):
    """ Drop the rows where all defined columns will be Nan
    And reset the index"""
    df = df.copy()
    if l_colToDropNA:   df.dropna(axis = 'index', subset = l_colToDropNA, inplace = True)
    else:               df.dropna(axis = 'index', inplace = True)
    df.reset_index(drop = True, inplace = True)
    return df

def dDf_fillNaColumn(df, str_colTarget, str_colValueToInputIfNA, str_CONST = None):
    """ Replace Nan in a column by the value in another column or a Constant """
    try:
        if str_CONST is None:
            df[str_colTarget] = df[str_colTarget].fillna(df[str_colValueToInputIfNA])
        else:
            df[str_colTarget] = df[str_colTarget].fillna(str_CONST)
    except Exception as err:   
        logger.error(' ERROR in dDf_fillNaColumn: |{}|'.format(err))
        raise
    return df

def fDf_changeDateFormat(df_in, str_colToApply, str_dateFormatInitial = '%Y%m%d', str_dateFormatWanted = '%Y-%m-%d'):
    # pd.set_option('display.max_rows', 1000)
    # If format is String, need to change it to Date
    df_result = df_in.copy()
    l_col = df_result.columns
    df_result['dte'] = pd.to_datetime(df_result[str_colToApply], format = str_dateFormatInitial)
    # Change back to string with the new format
    df_result[str_colToApply] = df_result['dte'].dt.strftime(str_dateFormatWanted)
    # df_result[str_colToApply].apply(lambda x: dat.fStr_DateToString(x, str_dateFormat = str_dateFormatWanted))
    return df_result[l_col]

def fDf_fillColUnderCondition(df, str_colToApply, ValueToApply, str_colCondition, ValueCondition = None, bl_except = False, ValueDefault = 0):
    ''' Transform DF with condition
    ValueToApply can be a value or a lambda function
    mask / 'map'
    '''
    # Add column if not here
    if not str_colToApply in df.columns:
        df[str_colToApply] = ValueDefault
    # MASK
    if bl_except:   
        df[str_colToApply]      = df[str_colToApply].mask(df[str_colCondition] != ValueCondition, ValueToApply)

    elif ValueCondition is None:
        df = dDf_fillNaColumn(df, str_colToApply, str_colCondition)

    elif '<=' in str(ValueCondition):
        ValueCondition = float(ValueCondition.replace('<=', ''))
        df[str_colToApply]      = df[str_colToApply].mask(df[str_colCondition] <= ValueCondition, ValueToApply)
    elif '<' in str(ValueCondition):
        ValueCondition = float(ValueCondition.replace('<', ''))
        df[str_colToApply]      = df[str_colToApply].mask(df[str_colCondition] < ValueCondition, ValueToApply)
    elif '>' in str(ValueCondition):
        ValueCondition = float(ValueCondition.replace('>', ''))
        df[str_colToApply]      = df[str_colToApply].mask(df[str_colCondition] > ValueCondition, ValueToApply)
    else: 
        df[str_colToApply]      = df[str_colToApply].mask(df[str_colCondition] == ValueCondition, ValueToApply)
    #df[str_colToApply] = [ValueToApply if x == ValueCondition else '-' for x in df[str_colCondition]]
    #df['Units'] = df['Units'].where(df['column'] == 'S', - df['Units'])
    return df

def fDf_replaceStringColByZero(df, str_colToApply, ValueToApply = 0):
    # df.str.replace(r'\$-', str(ValueToApply))
    # df = df.convert_objects(convert_numeric = True)
    try:
        ser = df[str_colToApply]
        ser = pd.to_numeric(ser, errors = 'coerce')
        # fill NA
        ser = ser.fillna(ValueToApply)
        df[str_colToApply] = ser
    except Exception as err:
        logger.error('   ERROR in dfram.fDf_replaceStringColByZero || {}'.format(err))
        raise
    return df

def fDf_FilterOnCol(df, str_colToApply, l_isIN = [], str_startWith = '', bl_except = False):
    if bl_except:
        if l_isIN:                  df = df[~df[str_colToApply].isin(l_isIN)].copy()
        elif str_startWith != '':   df = df[~df[str_colToApply].str.startswith(str_startWith, na = False)].copy()    
    else:
        if l_isIN:
            df = df[df[str_colToApply].isin(l_isIN)].copy()
            #df_Holdings = df_OUT_LIGHTINV[df_OUT_LIGHTINV['GTI'].isin(['S01','S39'])]
        elif str_startWith != '':
            df = df[df[str_colToApply].str.startswith(str_startWith, na = False)].copy()
            #df_Fund = df_Fund[df_Fund['colForCriteria'].str.startswith('S', na = False)].copy()
    return df

def fDf_filterNan(df, str_colToApply, bl_except = False):
    if bl_except:
        df_out = df[~df[str_colToApply].isnull()].copy()
        # df_out = df[~df[str_colToApply] == np.nan].copy()
        # df_noAn = df[~df[str_colToApply] == 'Nan'].copy()
        # df_out = fDf_Concat_wColOfDf1(df_noNa, df_noAn)
    else:               
        df_out = df[df[str_colToApply].isnull()].copy()
        # df_out = df[df[str_colToApply] == np.nan].copy()
        # df_An = df[df[str_colToApply] == 'Nan'].copy()
        # df_out = fDf_Concat_wColOfDf1(df_na, df_An)    
    return df_out


def fDf_InsertColumnOfIndex(df, int_StartNumber = 1, int_PositionOf_ColumnIndex = 0, l_colSort = [], bl_ascending = True, str_indColName = 'ind'):
    try:
        # Sort before to do anything else
        if l_colSort:
            df.sort_values(by = l_colSort, ascending = bl_ascending, inplace = True)
        # Keep the inital columns name in a list / Keep the index as well
        l_col = df.columns.tolist()
        l_index = df.index
        # Add a column of index
        df.reset_index(drop = True, inplace = True)
        df[str_indColName] = df.index + int_StartNumber
        df.index = l_index
        # re-Order the columns the the index column is not at the end
        if int_PositionOf_ColumnIndex == 0:
            df = df[[str_indColName] + l_col]
        else:
            df = df[l_col[:int_PositionOf_ColumnIndex] + [str_indColName] + l_col[int_PositionOf_ColumnIndex:]]
    except Exception as err:    
        logger.error(' ERROR in fDf_InsertColumnOfIndex: |{}| '.format(err))
        raise
    return df

def fDf_InsertRows(df, int_nbRows, int_rows):
    df_return = df
    for i in range(0, int_nbRows):
        df_line = pd.DataFrame([[''] * len(df_return.columns)], columns =  df_return.columns, index = [int_rows - 0.5])
        #df_return = pd.concat([df_return.ix[:int_rows], df_line, df_return.ix[int_rows + 1:]]).reset_index(drop=True)
        df_return = df_return.append(df_line, ignore_index = False)
        df_return = df_return.sort_index().reset_index(drop = True)
    return df_return

def fDf_InsertCol_fixedValue(df, str_colName, str_CONST, int_position=0):
    # Add a fixed value without having a pandas warning
    # -------- DONT --------------
    # df['str_colName'] = str_CONST
    # -------- But DO --------------
    # df.loc[:, str_colName] = str_CONST
    # OR
    df.insert(int_position, str_colName, str_CONST)
    return df

def fDf_MakeColumns_1stRow(df_in):
    try:
        l_column = list(df_in.columns)
        df_1stRow = pd.DataFrame([l_column], columns = l_column)
        df_return = fDf_Concat_wColOfDf1(df_1stRow, df_in)
        # df_return.reset_index(drop = True, inplace = True) 
    except Exception as err:    
        logger.error(' ERROR in fDf_MakeColumns_1stRow: |{}| '.format(err))
        raise
    return df_return

def fDf_Make1stRow_columns(df_in):
    try:
        df_return = df_in.iloc[1:].copy()
        df_return.columns = list(df_in.iloc[0])
        df_return.reset_index(drop = True, inplace = True) 
    except Exception as err:
        logger.error(' ERROR in fDf_Make1stRow_columns: |{}| '.format(err))
        return df_in
    return df_return

def fDf_Concat_wColOfDf1(df1, df2, bl_colDf2_AsARow = False, int_emptyRow = 0):
    # Intro: Prepare the DF
    if bl_colDf2_AsARow or int_emptyRow > 0:
        df_inBetween = pd.DataFrame(columns = df2.columns)
        for i in range(int_emptyRow):
            df_inBetween.loc[len(df_inBetween)] = [''] * len(df2.columns)
        if bl_colDf2_AsARow:
            df_inBetween.loc[len(df_inBetween)] = df2.columns
        df2 = pd.concat([df_inBetween, df2], ignore_index = True, sort = False)
    # CONCAT
    if len(df1.columns) >= len(df2.columns):
        df2.columns = df1.columns[:len(df2.columns)]
        df_return = pd.concat([df1, df2], ignore_index = True, sort = False)
        df_return = df_return[df1.columns]
    else:
        df2.columns = list(df1.columns) + list(df2.columns[len(df1.columns):])
        df_return = pd.concat([df1, df2], ignore_index = True, sort = False)
        df_return = df_return[df2.columns]
    return df_return

def fDf_Concat_horizontal(df1, df2, bl_colDf2_AsARow = False):
    df_return = pd.concat([df1, df2], axis = 1)
    if bl_colDf2_AsARow:
        df_inBetween = pd.DataFrame(columns = df_return.columns)
        df_inBetween.loc[len(df_inBetween)] = df_return.columns
        df_return = pd.concat([df_inBetween, df_return], ignore_index = True, sort = False)
    return df_return

def fDf_imposerStr_0apVirgule(df, str_colName, int_0apVirgule = 2):
    try:
        df_result = df.copy()
        df_result[str_colName] = pd.to_numeric(df_result[str_colName])
        df_result[str_colName] = df_result[str_colName].astype(str) + '0' * int_0apVirgule
        df_temp = df_result[str_colName].str.split('.', n = 1, expand = True)
        if int_0apVirgule == 0:
            df_result[str_colName] = df_temp[0]
        else:
            df_temp[1] = df_temp[1].str.slice(0, int_0apVirgule)
            df_result[str_colName] = df_temp[0] + '.' + df_temp[1]
    except:
        logger.error(' ERROR: fDf_imposerStr_0apVirgule did not work - it will pass without raising')
        logger.error('  ** str_colName: |{}| - int_0apVirgule: |{}| '.format(str_colName, str(int_0apVirgule)) )
        return df
    return df_result

def fDf3_unique_duplicate_missing(df_input, l_colName_subsetDuplicated = ['Isin'], str_colName_na = 'Isin', s_keep = False):
    #----------------------------------------------------
    # Split the df into 3 df, one with unique values, one with the duplicate / doublons, one with the missing values on another column
    # keep:     {‘first’, ‘last’, False}, default ‘first’
    #----------------------------------------------------
    df_data =       df_input.copy()
    # Duplicate
    df_duplicate =  df_data[df_data.duplicated( subset = l_colName_subsetDuplicated, keep = s_keep )].copy()
    # Get the rest
    df_noDupli =    df_data[ ~df_data.duplicated( subset = l_colName_subsetDuplicated, keep = s_keep )].copy()
    # Missing
    df_missing =    df_noDupli[ df_noDupli[str_colName_na].isna() ].copy()
    # Unique
    df_unique =     df_noDupli[ ~df_noDupli[str_colName_na].isna() ].copy()
    return df_unique, df_duplicate, df_missing


#-------------------------------------------
# Sub-Dataframe, find String to delimiter
#-------------------------------------------
def fInt_FindIndex(df, str_valueToFind, bl_resetIndex = False):
    logger.warning('  \n fInt__FindIndex is deprecated, replace with fL_find_index \n')
    return fL_find_index(df, str_valueToFind, bl_resetIndex)
def fL_find_index(df, str_valueToFind, bl_resetIndex=False):
    try:
        df_RowToFind = df.copy()
        if bl_resetIndex:
            df_RowToFind = df_RowToFind.reset_index(drop = True)
        # sBl_search = df_RowToFind.eq(str_valueToFind).any(1)
        # sBl_search = (df_RowToFind == str_valueToFind).any(1)
        # sBl_search = df_RowToFind.isin([str_valueToFind]).any(1)
        sBl_search = df_RowToFind.isin([str_valueToFind]).any(axis = 1)
        df_RowToFind = df_RowToFind[sBl_search]
        # df_RowToFind = df_RowToFind[df_RowToFind.iloc[:, 1] == str_valueToFind]
        l_index_RowToFind = df_RowToFind.index
    except Exception as err:
        logger.error('  ERROR in dfram fL_find_idx: |{}| - |{}| '.format(str_valueToFind, err))
        raise
    return l_index_RowToFind
def fInt_find_index(df, str_valueToFind, int_occurence = 0, bl_resetIndex = False):
    try:
        l_index_toFind = fL_find_index(df, str_valueToFind, bl_resetIndex = bl_resetIndex)
        int_row = int(l_index_toFind.values[int_occurence])
    except Exception as err:
        logger.error('  ERROR in dfram fInt_find_idx: |{}| - |{}|'.format(str_valueToFind, err))
        raise
    return int_row

def fL_find_index_like(df, str_valueToFind, bl_resetIndex=False):
    # df[df['ids'].str.contains('ball', na = False)]
    # df.set_index('ids').filter(like='ball', axis=0)
    # df.set_index('ids').filter(regex='ball$', axis=0)     # ENd by Ball
    # df.set_index('ids').filter(regex='^ball', axis=0)     # start by ball
    try:
        str_msgErr = '#'
        df_RowToFind = df.copy()
        if bl_resetIndex:
            df_RowToFind = df_RowToFind.reset_index(drop = True)
        # Loop on column
        for colum in list(df_RowToFind.columns):
            try:
                df_search = df_RowToFind[df_RowToFind[colum].str.contains(str_valueToFind, na = False)]
                l_index = df_search.index
                # SUCCESS: So we return one first column
                return l_index
            except: pass
        # Raise if it str(colum) never been found in any column
        str_msgErr = 'End of the loop, didnt find anything'
        raise
    except Exception as err:
        logger.error('  ERROR in dfram fInt_FindInd_like: |{}| - |{}| - |{}|'.format(str_valueToFind, str_msgErr, err))
        raise        
def fInt_find_index_like(df, str_valueToFind, int_occurence = 0, bl_resetIndex = False):
    try:
        l_index_toFind = fL_find_index_like(df, str_valueToFind, bl_resetIndex=bl_resetIndex)
        int_row = int(l_index_toFind.values[int_occurence])
    except Exception as err:
        logger.error('  ERROR in dfram fInt_fd_idx_like: |{}| - |{}|'.format(str_valueToFind, err))
        raise
    return int_row


def fL_FindColumn(df, str_valueToFind):
    # df_booleanIfValueOrNot = df.eq(str_valueToFind)
    # df_ValueOrNan_IfValueOrNot = df[df.eq(str_valueToFind)]
    try:
        df_ColToFind = df.copy()
        df_booleanIfValueOrNot =        df_ColToFind.isin([str_valueToFind])
        df_ValueOrNan_IfValueOrNot =    df_ColToFind[df_booleanIfValueOrNot]
        df_ColToFind =      df_ValueOrNan_IfValueOrNot.dropna(axis='columns', how='all')
        l_colNameToFind =   df_ColToFind.columns
    except Exception as err:
        logger.error('  ERROR in dfram fL_FindCol: |{}| - |{}|'.format(str_valueToFind, err))
        raise
    return l_colNameToFind
def fInt_FindColumn(df, str_valueToFind):
    try:
        l_col =             list(df.columns)
        l_colNameToFind =   fL_FindColumn(df, str_valueToFind)
        int_col =           l_col.index(l_colNameToFind[0])
    except Exception as err:
        logger.error('  ERROR in dfram fInt_FindCol: |{}| - |{}|'.format(str_valueToFind, err))
        raise
    return int_col

def fDf_FindSubDataframe(df, str_valueToFind, str_valueToEnd = '!@#$%', int_addRowsStart = 0, int_addRowsEnd = 0,
                         int_occurStart = 0, int_occurEnd = 0, bl_Make1stRow_columns = True,
                         bl_DropRowsIfNa_resetIndex = True, bl_like = False):
    # IMPORTANT Part: Take the first row and cut
    try:
        # Find the list of index (like or exact value)
        if bl_like:     l_index_RowToFind = fL_find_index_like(df, str_valueToFind)
        else:           l_index_RowToFind = fL_find_index(df, str_valueToFind)
        if not list(l_index_RowToFind):
            logger.error('  Warning: you are using fDf_FindSubDataframe but didnt find any value: #{}#. So we return the original DF'.format(str_valueToFind))
            return df
        # Start Cut DF by the first row
        int_rowStart =  l_index_RowToFind[int_occurStart] + int_addRowsStart
        df_sub =        df.loc[int_rowStart:].copy()
    except Exception as err:
        logger.error('  ERROR in dfram findSubDb start: |{}| - |{}|'.format(str_valueToFind, err))
        return df
    # Then cut at the end if needed
    try:
        # Cut with a end value
        if not str_valueToEnd == '!@#$%':
            if bl_like:     l_index_End = fL_find_index_like(df_sub, str_valueToEnd)
            else:           l_index_End = fL_find_index(df_sub, str_valueToEnd)
            if list(l_index_End):
                int_rowEnd = l_index_End[int_occurEnd] + int_addRowsEnd
                df_sub = df_sub.loc[:int_rowEnd]
    except Exception as err:
        logger.error('  ERROR in dfram findSubDb end: |{}| - |{}|'.format(str_valueToEnd, err))
        # you can return df_sub as it exists anyway
        return df_sub
    # Remove some Nan Column
    try:
        if not bl_like:
            l_colNameToFind = fL_FindColumn(df, str_valueToFind)
            if list(l_colNameToFind):
                if bl_DropRowsIfNa_resetIndex:
                    df_sub = fDf_DropRowsIfNa_resetIndex(df_sub, list(l_colNameToFind))
            else:       logger.warning(' WARNING in fDf_FindSubDataframe: could not find the column')
        # March 2021: Remove columns at the end where all is NA
        df_sub.dropna(axis = 'columns', how = 'all', inplace = True)
        # 1st columns become Title
        if bl_Make1stRow_columns:
            df_sub = fDf_Make1stRow_columns(df_sub)
    except Exception as err:
        logger.error('  ERROR in dfram findSubDb nan: |{}| - |{}| - |{}|'.format(bl_like, bl_DropRowsIfNa_resetIndex, err))
        # you can return df_sub as it exists anyway
        return df_sub
    return df_sub

def fStr_VlookUp(df, v_valueToFind, int_colNb = 2):
    """fStr_VlookUp is behaving like a vlookup on Excel
        It can search one value or a serie of value
        The input is a dataframe
        And a number of column which will be like in Excel: 2 will be next column
        Hence, we need to remove 1 to this value to adapt to Python (int_col + int(int_colNb) - 1)
    """
    # Look for only 1 Value
    if isinstance(v_valueToFind, str):
        return fStr_VlookUp(df, v_valueToFind=[v_valueToFind], int_colNb=int_colNb)
    # look for a series of values
    elif isinstance(v_valueToFind, list):
        for _valueToFind in v_valueToFind:
            try:
                int_row =       fInt_find_index(df, _valueToFind, int_occurence=0, bl_resetIndex=True)
                int_col =       fInt_FindColumn(df, _valueToFind)
                int_col2 =      int_col + int(int_colNb) - 1
                str_return =    df.iloc[ int_row, int_col2 ]
                return str_return
            except: logger.error(' No error in fStr_VlokUp: dont find the value: |{}|'.format(str(_valueToFind)))
        # out of FOR loop without finding anything
        logger.error('  ERROR in fStr_VlokUp: Could not find any value in the list: : |{}|'.format(v_valueToFind))
        pd.set_option('display.max_rows', 100)
        logger.error(df)
        return None
    else:
        logger.error('  ERROR fStr_VlokUp ** , check type v_valueToFind: |{}| - |{}| \n '.format(type(v_valueToFind), v_valueToFind))
        return None

def fStr_HlookUp(df, v_valueToFind, int_rowNb = 2):
    """fStr_HlookUp is behaving like a hlookup on Excel
            It can search one value or a serie of value
            The input is a dataframe
            And a number of column which will be like in Excel: 2 will be next column
            Hence, we need to remove 1 to this value to adapt to Python (int_row + int(int_rowNb) - 1)
        """
    # Look for only 1 Value
    if isinstance(v_valueToFind, str):
        return fStr_HlookUp(df, v_valueToFind=[v_valueToFind], int_rowNb=int_rowNb)
    # look for a series of values
    elif isinstance(v_valueToFind, list):
        for _valueToFind in v_valueToFind:
            try:
                int_row =   fInt_find_index(df, _valueToFind, int_occurence=0, bl_resetIndex=True)
                int_col =   fInt_FindColumn(df, _valueToFind)
                int_row2 =      int_row + int(int_rowNb) - 1
                str_return =    df.iloc[ int_row2, int_col ]
                return str_return
            except: logger.error(' No error in fStr_HlokUp: dont find the value: |{}|'.format(str(_valueToFind)))
        # out of FOR loop without finding anything
        logger.error('  ERROR in fStr_HlokUp: Could not find any value in the list: : |{}|'.format(v_valueToFind))
        pd.set_option('display.max_rows', 1000)
        logger.error(df)
        return None
    else:
        logger.error('  ERROR fStr_HlokUp ** , check type v_valueToFind: |{}| - |{}| \n '.format(type(v_valueToFind), v_valueToFind))
        return None

def fDf_filterMissingIsin(df_in, colName = 'Isin', bl_resetIndex = False):
    df = df_in.copy()
    # 1. DropNA
    df.dropna(axis = 'index', subset = [colName], inplace = True)
    # 2. Is Null
    df = df[~df[colName].isnull()].copy()
    # 3. If ISIN is empty string
    df = df[(df[colName] != '') ].copy()
    # reset Index ?
    if bl_resetIndex is True:
        df.reset_index(drop = True, inplace = True)
    return df
        
def fDf_getMissingIsin(df, colName = 'Isin'):
    df_na =     df[df[colName].isnull()].copy()
    df_empty =  df[(df[colName] == '') ].copy()
    # Concat
    df_isin =   fDf_Concat_wColOfDf1(df_na, df_empty)
    return df_isin


#-------------------------------------------
# Join / Merge
#-------------------------------------------
def fDf_JoinDf(df_left, df_right, str_columnON, str_how = 'inner', str_columnRightON = ''):
    # MERGE ASOF
    # https://pandas.pydata.org/pandas-docs/version/0.25.0/reference/api/pandas.merge_asof.html
    # how{‘left’, ‘right’, ‘outer’, ‘inner’}, default ‘inner’
    # https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.merge.html
    
    # Verification
    if not str_columnON in df_left.columns :
        logger.error(' ERROR  in fDf_JoinDf: Column {0} is not in left dataframe: {1}'.format(str_columnON, list(df_left.columns)))
        logger.error(df_left.head(5) )
        logger.error('\n')
        return df_left
    if str_columnRightON == '':
        if not str_columnON in df_right.columns:
            logger.error(' ERROR  in fDf_JoinDf: Column {0} is not in right dataframe: {1}'.format(str_columnON, list(df_right.columns)))
            logger.error(df_right.head(5) )
            logger.error('\n')
            return df_left
    else:
        if not str_columnRightON in df_right.columns:
            logger.error(' ERROR  in fDf_JoinDf: Column {0} is not in right dataframe: {1}'.format(str_columnRightON, list(df_right.columns)))
            logger.error(df_right.head(5) )
            logger.error('\n')
            return df_left
    # JOIN 
    try:
        if str_columnRightON == '':
            df = pd.merge(df_left, df_right, on = str_columnON, how = str_how)
        else:
            df = pd.merge(df_left, df_right, left_on = str_columnON, right_on = str_columnRightON, how = str_how)
        #df_Holds_MACI = df_Holds_MACI.join(df_Out_Fx[['Curr', 'Fx']].set_index('Curr'), on = 'Curr')
    except Exception as err:    
        logger.error(' ERROR  in fDf_JoinDf: |{}|'.format(str(err)) )
        logger.error('\n')
        return df_left
    return df


#-------------------------------------------
# GROUP BY
#-------------------------------------------
def fDf_resetIndex(df):
    df.reset_index(inplace=True)
    return df

def fDf_putBackColPivot_afGroupBy(df, str_colPivot):
    df[str_colPivot] = df.index                 # Put again the Column Pivot that disapear into index
    df.reset_index(drop = True, inplace = True) # reset_index
    df = df[[df.columns[-1]] + list(df.columns[:-1])]   # Put the col Pivot on first Position
    return df

def fDf_GroupBy(df_in, str_colPivot, str_colMeasure, d_aggPerCol = {}):
    df = fDf_CleanPrepareDF(df_in, l_colToBeFloat = [str_colMeasure], l_colToDropNA = [str_colPivot], o_fillNA_by = 0)
    # Sum is by default
    if d_aggPerCol == {}:
        d_aggPerCol = {str_colMeasure: 'sum'}
    # Group and have the colPivot as Index
    df_group = df.groupby(str_colPivot)
    # Aggregate the measures
    try:
        df = df_group.agg(d_aggPerCol)          
    except Exception as err:
        logger.error('  error in fDf_GroupBy: |{}| '.format(err))
        df = df_group[str_colMeasure].sum()
    df = fDf_putBackColPivot_afGroupBy(df, str_colPivot)
    return df

def fDf_GroupBy_sevColumns(df_in, l_colPivot, str_colMeasure, d_aggPerCol={}):
    if str_colMeasure == '':
        df = fDf_CleanPrepareDF(df_in, l_colToDropNA=l_colPivot, o_fillNA_by=0)
    else:
        df = fDf_CleanPrepareDF(df_in, l_colToBeFloat=[str_colMeasure], l_colToDropNA=l_colPivot, o_fillNA_by=0)
    # Sum is by default
    if d_aggPerCol == {}:
        d_aggPerCol = {str_colMeasure: 'sum'}
    # Group and have the colPivot as Index
    df_group = df.groupby(l_colPivot)
    # Aggregate the measures
    try:
        df = df_group.agg(d_aggPerCol)
    except Exception as err:
        logger.error('  error in fDf_GrpBy_sevCol: |{}| '.format(err))
        df = df_group[str_colMeasure].sum()
    df = fDf_resetIndex(df)
    return df

def fDf_GroupBy_multiply(df_in, str_colPivot, l_colMeasure = []):
    df = fDf_CleanPrepareDF(df_in, l_colToBeFloat = l_colMeasure, l_colToDropNA = [str_colPivot], o_fillNA_by = 1)
    # Group and have the colPivot as Index
    df_group = df.groupby(str_colPivot)
    # Aggregate the measures
    try:
        df = df_group.prod()
        # df = df_group.apply(np.prod)
    except Exception as err:
        logger.error('  error in fDf_GroupBy_multiply: |{}| '.format(err))
        raise
    df = fDf_putBackColPivot_afGroupBy(df, str_colPivot)
    return df

def fDf_GetFirst_onGroupBy(df_in, str_colPivot, str_colMeasure, bl_sort = True, l_ColSort = [], bl_ascending = False):
    df = fDf_CleanPrepareDF(df_in, l_colToBeFloat = [str_colMeasure], l_colToDropNA = [str_colPivot], o_fillNA_by = 0)
    # Get First on a Group By - 1 : Sort the value
    if l_ColSort:
        df.sort_values(by = l_ColSort, ascending = bl_ascending, inplace = True)
    elif bl_sort:
        df.sort_values(by = [str_colPivot, str_colMeasure], ascending = False, inplace = True)
    
    df_group = df.groupby(str_colPivot)                     # Group and have the colPivot as Index
    df = df_group.first()                                   # Keep only the first of the Column Pivot
    df = fDf_putBackColPivot_afGroupBy(df, str_colPivot)
    return df
    
def fDidDf_SplitDataframe(df_in, l_colTogether = ['ID']):
    dic_df = {}
    dic_value = {}
    # LOOP
    for i, row in enumerate(df_in.index):
        df_tmp = df_in.loc[row : row].copy()
        l_value = [df_in.loc[row, col] for col in l_colTogether]
        l_inOrOut = [x for x in l_value if x in dic_value]
        # NEW DF
        if l_inOrOut == []:
            dic_df[row] = df_tmp
            dic_row = {df_in.loc[row, col] : row for col in l_colTogether}
            dic_value.update(dic_row)
        #ROS TO ADD to existing DF
        else:
            int_iNumber = dic_value[l_inOrOut[0]]            
            dic_row = {df_in.loc[row, col] : row for col in l_colTogether}
            for val in dic_row.keys():
                if val not in dic_value:
                    dic_value[val] = int_iNumber
            dic_df[int_iNumber] = fDf_Concat_wColOfDf1(dic_df[int_iNumber], df_tmp, bl_colDf2_AsARow = False)
    return dic_df
