try:
    from pynut_2files.pyNutFiles import _lib as lib
except:
    try:
        from pyNutFiles import _lib as lib
    except:
        try:
            from . import _lib as lib
        except:
            import _lib as lib
# pynut
oth =       lib.nutOther()
dat =       lib.nutDate()
dframe =    lib.nutDataframe()
fl =        lib.nutFiles()
flCopy =    lib.nutCopy()
# Others
pythoncom = lib.pythoncom()
logger =    lib.logger()
xlsxwriter = lib.xlsxwriter()
shutil =    lib.shutil()
win32 =     lib.win32()
import os, time


# ------------------------------------------------------------------------------
# DEPRECATED - Just for info
# ------------------------------------------------------------------------------
def del_Gen_py_folder(self, str_function):
    # =====================================================
    # Documentation on the subject:
    # https://gist.github.com/rdapaz/63590adb94a46039ca4a10994dff9dbe
    # https://stackoverflow.com/questions/47608506/issue-in-using-win32com-to-access-excel-file/47612742
    # =====================================================
    str_DirPath = fl.fStr_BuildPath(os.environ['USERPROFILE'], r'AppData\Local\Temp\gen_py')
    logger.warning('   (***) delete folder : {}'.format(str_DirPath))
    if fl.fBl_FolderExist(str_DirPath):
        # Delete the folder
        shutil.rmtree(str_DirPath, ignore_errors=True)
    # Re- Launch Process
    if str_function == 'FindXlApp':
        # Define again the App
        xlApp = win32.Dispatch('Excel.Application')
        self.xlApp = xlApp
        return self.xlApp
    #### CALL
    # except AttributeError as err_att:
    #     if "no attribute 'CLSIDToClassMap'" in str(err_att):
    #         logger.error('  WARNING in FindXslApp: no attribute CLSIDToClassMap || {}'.format(str(err_att)))
    #         self.del_Gen_py_folder('FindXlsApp')
    #         return self.xlApp
    #     else:
    #         logger.error('  ERROR in FindXlsApp || {}'.format(str(err_att)))
    #         raise


def fStr_createExcel_SevSh_celByCel(str_folder, str_FileName, l_dfData, l_SheetName=[]):
    """ Create a several sheets Excel file
    Input is a list of Dataframe and list of Sheet Names
    Will use xlsxwriter and fill the Excel Cell by Cell
    Performance may be pretty low
    Preferable to use the function : fStr_createExcel_SevSh
    """
    try:
        # Define Path
        if str_FileName == '':
            str_path = str_folder
        else:
            str_path = fl.fStr_BuildPath(str_folder, str_FileName)
        # Create the file (xlsxwriter cannot modify files)
        xlWb = xlsxwriter.Workbook(str_path)
        # Dataframe
        for i in range(len(l_dfData)):
            df_data = l_dfData[i]
            try:
                str_SheetName = l_SheetName[i]
            except:
                str_SheetName = ''
            # Sheet Name
            if str_SheetName != '':
                xlWs = xlWb.add_worksheet(str_SheetName)
            else:
                xlWs = xlWb.add_worksheet()
            # fill in
            for i, row in enumerate(df_data.index):
                for j, col in enumerate(df_data.columns):
                    xlWs.write(i, j, str(df_data.iat[i, j]))
                    # xlWs.Cells(i+1, j+1).Value = str(df_data.iat[i, j])
        xlWb.close()
    except Exception as err:
        logger.error('  ERROR: fl fStr__createExcel_SevSh_celByCel did not work : |{}|'.format(err))
        logger.error('  - Path : |{}|'.format(str_folder))
        logger.error('  - fileName : |{}|'.format(str_FileName))
        logger.error('  - l_SheetName : |{}|'.format('|'.join(l_SheetName)))
        try:
            xlWb.close()
        except:
            logger.error('  *** Could not close the file')
        return False
    return str_path





#=====================================================================================================================
# Deperecated and not used
#=====================================================================================================================

def fStr_fillXls_celByCel(str_path, df_data, str_SheetName='', xlWs=0, int_nbRows=0, int_rowsWhere=1):

    raise PermissionError('This function is OLD and should not be used in pynut, this is only old code kept for legacy purpose')

    # try:
    #     # If Sheet is nothing, we must define it
    #     if xlWs == 0:
    #         bl_CloseExcel = True
    #         inst_xlApp = c_win32_xlApp()
    #         inst_xlApp.FindXlApp(bl_visible=False)
    #         inst_xlApp.OpenWorkbook(str_path)
    #         xlWs = inst_xlApp.DefineWorksheet(str_SheetName, -1, str_SheetName)
    #         if xlWs == 0:
    #             logger.warning('  (--) ERROR in fillXls_celByCel: really could not find the sheet')
    #             raise
    #     else:   bl_CloseExcel = False
    # except Exception as err:
    #     logger.error('  ERROR in fl fillXls_celByCel: Could not find Excel: |{}|'.format(err))
    #     logger.error('  - Path : |{}|'.format(str_path))
    #     logger.error('  - SheetName : |{}|'.format(str_SheetName))
    #     return False
    #
    # # ------ Insert or delete ROWS ------
    # try:
    #     if int_nbRows > 0:
    #         for i in range(0, int_nbRows):      xlWs.Rows(int_rowsWhere).EntireRow.Insert()
    #     elif int_nbRows < 0:
    #         for i in range(0, -int_nbRows):     xlWs.Rows(int_rowsWhere).EntireRow.Delete()
    # except Exception as err:
    #     logger.error('  ERROR in fl fillXlscelByCel, Insert or delete ROWS: |{}|'.format(err))
    #     try:    logger.error(f'  - int_nbRows : {int_nbRows} int_rowsWhere {int_rowsWhere}')
    #     except: pass
    #     return False
    #
    # # ------ Fill Cell by Cell  ------
    # try:
    #     i_max, j_max = 1, 1
    #     for i, row in enumerate(df_data.index):
    #         for j, col in enumerate(df_data.columns):
    #             xlWs.Cells(i + 1, j + 1).Value = str(df_data.iat[i, j])
    #             j_max = j + 1
    #         i_max = i + 1
    # except Exception as err:
    #     logger.error('  ERROR in fl fStr_filXls_celByCel, Fill Cell by Cell: |{}|'.format(err))
    #     try:
    #         logger.error(f'  - i_max= {i_max}, j_max= {j_max}')
    #         logger.error(f'  - Cell value: {df_data.iat[i, j]}')
    #     except: pass
    #     return False
    #
    # # Empty the rest of the sheet
    # try:
    #     col = fDic_colNumber()[j_max]
    #     range = f"A{i_max + 1}:B{col}{i_max + 1000}"
    #     xlWs.Range(range).ClearContents()
    # except Exception as err:
    #     logger.error('  ERROR in fl fStr_filXls_celByCel: Empty the rest of the sheet: |{}|'.format(err))
    #     try:
    #         logger.error(f'  - i_max= {i_max}, j_max= {j_max}')
    #         logger.error(f'  - col= {col}')
    #         logger.error(f'  - range= {range}')
    #     except: pass
    #     return False
    #
    # # rustine depending where Function start
    # if bl_CloseExcel:
    #     try:                        inst_xlApp.Visible = True
    #     except Exception as err:    logger.error('  ERROR in fl fStr_filXls_celByCel: xlApp visible did not work | {}'.format(str(err)))
    #     try:                        inst_xlApp.CloseWorkbook(True)
    #     except Exception as err:    logger.error('  ERROR in fl fStr_filXls_celByCel: Excel workbook could not be closed | {}'.format(str(err)))
    #     try:                        inst_xlApp.QuitXlApp(bl_force=False)
    #     except Exception as err:    logger.error('  ERROR: Excel could not be closed | {}'.format(str(err)))
    # return str_path


# @oth.dec_singletonsClass
# class c_win32_xlApp:
#     """ The class allow you to manage excel with the library win32com.client
#     Open the Excel Office App, Close, Save, define / rename / create sheet, fill an area
#     The class is decorated to be a singleton so we always use the same instance of Excel
#     """
#     def __init__(self):
#         self.__wkIsOpen = False
#         self.d_wkOpen = {}
#         self.str_lastSheetName = None
#         self.fBl_ExcelIsOpen()
#
#     # =====================================================
#     @property
#     def visible(self):
#         return self.__visible
#
#     @visible.setter
#     def visible(self, bl_visible):
#         self.__visible = bl_visible
#
#     @property
#     def wb_path(self):
#         return self.__wb_path
#
#     @wb_path.setter
#     def wb_path(self, str_path):
#         self.__wb_path = str_path
#
#     # =====================================================
#
#     def fBl_ExcelIsOpen(self):
#         try:
#             self.xlApp = win32.GetActiveObject("Excel.Application")
#             self.__blXlWasOpen = True
#         except:
#             self.__blXlWasOpen = False
#
#     def FindXlApp(self, bl_visible=True, bl_gencache_EnsureDispatch=False):
#         '''Get running Excel instance if possible, else return new instance.'''
#         self.__visible = bl_visible
#         self.__gencache_EnsureDispatch = bl_gencache_EnsureDispatch
#         try:
#             xlApp = self.xlApp
#             xlApp.Visible = self.__visible
#             xlApp.Interactive = self.__visible
#             # This row only check errors (avoid prrint(xlApp))
#             # Because if Excel has been killed 'xlApp = self.xlApp' wont be an error paradoxally
#         except:
#             # prrint("No running Excel instances, returning new instance")
#             pythoncom.CoInitialize()
#             try:
#                 if self.__gencache_EnsureDispatch:
#                     xlApp = win32.gencache.EnsureDispatch('Excel.Application')
#                 else:
#                     # xlApp = win32.Dispatch('Excel.Application')
#                     xlApp = win32.DispatchEx('Excel.Application')
#                     # xlApp = win32.dynamic.Dispatch('Excel.Application')
#             except AttributeError as err_att:
#                 if "no attribute 'CLSIDToClassMap'" in str(err_att):
#                     logger.error('  WARNING in FindXlApp: no attribute CLSIDToClassMap || {}'.format(str(err_att)))
#                     self.del_Gen_py_folder('FindXlApp')
#                     return self.xlApp
#                 else:
#                     logger.error('  ERROR in FindXlApp || {}'.format(str(err_att)))
#                     raise
#         xlApp.Visible = self.__visible
#         self.xlApp = xlApp
#         return self.xlApp
#
#     def WaitFile(self, int_sec=1, str_msg=' (*-*) Wait for file to load (in c_win32_xApp)...', otherARG=''):
#         if otherARG != '':
#             logger.warning('  - ** otherARG : |{}|-|{}|'.format(otherARG, type(otherARG)))
#         logger.warning(str_msg)
#         time.sleep(int_sec)
#
#     def del_Gen_py_folder(self, str_function):
#         # =====================================================
#         # Documentation on the subject:
#         # https://gist.github.com/rdapaz/63590adb94a46039ca4a10994dff9dbe
#         # https://stackoverflow.com/questions/47608506/issue-in-using-win32com-to-access-excel-file/47612742
#         # =====================================================
#         str_DirPath = fl.fStr_BuildPath(os.environ['USERPROFILE'], r'AppData\Local\Temp\gen_py')
#         logger.warning('   (***) delete folder : {}'.format(str_DirPath))
#         if fl.fBl_FolderExist(str_DirPath):
#             # Delete the folder
#             shutil.rmtree(str_DirPath, ignore_errors=True)
#         # Re- Launch Process
#         if str_function == 'FindXlApp':
#             # Define again the App
#             xlApp = win32.Dispatch('Excel.Application')
#             self.xlApp = xlApp
#             return self.xlApp
#
#     def OpenWorkbook(self, str_path='', str_password=''):
#         if str_path != '':          self.wb_path = str_path
#         # OPEN
#         if str_password != '':
#             xlWb = self.xlApp.Workbooks.Open(self.wb_path, False, True, None, Password=str_password)
#         else:
#             xlWb = self.xlApp.Workbooks.Open(self.wb_path)
#         self.xl_lastWk = xlWb
#         # Dico - {path : obj_workbook}
#         self.d_wkOpen[self.wb_path] = xlWb
#         self.__wkIsOpen = True
#         return self.xl_lastWk
#
#     def SelectWorksheet(self):
#         xlWs = self.xl_lastWsh
#         # Authorize 10 try to add worksheet
#         for i_try in range(1, 6):
#             try:
#                 xlWs.Select
#                 return True
#             except:
#                 self.WaitFile(1, f' (**) Error on SelectWorksheet (in c_win32_xApp), try number {i_try}')
#         return False
#
#     def AddWorksheet(self, str_sheetName=''):
#         xlWb = self.xl_lastWk
#         xlWs = None
#         # Authorize 10 try to add worksheet
#         for i_try in range(1, 6):
#             try:
#                 if str_sheetName == '':
#                     xlWs = xlWb.add_worksheet()
#                 else:
#                     xlWs = xlWb.add_worksheet(str_sheetName)
#                 break
#             except:
#                 self.WaitFile(1, f' (**) Error on AddWorksheet (in c_win32_xApp), try number {i_try}')
#         # avoid further message and hussle
#         if xlWs is None:
#             raise
#         self.xl_lastWsh = xlWs
#         self.lastSheetName(str_sheetName)
#         self.SelectWorksheet()
#         return self.xl_lastWsh
#
#     def lastSheetName(self, str_sheetName):
#         # --------------------------------------------------
#         # Shitty stuff because sheet name is not recognised
#         try:
#             # Authorize 5 try to add worksheet
#             for i_try in range(1, 6):
#                 try:
#                     self.str_lastSheetName = self.xl_lastWsh.Name
#                 except:
#                     self.WaitFile(i_try, f' (**) try again self.xl_lastWsh.Name |{i_try}|')
#             if self.str_lastSheetName is None:
#                 raise
#         except Exception as Err:
#             logger.error(f'\n  Resolved ERROR in lastSheetName(c_win32_xApp) |{str_sheetName}|: {Err} \n')
#             self.str_lastSheetName = str_sheetName
#
#     def RenameSheet(self, str_sheetName=''):
#         try:
#             if str_sheetName != '':
#                 try:
#                     self.xl_lastWsh.Name = str_sheetName  # xlWs.title
#                 except:
#                     self.WaitFile(1, f' (**) Warning DefinWorkshet: canot rename Sheet: {str_sheetName}')
#         except Exception as err:
#             logger.error('  ERROR in RenameSheet || {}'.format(str(err)))
#
#     def DefineWorksheet(self, str_sheetName='', int_sheetNumber=-1, str_sheetNameToADD=''):
#         xlWb = self.xl_lastWk
#         # Name is defined
#         if str_sheetName != '':
#             try:
#                 xlWs = None
#                 # Authorize 10 try to add worksheet
#                 for i_try in range(1, 6):
#                     try:
#                         xlWs = xlWb.Sheets(str_sheetName)
#                         break
#                     except:
#                         self.WaitFile(i_try, f' (**) Err on DefineWsht (c_win32_xApp), try {i_try}')
#                 if xlWs is None:
#                     logger.warning('  \n => List of sheet')
#                     sheet_names = [sheet.Name for sheet in xlWb.Sheets]
#                     logger.warning(sheet_names)
#                     if str_sheetName in sheet_names:
#                         self.WaitFile(10, '\n ++ We can see the Sheet we want is in the list of Sheets! WTH!  ')
#                         logger.warning('  => Get the number of the Sheet')
#                         int_shNb = 1 + sheet_names.index(str_sheetName)
#                         logger.warning(f'--Find worksheet by NB |{int_shNb}|-------')
#                         xlWs = xlWb.Sheets(int_shNb)
#                         # DONT RENAME
#                         logger.warning(f'  => Indeed the name of the Sheet is : |{xlWs.Name}|')
#                     else:
#                         logger.warning('--ADD worksheet a-------')
#                         self.AddWorksheet(str_sheetNameToADD)
#                         # self.SelectWorksheet()
#                         return self.xl_lastWsh  # All defined in Add worksheet, we can get out
#                 # END
#                 self.xl_lastWsh = xlWs
#             except Exception as Err:
#                 logger.error('  ERROR in xx DefineWorksheet (c_win32_xApp): {}'.format(Err))
#                 logger.error('  - ** ARGS : |{}|-|{}|-|{}|'.format(str_sheetName))
#                 # self.lastSheetName(str_sheetName)
#                 self.str_lastSheetName = str_sheetName
#                 raise
#         else:
#             if int_sheetNumber > 0:
#                 logger.warning('--Find worksheet by number-------')
#                 try:
#                     xlWs = xlWb.Sheets(int_sheetNumber)
#                 except:  # After an error, all should have been defined in the call to add worksheet, so RETURN to get out
#                     self.WaitFile(2, ' (**) Warning on DefineWorksheet: Could not find Sheet Number : {}'.format(str(int_sheetNumber)))
#                     logger.warning('--ADD worksheet b -------')
#                     self.AddWorksheet(str_sheetNameToADD)
#                     # self.SelectWorksheet()
#                     return self.xl_lastWsh # All defined in Add worksheet, we can get out
#                 self.xl_lastWsh = xlWs
#                 # Rename the Sheet if possible (if its a recall with str_sheetName defined in str_sheetNameToADD)
#                 self.RenameSheet(str_sheetNameToADD)
#             else:
#                 logger.warning('--ADD worksheet c -------')
#                 self.AddWorksheet(str_sheetNameToADD)
#                 # self.SelectWorksheet()
#                 return self.xl_lastWsh  # All defined in Add worksheet, we can get out
#         #-----------------------------------------------------------------------------------------
#         # END
#         self.lastSheetName(str_sheetName)
#         self.SelectWorksheet()
#         return self.xl_lastWsh
#
#     def SaveAs(self, str_newPath, int_fileFormat=-1):
#         if self.__wkIsOpen:
#             # Define FileFormat
#             str_lower = str_newPath.lower()
#             if int_fileFormat == -1:
#                 if '.xlsx' in str_lower:
#                     self.__fileFormat = 51
#                 elif '.xlsb' in str_lower:
#                     self.__fileFormat = 50
#                 elif '.xlsm' in str_lower:
#                     self.__fileFormat = 52
#                 elif '.xls' == str_lower[-4:]:
#                     self.__fileFormat = 56
#                 else:
#                     self.__fileFormat = -1
#             else:
#                 self.__fileFormat = int_fileFormat
#             # Save As
#             self.__displayAlert = self.xlApp.DisplayAlerts
#             self.xlApp.DisplayAlerts = False
#             try:
#                 if self.__fileFormat == -1:
#                     self.xl_lastWk.SaveAs(str_newPath)
#                 else:
#                     self.xl_lastWk.SaveAs(str_newPath, FileFormat=self.__fileFormat)
#             except Exception as err:
#                 logger.error('  Error in SaveAs (Files): {}'.format(str(err)))
#                 raise
#             finally:
#                 self.xlApp.DisplayAlerts = self.__displayAlert
#         else:
#             logger.error('  ERROR in SaveAs (c_win32_xApp) | a WB need to be open before to bes Saved AS')
#
#     def ConvertToPdf(self, str_pdfPath=None):
#         xlWb = self.xl_lastWk
#         if str_pdfPath is None:
#             str_pdfPath = self.wb_path.replace('.xlsx', '.pdf')
#         try:
#             xlWb.ActiveSheet.ExportAsFixedFormat(0, str_pdfPath)
#         except Exception as err:
#             logger.error('  ERROR in ConvertToPdf (c_win32_xApp). Failed to convert in PDF format | {}'.format(err))
#             return False
#         return True
#
#     def CloseWorkbook(self, bl_saveBeforeClose=True):
#         self.__saveBeforeClose = bl_saveBeforeClose
#         if self.__wkIsOpen:
#             self.xl_lastWk.Close(SaveChanges=self.__saveBeforeClose)
#
#     def CheckAnyWkIsOpen(self):
#         try:
#             if self.__gencache_EnsureDispatch:
#                 xlApp2 = win32.gencache.EnsureDispatch('Excel.Application')
#             else:
#                 xlApp2 = self.xlApp
#             l_wkOpen = [wk.Name for wk in xlApp2.Workbooks]
#             d_wkOpenCopy = self.d_wkOpen.copy()
#             for path, wk in d_wkOpenCopy.items():
#                 try:
#                     wk_Name = wk.Name
#                     if not wk_Name in l_wkOpen:
#                         del self.d_wkOpen[path]
#                 except:
#                     del self.d_wkOpen[path]
#             # Conclude if any wk is open
#             if self.d_wkOpen:
#                 self.__wkIsOpen = True
#             else:
#                 self.__wkIsOpen = False
#         except Exception as err:
#             logger.error('  INFORMATION: CheckAnyWkIsOpen (Files): {}'.format(str(err)))
#             self.__wkIsOpen = False
#             self.__killExcelProcess = True
#         return self.__wkIsOpen
#
#     def Kill_Excel(self):
#         try:
#             if self.__killExcelProcess:
#                 flCopy.Act_KillExcel()
#             # -----------------------------------------------------------------------
#             elif False:  # Other things picked up on Internet
#                 if hasattr(self, 'xlBook'):
#                     logger.warning(' WARNING in Kill_Excel (Files): remaining xlBook.....')
#                     del self.xl_lastWk
#                 import gc
#                 gc.collect()
#             # -----------------------------------------------------------------------
#             else:
#                 self.xlApp.Application.Quit()
#                 # self.xlApp.Exit()
#                 del (self.xlApp)
#             # ----- restart Init for the Next Instance -----
#             self.__wkIsOpen = False
#             self.d_wkOpen = {}
#             self.__blXlWasOpen = False
#         except Exception as err:
#             logger.error('  Error in Kill_Excel (Files): {}'.format(str(err)))
#             raise
#
#     def QuitXlApp(self, bl_force=False, bl_killExcelProcess=False):
#         self.__killExcelProcess = bl_killExcelProcess
#         if bl_force:
#             if self.__wkIsOpen:
#                 try:
#                     self.CloseWorkbook()
#                 except:
#                     pass
#             self.Kill_Excel()
#         else:
#             if self.__blXlWasOpen:
#                 logger.warning(
#                     '  (*) Warning QuitXlApp(c_win32_xApp): Not closing EXCEL, a previous workbook might be still Open')
#             else:
#                 self.CheckAnyWkIsOpen()
#                 if self.__wkIsOpen:
#                     logger.warning('  (*) Warning QuitXlApp(c_win32_xApp): Not closing EXCEL, a workbook is still Open')
#                 else:
#                     self.Kill_Excel()
# # _____________________________________________________________________________________________________
#
#
#
#
# # Duplicate I put just for this old process I still need to delete
# def fDic_colNumber():
#     d_cell = {0: 'A', 1: 'A', 2: 'B', 3: 'C', 4: 'D', 5: 'E', 6: 'F', 7: 'G', 8: 'H', 9: 'I',
#               10: 'J', 11: 'K', 12: 'L', 13: 'M', 14: 'N', 15: 'O', 16: 'P', 17: 'Q', 18: 'R', 19: 'S',
#               20: 'T', 21: 'U', 22: 'V', 23: 'W', 24: 'X', 25: 'Y', 26: 'Z', 27: 'AA', 28: 'AB', 29: 'AC',
#               30: 'AD', 31: 'AE', 32: 'AF', 33: 'AG', 34: 'AH', 35: 'AI', 36: 'AJ', 37: 'AK', 38: 'AL', 39: 'AM',
#               40: 'AN', 41: 'AO', 42: 'AP', 43: 'AQ', 44: 'AR', 45: 'AS', 46: 'AT', 47: 'AU', 48: 'AV', 49: 'AW',
#               50: 'AX'}
#     return d_cell