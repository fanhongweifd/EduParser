# coding=utf-8
import os
from models import Employee
from bs4 import BeautifulSoup
from config import Config
from mparser import ProfileParser
from mparser import get_doc_bySelenium


# @brief: 函数将过滤结果转化为Employee数据
# @tag: 输入为待处理的BeautifulSoup的tag对象
# @output:输出employee
def handler(tag):
    name = tag.get_text()
    name = ''.join(name.split())
    #name = name.replace('（', '(')
    #idx = name.find('(')
    #if idx != -1:
    #    name = name[:idx]
    return Employee(name=name, url=tag['href'])

def set_attr_hook(name,value):
    if name == 'departments':
        if len(value) > 32:
            return None
    elif name == 'email':
        if not '@' in value:
            return None
    return value

# @doc: 输入为个人详情页的整个网页源码
# @output:输出employee，如果没有检测到内容返回None          
# employee可用属性(url, name, email, tel, title, profile, research, departments,fax,addr):
def profile_handler(doc, name, url, path):
    filename = os.path.join(path, name + ".html")
    employee = Employee(name=name, url=url)

    # 只保存名称和个人主页，个人简历文件另存当前目录
    soup = BeautifulSoup(doc, Config.SOUP_PARSER)
    divs = soup.find_all(name="div", attrs={"class":"page_right addpage_right"}, limit=1)
    if not divs or len(divs) == 0:
        div= soup
    else:
        div = divs[0]
    if not os.path.exists(filename):
        with open(filename, 'wb') as fp:
            content = div.prettify()
            fp.write(content)
            fp.close()

    tds = div.find_all('td')
    if tds and len(tds) == 11:
        department =  tds[2].get_text()
        if department:
            department = ''.join(department.split())
            if department and len(department) != 0:
                employee.departments = department

        title =  tds[4].get_text()
        if title:
            title = ''.join(title.split())
            if title and len(title) != 0:
                employee.title = title

        email = tds[8].get_text()
        if email:
            email = ''.join(email.split())
            if email and len(email) != 0:
                employee.email = email

        research =  tds[10].get_text()
        if research:
            research = ''.join(research.split())
            if research and len(research) != 0:
                employee.research = research

    divs = soup.find_all(name="div", attrs={"class":"text_more"}, limit=1)
    if divs and len(divs) != 0:
        div = divs[0]
    # 使用纯文本方式处理
    lines = div.stripped_strings
    # text=div.get_text(strip=True)
    parser = ProfileParser(lines=lines,employee=employee,set_attr_hook=set_attr_hook)
    return parser.parse()
