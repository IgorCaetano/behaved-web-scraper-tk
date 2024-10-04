import pandas as pd
import os
import pytz
from datetime import datetime


def getCurrentDateAndTime(time_zone : str = 'America/Sao_Paulo') -> str:
    """
    Returns a string with year_month_day_hour_minute_seconds marking when it was called.
    """
    time_zone_desired = pytz.timezone(time_zone)
    insert_date_time_brasilia = datetime.now(time_zone_desired)
    return insert_date_time_brasilia.strftime('%Y_%m_%d_%H_%M_%S')


def createExcelFile(root_link : str,
                    robots_txt_exists : bool,
                    possibility_status : bool,
                    scraping_rules : dict,
                    excel_dir_path_to_save : str,
                    silence : bool = True):
    try:
        data = {'URL':[root_link],
                'RobotsTxt_Exists':[],
                'Explicit_Allowed':[],
                'Explicit_Restricted':[],
                'Possible_Scraping':[]}
        if robots_txt_exists:
            data['RobotsTxt_Exists'].append('YES')
            if 'Allowed' in scraping_rules.keys():
                data['Explicit_Allowed'].append(', '.join(scraping_rules['Allowed']))
            else:
                data['Explicit_Allowed'].append('')
            if 'Restricted' in scraping_rules.keys():
                data['Explicit_Restricted'].append(', '.join(scraping_rules['Restricted']))
            else:
                data['Explicit_Restricted'].append('')
        else:
            if scraping_rules:
                data['RobotsTxt_Exists'].append('NO')
                data['Explicit_Allowed'].append('-')
                data['Explicit_Restricted'].append('*')
            else:
                data['RobotsTxt_Exists'].append('NO')
                data['Explicit_Allowed'].append('')
                data['Explicit_Restricted'].append('')
        if possibility_status:
            possibility_status = 'YES'
        elif not robots_txt_exists:
            possibility_status = 'MAYBE'
        else:
            possibility_status = 'NO'
        data['Possible_Scraping'].append(possibility_status)

        if excel_dir_path_to_save == 'here':
            excel_dir_path_to_save = os.getcwd()
        
        os.makedirs(excel_dir_path_to_save,exist_ok=True)
            
        full_excel_file_path_to_save = os.path.join(excel_dir_path_to_save,f'bhd_wbsp_tk_{root_link.split('://')[-1].replace('www.','').replace('.','_').replace('/','')}_'+getCurrentDateAndTime()+'.xlsx')
        df = pd.DataFrame(data)
        df.to_excel(full_excel_file_path_to_save,index=False)
        
    except Exception as e:
        if not silence:
            error = f'{e.__class__.__name__}: {str(e)}'
            print(f'! Trouble while creating the Excel file for "{root_link}":\n--> {error}.')
