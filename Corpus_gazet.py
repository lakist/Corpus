import urllib.request
import io
import os
import re
import html
import sys
        
#       _скачивание страницы_
def download_page(pageUrl):
    try:
        page = urllib.request.urlopen(pageUrl)
        text = page.read().decode('utf-8')
        return(text)
    except:
#        print('Error at', pageUrl)
        return(-1)


#       _очистка текста_
def clean_page(text):
    description = re.compile('<div class="b-object__detail__annotation">.*?</div>', flags=re.DOTALL) 
    description = description.findall(text)
    description = str(description) # описание статьи
    if description.find("<p>")>0: # чтобы описание не повторялось два раза
        description = ""
    description = description[description.find(">")+1:description.rfind("<")]
    
    st=re.compile('<p>.*?</p>', flags=re.DOTALL)
    text = st.findall(text) # текст статьи
    regTag = re.compile('<.*?>', flags=re.DOTALL) 
    regScript = re.compile('<script>.*?</script>', flags=re.DOTALL)
    regComment = re.compile('<!--.*?-->', flags=re.DOTALL)
    regMdash = re.compile('&mdash;', flags=re.DOTALL)
    text = regMdash.sub("–", str(text)) # заменяем тире
    description = regMdash.sub("–", description) # заменяем тире
    text = regScript.sub("", text) # удаляем скрипты
    text = regComment.sub("", text) # удаляем комментарии
    text = regTag.sub("", text) # удаляем тэги
    # дочищаем текст
    newText = '' 
    for line in text.split('\r\n'):
        line = html.unescape(line.strip('\t '))
        if line:
            if newText != '':
                newText = newText + '\r\n' + line
            else:
                newText = line
    a=newText.find ('Редакция газеты «Знамя Октября»:')
    newText=newText[2:a-4]
    newText=newText.replace ("\',", "")
    newText=newText.replace ("\'", "")
    newText=newText.replace ("  ", " ")
    newText=description + newText
    return(newText)


#       _автор_
def author_(text):
    author=re.compile('<span class="b-object__detail__author__name">.*?</span>', flags=re.DOTALL)
    author = author.findall(text) 
    regComment = re.compile('<.*?>', flags=re.DOTALL)
    author = regComment.sub("", str(author))
    regQuot = re.compile('&quot;', flags=re.DOTALL) 
    author = regQuot.sub("", str(author))
    author = author[2:-2]
    if author == '': # если автора нет
        author = 'Noname'
    if author[-1] == '.':
        author = author[0:-1]
    return(author)


#       _дата_
def date_(text):
    date = re.compile('<span class="b-object__detail__issue__date">.*?</span>.', flags=re.DOTALL)
    date = date.findall(text)
    regComment = re.compile('<.*?>', flags=re.DOTALL)
    date = regComment.sub("", str(date))
    date = date[2:-5]
    return(date)


#       _топик_
def topic_(text):    
    topic = re.compile('category=.*?\".*?</a></li>', flags=re.DOTALL)
    topic = topic.findall(text)
    regComment = re.compile('<.*?>', flags=re.DOTALL)
    topic = regComment.sub("", str(topic))
    topic = topic[topic.find(">"):-2]
    return(topic)


#       _название_
def title_(text): 
    title = re.compile('<meta name="title" content=".*?"/>', flags=re.DOTALL)
    title = title.findall(text)
    title = str(title)
    title = title[title.rfind("=")+2:-5]
    return(title)


#       _распределение по каталогу_
def direct(page):
    # создание директорий
    path = "/Corpus"
    os.chdir(path)
    if not os.path.exists("plain"):
        os.makedirs("plain")
    if not os.path.exists("mystem-plain"):
        os.makedirs("mystem-plain")
    if not os.path.exists("mystem-xml"):
        os.makedirs("mystem-xml")
    path = "/Corpus/plain"
    os.chdir(path)
    clean = clean_page(page) #неразмеченный очищенный текст
    date = date_(page) # дата
    year = date[6:] # год
    month = date[4:-5] # месяц
    # создание директорий
    if not os.path.exists(str(year)):
        os.makedirs(str(year))
    path = path + os.sep + str(year)
    os.chdir(path)
    if not os.path.exists(str(month)):
        os.makedirs(str(month))
    path = path + os.sep + str(month)
    os.chdir(month)
    files = os.listdir()
    # создание файлов с неразмеченным текстом
    ouf=open(str(len(files))+".txt", "w", encoding="utf-8")
    ouf.write(clean)
    ouf.close()
    return (str(len(files)))


#       _разметка текста_    
def mystem(page, file):
    date = date_(page) #дата
    year = date[6:] #год
    month = date[4:-5] #месяц
    # создание директорий
    path = "/Corpus/mystem-plain/"
    os.chdir(path)
    if not os.path.exists(year):
        os.makedirs(year)
    path = "/Corpus/mystem-plain/" + year
    os.chdir(path)
    if not os.path.exists(month):
        os.makedirs(month)
    path = "/Corpus/mystem-xml/"
    os.chdir(path)
    if not os.path.exists(year):
        os.makedirs(year)
    path = "/Corpus/mystem-xml/" + year
    os.chdir(path)
    if not os.path.exists(month):
        os.makedirs(month)
    path = year + os.sep + month + os.sep
    # создание файлов с размеченным текстом
    os.system(r"/Users/lakist/mystem" + " /Corpus/plain/" + path + file + ".txt" + " /Corpus/mystem-plain/" + path + file + ".txt")
    os.system(r"/Users/lakist/mystem" + " -cgin --format xml" + " /Corpus/plain/" +  path + file + ".txt" + " /Corpus/mystem-xml/" + path + file+".xml")
    return (0)


#       _информация о статье_            
def info(page, filename, url):
    info = "@au " + author_(page) + "\n" +  "@ti " + title_(page) + "\n" + "@da " + date_(page) + "\n" + "@topic " + topic_(page) + "\n" + "@url " + url
    ouf=open((filename)+".txt", "w", encoding="utf-8")
    ouf.write(info)
    ouf.close()
    return (0)


#       _создание метатаблицы_
def meta(page, url, file):
    tablePath = 'metadata.csv'
    path = "/Corpus"
    os.chdir(path)
    if not os.path.isfile(tablePath):
        create = open(tablePath, 'w', encoding='utf-8')
        create.close()
    table = open(tablePath, 'a', encoding='utf-8')
    infoString = '%s\t%s\t\t\t%s\t%s\tпублицистика\t\t\t%s\t\tнейтральный\tн-возраст\tн-уровень\tрегиональная\t%s\tЗнамя Октября\t\t%s\tгазета\tРоссия\tЮкаменский район Удмуртской Республики\tru'
    author = author_(page) # автор
    header = title_(page) # название
    date = date_(page) # дата
    topic = topic_(page) # топик
    year = date[6:] # год
    month = date[4:-5] # месяц
    path = "/Corpus/plain/" + year + os.sep + month + os.sep + file + ".txt" # расположение файла
    table.write(infoString % (path, author, header, date, topic, url, year) + '\r\n')
    table.close()
    return (0)


def main ():
    commonUrl = 'http://ukam-gazeta.ru/article/'
    for i in range(18809, 190000):
        pageUrl = commonUrl + str(i) 
        page = download_page(pageUrl) #скачиваем страницу
        if page != -1:
            file = direct(page) #кладём в каталог
            mystem(page, file) # добавляем распознанные фалы
            info(page, file, pageUrl) # добавляем информацию о статье в неразмеченный текст
            meta(page, pageUrl, file) # добавляем информацию в мататаблицу в корне каталога
    return (0)

main()
