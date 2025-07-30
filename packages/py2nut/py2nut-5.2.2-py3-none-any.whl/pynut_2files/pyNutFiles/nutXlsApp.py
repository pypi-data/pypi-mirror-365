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
# Pynut
xlsCop =    lib.nutCopy()
XlsFmt =    lib.nutXlsFormat()
dframe = 	lib.nutDataframe()
# Other
win32 =     lib.win32()
xw =        lib.xlwings()
pythoncom = lib.pythoncom()
logger =  	lib.logger()
import time


# -----------------------------------------------------------------
# Launching Function
# -----------------------------------------------------------------
def fApp_xls_win32():
	return AppXlsBridge(AppXls_win32())


def fApp_xls_wings():
	return AppXlsBridge(AppXls_wings())


def fApp_xls_start(xl_app, path='', sheetName='', visible=False):
	xl_app.define_xls_app()
	xl_app.set_xls_option(visible, False, False)
	xl_app.OpenWorkbook(path)
	xl_app.DefineWorksheet(sheetName)
	# Other function to see
	# xl_app.AddWorksheet(sheetName)
	# xl_app.SaveBook(newPath)
	# xl_app.ConvertToPdf()
	# xlApp.CopySheetFromAnotherBook(str_pathOrigin, str_pathDest='', bl_allSheets=False, shName=1)
	# xlApp.InsertDf_inRange(df, t_cell, bl_autofitCol)


def fApp_xls_end(xl_app, saveBeforeClose=True):
	xl_app.CloseWorkbook(saveBeforeClose=saveBeforeClose)
	xl_app.QuitXlApp()


# -----------------------------------------------------------------
# API 1 : win32com.client
# -----------------------------------------------------------------
class AppXls_win32(object):
	""" The class allow you to manage excel with the library win32com.client
	Part of the bridge DP - concrete class;  Call this way:
	xlApp = AppXlsBridge(AppXls_win32)
	"""
	def __init__(self):
		# I did not see any case with True, but I leave it for documentation purpose
		self.win32_dispatchEx = True

	def getName_sheet_or_workbook(self, wk_sh):
		print('-----------------------------')
		return wk_sh.Name
	def getListSheehNames(self, bridge):
		return [sheet.Name for sheet in bridge.xl_lastWk.Sheets]
	def getListWorkbook(self, bridge):
		if self.win32_dispatchEx is True:
			xlApp = win32.gencache.EnsureDispatch('Excel.Application')
		else:
			xlApp = bridge.xlApp
		if len(xlApp.Workbooks) == 0:	return []
		else:	return [wk.Name for wk in xlApp.Workbooks]

	def define_excel_app(self, bridge):
		# If Excel is open, use it
		try:
			bridge.xlApp = win32.GetActiveObject("Excel.Application")
			bridge.XlWasOpen = True
			bridge.description_xls_app = 'GetActiveObject'
		# New Excel instance
		except:
			bridge.XlWasOpen = False
			# Need to Start Excel
			pythoncom.CoInitialize()
			try:
				if self.win32_dispatchEx is True:
					bridge.xlApp = win32.DispatchEx('Excel.Application')
					# self.xlApp = win32.dynamic.Dispatch('Excel.Application')
					bridge.description_xls_app = 'DispatchEx'
				else:
					bridge.xlApp = win32.gencache.EnsureDispatch('Excel.Application')
					bridge.description_xls_app = 'gencache.EnsureDispatch'
			except AttributeError as err_att:
				logger.error('  ERROR in define_excl_app || {}'.format(str(err_att)))
				raise
		return bridge.xlApp

	def set_excel_option(self, bridge, bl_visible=True, bl_screen_updating=True, bl_display_alerts=True):
		try:	bridge.xlApp.Visible = bl_visible
		except: logger.error(f' ERROR on setexceloption Visible')
		try:	bridge.xlApp.Interactive = bl_visible
		except: logger.error(f' ERROR on setexceloption Interactive')
		try:	bridge.xlApp.DisplayAlerts = bl_display_alerts
		except: logger.error(f' ERROR on setexceloption DisplayAlerts')

	def open_book(self, bridge, password):
		if password is None:
			bridge.xl_lastWk = bridge.xlApp.Workbooks.Open(bridge.wb_path)
		else:
			bridge.xl_lastWk = bridge.xlApp.Workbooks.Open(bridge.wb_path, False, True, None, Password=password)

	def select_sheet(self, bridge, sheetID):
		xlWs = bridge.xl_lastWk.Sheets(sheetID)
		xlWs.Select
		bridge.xl_lastWsh = xlWs
		bridge.str_lastSheetName = self.getName_sheet_or_workbook(xlWs)

	def add_sheet(self, bridge, sheetName = ''):
		wk = 		bridge.xl_lastWk
		xl_sheets = wk.Sheets
		xlWs = 		xl_sheets.Add(Before=None, After=xl_sheets(xl_sheets.Count))
		xlWs.Name = sheetName
		xlWs.Select
		bridge.xl_lastWsh = xlWs
		bridge.str_lastSheetName = self.getName_sheet_or_workbook(xlWs)

	def clear_content(self, bridge, sheet_name='', range_select=None, block_if_cell_empty: str = 'A1'):
		if sheet_name == '':
			xlWs = bridge.xl_lastWsh
		else:
			xlWs = bridge.xl_lastWk.Sheets(sheet_name)
		# None means we clear contents whatever
		try:
			if block_if_cell_empty is None:
				xlWs.Range(range_select).ClearContents()
			else:
				value_cell = bridge.xl_lastWsh.Range(block_if_cell_empty).value
				cell_is_empty = dframe.fBl_empty_or_nan(value_cell)
				if not cell_is_empty:
					xlWs.Range(range_select).ClearContents()
		except Exception as err:
			logger.error(f'  ERROR in clear-content : {err}')
			logger.error('  - sheet_name : |{}|'.format(sheet_name))
			logger.error('  - range_select : |{}|'.format(range_select))
			logger.error('  - value_A1 : |{}|{}|'.format(value_cell, cell_is_empty))
			raise err

	def save_book(self, bridge):
		bridge.xl_lastWk.Save()

	def save_as(self, bridge, newPath, file_format=None):
		# File Format
		if file_format == -1:
			file_format = get_xl32_format(newPath)
		# Turn Off the alerts
		try:
			display_alert = bridge.xlApp.DisplayAlerts
			bridge.xlApp.DisplayAlerts = False
			# SAVE
			if file_format == -1:
				bridge.xl_lastWk.SaveAs(newPath)
			else:
				bridge.xl_lastWk.SaveAs(newPath, FileFormat=file_format)
		except Exception as err:
			logger.error('  ERROR in SaveBok : {}'.format(str(err)))
			raise
		finally:
			bridge.xlApp.DisplayAlerts = display_alert

	def close_wk(self, bridge, saveBeforeClose=True):
		bridge.xl_lastWk.Close(SaveChanges=saveBeforeClose)

	def quit_excel(self, bridge):
		bridge.xlApp.Application.Quit()
		# Test if we can still get Excel
		for i in range(6):
			try:
				xlApp = win32.GetActiveObject("Excel.Application")
				time.sleep(i)
				bridge.xlApp.Application.Quit()
			except:
				return True
		logger.warning('INFO quitexcel: we could still find Excel Application after 5 attempt')
		return False

	def convert_to_pdf(self, bridge, str_pdfPath=None):
		# init
		xlWb = bridge.xl_lastWk
		# Define Name
		if str_pdfPath is None:
			str_pdfPath = bridge.wb_path.replace('.xlsx', '.pdf')
		# Convert
		try:
			xlWb.ActiveSheet.ExportAsFixedFormat(0, str_pdfPath)
		except Exception as err:
			logger.error('  ERROR in Convrt ToPdf: Failed to convert in PDF format | {}'.format(err))
			return False
		return True

	def insert_df_range(self, bridge, df, t_cell=(1, 1), bl_autofitCol=None):
		xl_sheet = bridge.xl_lastWsh
		try:
			if t_cell == (1, 1):
				for i, row in enumerate(df.index):
					for j, col in enumerate(df.columns):
						xl_sheet.Cells(i + 1, j + 1).Value = str(df.iat[i, j])
						j_max = j + 1
					i_max = i + 1
			else:
				row_init = t_cell[0]
				col_init = t_cell[1]
				for i, row in enumerate(df.index):
					for j, col in enumerate(df.columns):
						xl_sheet.Cells(i + row_init, j + col_init).Value = str(df.iat[i, j])
						j_max = j + col_init
					i_max = i + row_init
		except Exception as err:
			logger.error(f'ERROR in insertdfrange 1: |{err}|')
			logger.error(f'  - i_max= {i_max}, j_max= {j_max}')
			logger.error(f'  - Cell value: {self.df_price.iat[i, j]}')
			raise err
		# Empty the rest of the sheet
		try:
			col = XlsFmt.fDic_colNumber()[j_max]
			range = f"A{i_max + 1}:B{col}{i_max + 1000}"
			xl_sheet.Range(range).ClearContents()
		except Exception as err:
			logger.error(f'ERROR in insertdfrange, Empty the rest of the sheet: |{err}|')
			logger.error(f'  - i_max= {i_max}, j_max= {j_max}')
			logger.error(f'  - col= {col}, range: {range}')
			raise err

	def copy_sh_from_another_book(self, bridge, str_pathOrigin, str_pathDest='', bl_allSheets=False, shName=1):
		logger.error('ERROR: copy_sh_from_another book is only defined for Xlwings, not for Win32')
	def execute_macro(self, bridge, str_macroName, o_arg=None):
		logger.error('ERROR: execute macro is only defined for Xlwings, not for Win32')


# -----------------------------------------------------------------
# API 2 : xlwings
# -----------------------------------------------------------------
class AppXls_wings(object):
	""" The class allow you to manage excel with the library xlwings which might work better than win32
	DOC: https://docs.xlwings.org/en/stable/api.html
	Part of the bridge DP - concrete class;  Call this way:
	xlApp = AppXlsBridge(AppXls_wings)
	"""
	def __init__(self):
		# initiate the Xl ID
		self.xlApp_wingsId = -1

	def getName_sheet_or_workbook(self, wk_sh):
		return wk_sh.name
	def getListSheehNames(self, bridge):
		return [sheet.name for sheet in bridge.xl_lastWk.sheets]
	def getListWorkbook(self, bridge):
		xlApp = bridge.xlApp
		if len(xlApp.books) == 0:	return []
		else:	return [wk.name for wk in xlApp.books]

	def define_excel_app(self, bridge):
		try:
			self.xlApp_s = xw.apps
			if not self.xlApp_s:
				raise
			bridge.XlWasOpen = True
		except:
			bridge.XlWasOpen = False
		self.define_right_excel_session(bridge)

	def define_right_excel_session(self, bridge):
		# New Excel instance: Either Error (no excel open) or session not defined
		if self.xlApp_wingsId == -1:
			try:
				bridge.xlApp = xw.apps.add()	# or xw.App()
			except Exception as err:
				logger.error('  ERROR in define right Xls session || {}'.format(str(err)))
				raise err
			self.xlApp_wingsId = int(bridge.xlApp.pid)
			bridge.description_xls_app = 'xw.apps.add'
		# We already got out own session
		else:
			try:
				bridge.xlApp = self.xlApp_s[int(self.xlApp_wingsId)]
				bridge.description_xls_app = 'Look for wings Id'
			except:
				# Add a new session
				logger.warning(' Warning: Do not touch Excel while running. Script will create a new XLS session ')
				bridge.xlApp = None
				self.xlApp_wingsId = -1
				self.define_right_excel_session(bridge)

	def set_excel_option(self, bridge, bl_visible=True, bl_screen_updating=True, bl_display_alerts=True):
		bridge.xlApp.visible = bl_visible
		bridge.xlApp.screen_updating = bl_screen_updating
		bridge.xlApp.display_alerts = bl_display_alerts

	def open_book(self, bridge, password):
		if password is None:
			bridge.xl_lastWk = bridge.xlApp.books.open(bridge.wb_path)
		else:
			logger.error(' ERROR: Password protected xls are not set for xlWings lib, try win32 instead')
			raise

	def select_sheet(self, bridge, sheetID):
		# xlWings takes sheet position as a dico
		if isinstance(sheetID, int):
			sheetID = sheetID - 1
		xlWs = bridge.xl_lastWk.sheets[sheetID]
		xlWs.select()
		bridge.xl_lastWsh = xlWs
		bridge.str_lastSheetName = self.getName_sheet_or_workbook(xlWs)

	def add_sheet(self, bridge, sheetName = ''):
		wk = 		bridge.xl_lastWk
		xl_sheets = wk.sheets
		xlWs = 		xl_sheets.add(name=sheetName, before=None, after=xl_sheets(xl_sheets.count))
		# before and after were never used, but keep them, for documentation
		xlWs.select()
		bridge.xl_lastWsh = xlWs
		bridge.str_lastSheetName = self.getName_sheet_or_workbook(xlWs)

	def clear_content(self, bridge, sheet_name='', range_select=None, block_if_cell_empty: str = 'A1'):
		if sheet_name == '':
			xlWs = bridge.xl_lastWsh
		else:
			xlWs = bridge.xl_lastWk.sheets[sheet_name]
		# None means we clear contents whatever
		try:
			if block_if_cell_empty is None:
				xlWs.range(range_select).clear_contents()
			else:
				value_cell = bridge.xl_lastWsh.range(block_if_cell_empty).value
				cell_is_empty = dframe.fBl_empty_or_nan(value_cell)
				if not cell_is_empty:
					xlWs.range(range_select).clear_contents()
		except Exception as err:
			logger.error(f'  ERROR in clear-content : {err}')
			logger.error('  - sheet_name : |{}|'.format(sheet_name))
			logger.error('  - range_select : |{}|'.format(range_select))
			logger.error('  - value_A1 : |{}|{}|'.format(value_cell, cell_is_empty))
			raise err

	def save_book(self, bridge):
		bridge.xl_lastWk.save()

	def save_as(self, bridge, newPath, file_format=None, display_alert = None):
		# Turn Off the alerts
		try:
			display_alert = bridge.xlApp.display_alerts
			bridge.xlApp.display_alerts = False
			# SAVE
			bridge.xl_lastWk.save(newPath)
		except Exception as err:
			logger.error('  ERROR in SaveBok : {}'.format(str(err)))
			raise
		finally:
			bridge.xlApp.display_alerts = display_alert

	def close_wk(self, bridge, saveBeforeClose=True):
		if saveBeforeClose is True:
			self.save_book(bridge)
		bridge.xl_lastWk.close()

	def quit_excel(self, bridge):
		bridge.xlApp.quit()
		self.xlApp_wingsId = -1
		# Test if we can still get Excel
		for i in range(6):
			try:
				xlApp_s = xw.apps
				time.sleep(i)
				bridge.xlApp.quit()
			except:
				return True
		logger.warning('INFO quitexcel: we could still find xw.apps after 5 attempt')
		return False

	def convert_to_pdf(self, bridge, str_pdfPath=None):
		logger.error('ERROR: convert_to_pdf is only defined for Win32, not for Xlwings')

	def copy_sh_from_another_book(self, bridge, str_pathOrigin, str_pathDest='', bl_allSheets=False, shName=1):
		# BOOKS
		try:
			if str_pathDest != '':      bridge.wb_path = str_pathDest
			xl_origin = 	bridge.OpenWorkbook(str_pathOrigin)
			xl_dest = 		bridge.OpenWorkbook(str_pathDest)
		except Exception as err:
			logger.error(f'ERROR: copy sh from another book  |{err}|')
			raise
		# SHEETS
		try:
			int_lastSheet = int(len(xl_dest.sheets))
			if bl_allSheets is True:
				l_sheets = xl_origin.sheets
				for o_sheet in l_sheets:
					o_sheet.api.Copy(After=xl_dest.sheets(int_lastSheet).api)
			elif isinstance(shName, list):
				for _shName in shName:
					o_sheet = xl_origin.sheets(_shName)
					o_sheet.api.Copy(After=xl_dest.sheets(int_lastSheet).api)
			else:
				o_sheet = xl_origin.sheets(shName)
				o_sheet.api.Copy(After=xl_dest.sheets(int_lastSheet).api)
		except Exception as err:
			logger.error(f'ERROR: fl Copy Sheet From Another Bok- SHEETS |{err}|')
			raise

	def insert_df_range(self, bridge, df, t_cell=(1, 1), bl_autofitCol=False):
		''' t_cell argument can be : |'A1:C3'|, |(1,1), (3,3)|, |'NamedRange'|, |xw.Range('A1'), xw.Range('B2')|
		** https://docs.xlwings.org/en/stable/converters.html
		'''
		xl_sheet = bridge.xl_lastWsh
		if t_cell == (1, 1):
			xl_sheet.range('A1').options(index=False, header=False).value = df
		else:
			xl_sheet.range(t_cell).options(index=False, header=False).value = df
		# Autofits the width of either columns, rows or both on a whole Sheet.
		if bl_autofitCol:
			xl_sheet.autofit('columns')

	def execute_macro(self, bridge, str_macroName, o_arg=None):
		# Just keep it for documentation, not used or tested
		vb_function = bridge.xlApp.macro(str_macroName)
		o_result = vb_function(o_arg)
		return o_result


#-----------------------------------------------------------------
# BRIDGE
#-----------------------------------------------------------------
class AppXlsBridge(object):
	"""The class allow you to manage excel with different libraries
	It is the Abstract Bridge which you can call other Concrete class from, as:
	xlApp = AppXlsBridge(AppXls_win32)
	xlApp = AppXlsBridge(AppXls_wings)
	"""
	def __init__(self, xlAppApi):
		self._xlAppApi = xlAppApi
		self.xlApp = None
		self.description_xls_app = ''
		self.XlWasOpen = None
		self.wb_path = ''
		self.xl_lastWk = None
		self.d_wkOpen = {}
		self.xl_lastWsh = None
		self.str_lastSheetName = None
		self.wkIsOpen = False

	def define_xls_app(self):
		self._xlAppApi.define_excel_app(self)

	def set_xls_option(self, bl_visible=True, bl_screen_updating=True, bl_display_alerts=True):
		if not self.xlApp is None:
			self._xlAppApi.set_excel_option(self, bl_visible, bl_screen_updating, bl_display_alerts)

	def OpenWorkbook(self, path='', password=None):
		if path != '':
			self.wb_path = path
		self._xlAppApi.open_book(self, password)
		self.d_wkOpen[self.wb_path] = self.xl_lastWk
		self.wkIsOpen = True
		return self.xl_lastWk

	def DefineWorksheet(self, sheetName='', sheetNumber=-1, stop_fail=False):
		# What do we use to define the sheet
		if sheetName != '':			sheetID = sheetName
		elif sheetNumber > 0:		sheetID = sheetNumber
		else:
			logger.warning('--ADD worksheet 1 -------')
			self.AddWorksheet('pynutCreated')
			return self.xl_lastWsh
		# Authorize 10 try to add worksheet
		for i_try in range(1, 10):
			try:
				self._xlAppApi.select_sheet(self, sheetID)
				break
			except:
				WaitFile(i_try, f' (**) No-Err on DefineWsht to select sheet |{sheetID}| - try |{i_try}|')
		# If we still could not define the sheet, then we need to add the sheet another way
		if self.xl_lastWsh is None:
			if stop_fail is True:
				raise ValueError(f' Could not select sheet |{sheetID}|')
			else:
				logger.warning(' INFO: ApXlsBridg will use DefineSheetFailManagement')
				self.DefineSheet_FailManagement(sheetName=sheetName)
		return self.xl_lastWsh

	def AddWorksheet(self, sheetName=''):
		sheet_names = self._xlAppApi.getListSheehNames(self)
		# Authorize 10 try to add worksheet
		for i_try in range(1, 6):
			try:
				if sheetName in sheet_names:
					logger.error(f'  ERROR in xx AddWorkshet: {sheetName} is already present in the book')
					sheetName = sheetName + '0'
				self._xlAppApi.add_sheet(self, sheetName=sheetName)
				break
			except Exception as err:
				WaitFile(i_try, f' (**) No-Err on AddWorksht - try {i_try}')
				Err = err
		# If we still could not Add the sheet, we need to raise at this point
		if self.xl_lastWsh is None:
			logger.error('  ERROR in xx AddWorkshet: {}'.format(Err))
			raise Err
		return self.xl_lastWsh

	def ClearContentSheet(self, sheet_name='', range_select=None, block_if_cell_empty=None):
		self._xlAppApi.clear_content(self, sheet_name=sheet_name, range_select=range_select, block_if_cell_empty=block_if_cell_empty)

	def SaveBook(self, newPath='', file_format=-1):
		# Xls need to be Open
		if self.wkIsOpen is False:
			logger.error('  ERROR in SaveBok | a WB need to be open before to be Save')
			raise
		# Just SAVE
		if newPath == '':
			self._xlAppApi.save_book(self)
			return True
		# SAVE AS
		self._xlAppApi.save_as(self, newPath, file_format)

	def CloseWorkbook(self, saveBeforeClose=True):
		if self.wkIsOpen is True:
			self._xlAppApi.close_wk(self, saveBeforeClose)
			self.wkIsOpen = False
			time.sleep(3)

	def QuitXlApp(self, bl_force=False, bl_killExcelProcess=False):
		# Close the book
		try:
			self.CloseWorkbook(saveBeforeClose=True)
		except Exception as err:
			logger.error('  ERROR in CloseWorkbook : Excel wk could not be closed | {}'.format(err))
		# when we quit Excel, we want to put back the visibility and screenUpdate to avoid user confusion
		try:
			self.set_xls_option(bl_visible=True, bl_screen_updating=True, bl_display_alerts=True)
		except Exception as err:
			logger.error('  ERROR in set_xls_option : Excel could not be visible again | {}'.format(err))
		# see what we do with Excel
		if bl_killExcelProcess is True:
			self.QuitExcel()
			self.KillExcel()
		elif bl_force is True:
			self.QuitExcel()
		else:
			if self.XlWasOpen:
				logger.warning('  (*) Warning QuitXl App: Not closing EXCEL, a previous wk might be still Open')
			else:
				self.CheckAnyWkIsOpen()
				if self.wkIsOpen:
					logger.warning('  (*) Warning QuitX lApp: Not closing EXCEL, a workbook is still Open')
				else:
					self.QuitExcel()

	# -----------------------------------------------------------------
	# -- Function only called from here--------------------------------
	def DefineSheet_FailManagement(self, sheetName=''):
		try:
			logger.warning('  \n => List of sheet')
			sheet_names = self._xlAppApi.getListSheehNames(self)
			logger.warning(sheet_names)
			sheetName = str(sheetName)
			# For this one, we need a name, makes no sense if it fails with just a Sheet Number
			if sheetName == '':
				raise
			if sheetName in sheet_names:
				WaitFile(10, '\n ++ We can see the Sheet we want is in the list of Sheets! WTH!  ')
				logger.warning('  => Get the number of the Sheet')
				int_shNb = 1 + sheet_names.index(sheetName)
				logger.warning(f'--Find worksheet by NB |{int_shNb}|-------')
				self.DefineWorksheet('', sheetNumber=int_shNb, stop_fail=True)
				logger.warning(f'  => Indeed the name of the Sheet is : |{self.str_lastSheetName}|')
			else:
				logger.warning('--ADD workshet 2 -------')
				self.AddWorksheet(sheetName)
		except Exception as Err:
			logger.error('  ERROR in xx DefineWorkshet Fail mgt: {}'.format(Err))
			logger.error(f'  ** ARGS : |{sheetName}|')
			raise

	def QuitExcel(self):
		try:
			if self.xlApp is None:
				pass
			else:
				self._xlAppApi.quit_excel(self)
				self.xlApp = None
			self.wkIsOpen = False
			self.d_wkOpen = {}
			self.XlWasOpen = False
			# self.xl_lastWk = None
		except Exception as err:
			logger.error('  Error in QuitExcl: {}'.format(err))

	def KillExcel(self):
		xlsCop.Act_KillExcel()

	def CheckAnyWkIsOpen(self):
		try:
			l_wkOpen = self._xlAppApi.getListWorkbook(self)
			if len(l_wkOpen) > 0:
				logger.warning(' List of open Workbook: {}'.format(l_wkOpen))
			# read through the dico of all Workbook open
			d_wkOpenCopy = 	self.d_wkOpen.copy()
			for path, wk in d_wkOpenCopy.items():
				try:
					wk_Name = path.split('\\')[-1]
					# wk_Name = self._xlAppApi.getName_sheet_or_workbook(wk)
					if not wk_Name in l_wkOpen:
						del self.d_wkOpen[path]
				except: del self.d_wkOpen[path]
			# Conclude if any wk is open
			if self.d_wkOpen:	self.wkIsOpen = True
			else:				self.wkIsOpen = False
		except Exception as err:
			logger.error('  INFORMATION: CheckAnyWkIsOpn: {}'.format(err))
			self.wkIsOpen = False
		return self.wkIsOpen

	# -----------------------------------------------------------------
	# -- Function only for one of the library--------------------------
	def ConvertToPdf(self, str_pdfPath=None):
		self._xlAppApi.convert_to_pdf(self, str_pdfPath)

	# 	ONLY for XLWINGS
	def CopySheetFromAnotherBook(self, str_pathOrigin, str_pathDest='', bl_allSheets=False, shName=1):
		# TODO: Test
		self._xlAppApi.copy_sh_from_another_book(self, str_pathOrigin, str_pathDest, bl_allSheets=bl_allSheets, shName=1)
		# SAVE
		self.QuitXlApp()

	def InsertDf_inRange(self, df, t_cell=(1, 1), bl_autofitCol=False):
		self._xlAppApi.insert_df_range(self, df, t_cell=t_cell, bl_autofitCol=bl_autofitCol)

	def ExecuteMacro(self, str_macroName, o_arg=None):
		# NEVER used
		self._xlAppApi.execute_macro(self, str_macroName, o_arg=o_arg)


#-----------------------------------------------------------------
# Extern function
#-----------------------------------------------------------------
def WaitFile(int_sec=1, str_msg=' (*-*) Wait for: ', otherARG=''):
	if otherARG != '':
		logger.warning(f'  - ** otherARG : |{otherARG}|-|{type(otherARG)}|')
	logger.warning(f'{str_msg} {str(int_sec)} secondes')
	time.sleep(int_sec)

def get_xl32_format(xls_path):
	str_lower = xls_path.lower()
	if '.xlsx' in str_lower:
		file_format = 51
	elif '.xlsb' in str_lower:
		file_format = 50
	elif '.xlsm' in str_lower:
		file_format = 52
	elif '.xls' == str_lower[-4:]:
		file_format = 56
	else:
		file_format = -1
	return file_format


# # -----------------------------------------------------------------
# # BRIDGE Notes
# # -----------------------------------------------------------------
# def callBridge():
# 	circle1 = Circle(Api1(), 10)
# 	circle1.draw()
# class Api1(object):
# 	"""Implementation-specific abstraction: concrete class one"""
# 	def draw_circle(self, x):
# 		print(f"API 1 with {x}")
# class Api2(object):
# 	"""Implementation-specific abstraction: concrete class two"""
# 	def draw_circle(self, x):
# 		print(f"API 2 with {x}")
# class Circle(object):
# 	"""Implementation-independent abstraction: for example, there could be a rectangle class!"""
# 	def __init__(self, drawing_api, x):
# 		"""Initialize the necessary attributes"""
# 		self._drawing_api = drawing_api
# 		self._x = x
# 		self._y = None
# 	def draw(self):
# 		"""Implementation-specific abstraction taken care of by another class: DrawingAPI"""
# 		self._drawing_api.draw_circle(self._x)
# 	def scale(self, y):
# 		"""Implementation-independent"""
# 		self._y *= y
