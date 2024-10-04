import re
from string import punctuation
from bs4 import BeautifulSoup
from ferramentas_basicas_pln import removerCaracteresEspeciais as removeSpecialCharacters
from ferramentas_basicas_pln import removerEspacosEmBrancoExtras as removeExtraBlankSpaces
from be_ethical.requesting import sendRequest,validateStatusCode
from be_ethical.creating_sheet import createExcelFile

def getRobotsTxtRules(robots_txt_user_agent : str) -> tuple[bool,dict]:
    """
    If the website allows you to navigate with your crawler, it will return True on
    the first element of the tuple. The second element will tell you where you can 
    access and where you can't.
    """
    robots_txt_user_agent = robots_txt_user_agent.split('\n')
    rules = {'Allowed':[],'Restricted':[]}
    for line in robots_txt_user_agent[1:]:
        line = line.lower()
        if line.startswith('disallow:'):
            rules['Restricted'].append(line.split()[-1])
        elif line.startswith('allow:'):
            rules['Allowed'].append(line.split()[-1])
    if not rules['Restricted']:
        del(rules['Restricted'])
    if not rules['Allowed']:
        del(rules['Allowed'])
    if '*' in rules['Restricted'] or '/*' in rules['Restricted'] or '/ *' in rules['Restricted'] or '/' in rules['Restricted']:
        return False,rules
    return True,rules

def verifyRobotsTxt(root_link : str, silence : bool = True) -> str|bool:
    try:
        if not root_link.endswith('/'):
            root_link+='/'
        full_link = root_link+'robots.txt'
        response = sendRequest(full_link,silence=silence)
        if response:
            status_code = response.status_code
            if not validateStatusCode(status_code,silence=silence):
                return False
            else:
                soup = BeautifulSoup(response.content,'html.parser')
                return soup.text
        else:
            return False
    except Exception as e:
        if not silence:
            error = f'{e.__class__.__name__}: {str(e)}'
            print(f'! Trouble while verifying robots.txt with link: "{full_link}":\n--> {error}.')
        return False

def colectRobotsTxtInfo(robots_txt : str) -> str:
    desired_lines = []
    user_agent = False
    for line in robots_txt.split('\n'):
        line = line.strip()        
        if user_agent:
            if line != '':
                desired_lines.append(line)
            else:
                break
        else:
            formatted_line = line.replace(' ','').lower()
            if formatted_line.startswith('user-agent:*'):
                desired_lines.append(line)
                user_agent = True
    return '\n'.join(desired_lines)

def getScrapingPossibilities(root_link : str,
                             create_excel : bool = False,
                             excel_dir_path_to_save : str = 'here',
                             silence : bool = True) -> tuple[bool,dict]:
    robots_txt = verifyRobotsTxt(root_link=root_link,silence=silence)
    if not robots_txt:
        robots_txt_exists = False
        possibility_status = False
        scraping_rules = {}
    else:
        robots_txt_exists = True
        robots_txt_user_agent = colectRobotsTxtInfo(robots_txt)
        if robots_txt_user_agent.strip():
            possibility_status, scraping_rules = getRobotsTxtRules(robots_txt_user_agent)            
        else:
            possibility_status = True
            scraping_rules = {}
    if create_excel:
        createExcelFile(root_link,robots_txt_exists,possibility_status,scraping_rules,excel_dir_path_to_save,silence)        
    return possibility_status,scraping_rules

def getRootUrl(link):
    pattern = r'^(https?://[^/]+)'
    match = re.match(pattern, link)
    if match:
        return match.group(1)
    return None

def createRegexPatterns(restricted_urls : list[str]):
    regex_restricted_urls = []
    for restricted_url in restricted_urls:
        if restricted_url.endswith('*'):
            restricted_url = restricted_url[:-1]
        if restricted_url.startswith('/*'):
            regex_restricted_url = restricted_url.replace('/*/','.*/')
            regex_restricted_url = regex_restricted_url.replace('/*','.*/')
        else:
            regex_restricted_url = '^'+restricted_url
        if not regex_restricted_url.endswith('/'):
            regex_restricted_url += '/?'
        else:
            regex_restricted_url += '?'

        regex_restricted_url = regex_restricted_url.replace('*','.*')

        regex_restricted_url += '.*'
        regex_restricted_urls.append(regex_restricted_url)
    return regex_restricted_urls

def checkUrlPermission(link : str,scraping_possibilities : tuple[bool,dict]) -> bool:
    status_possibility, scraping_rules = scraping_possibilities
    if not status_possibility:
        return False
    else:
        rule_keys = scraping_rules.keys()
        if 'Restricted' in rule_keys:
            root_link = getRootUrl(link)
            if root_link:
                travel_link = link.split(root_link)[-1]
                for regex_restricted_url in createRegexPatterns(restricted_urls=scraping_rules['Restricted']):                    
                    if re.search(r'{x}'.format(x=regex_restricted_url),travel_link):
                        return False
    return True
