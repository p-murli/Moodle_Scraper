import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import lxml
from lxml import html
from urllib.request import urlretrieve
import time
import os
#import necessary packages


#User data. Noob level. Make this more secure later
#username = input("Enter Moodle Username")
#password = input("Enter Password")

cred = open("pass.txt", "r")
user = cred.readline().rstrip("\n")
pas = cred.readline().rstrip("\n")
print(user)
print(pas)
payload = {'username':user, 'password':pas}


#2 sites needed. One is the login page and the other is the page from where to start data collection
login_site = (r"http://photon.bits-goa.ac.in/lms/login/index.php")
data_site = (r"http://photon.bits-goa.ac.in/lms/my/")



#Make a requests Session and input the login data and get the text on the page

with requests.Session() as session:
    post = session.post(login_site, data=payload)
    r = session.get(data_site)
    content = r.text

#Make a Beasutiful Soup object and write contents to a file

soup = BeautifulSoup(content, 'lxml')

moo = open("Moodle.txt", 'w')
#moo.write(soup.prettify().encode('utf-8'))

#Inspect element from website to find out what type of tag our data is in and use find that tag
#Below code finds 8 tags for 8 courses
#course_tags is a bs4 Result set


course_tags = soup.find_all('h3', class_ ='main')
#print(len(course_tags))

#Make a dictoinary to update all the individual links of the subjects
link_dict = {}
course_links = []

for c in course_tags:
    for i in c.children:
        #print(i if i!='\n' else '')
        href = i['href']
        c_name  = i.text
        #print(i.text)
        #print(href)
        course_links.append(href)
        link_dict[href] = c_name

print(link_dict)




#link_dict now contains all the links to the registered courses for a person for  this semester

#print(evs)

#This function is to get all the resource links in a particular course
def links_in_course(course_link):

    course_page = session.get(course_link)
    course_page_content_soup = BeautifulSoup(course_page.text,'lxml')

    resource_links = course_page_content_soup.find_all('li', class_ ='activity resource modtype_resource')
    resource_links_2 = []
    file_types = []

    for li in resource_links:
        r_tags = li.find_all('a')
        r_link = r_tags[0]['href']

        img_tags = li.find_all('img')
        img_link = img_tags[0]['src']

        if 'powerpoint' in img_link:
            f_type = 'powerpoint'
        elif 'pdf' in img_link:
            f_type = 'pdf'
        elif 'document' in img_link:
            f_type = 'document'
        elif 'folder' in img_link:
            f_type = 'folder'

        #file_name_tags =  []
        for a_tag in r_tags:
            file_name_tags = a_tag.find('span', class_ = 'instancename')
            if file_name_tags is not None:
                file_name = file_name_tags.contents[0]


        resource_links_2.append([r_link,f_type,file_name])



    moo.write(str(resource_links_2))

    return resource_links_2


#This function is to download the pdf from the link
def download_pdf(pg_link,file_name,subj_path):
    pdf_page = session.get(pg_link)
    pdf_page_soup = BeautifulSoup(pdf_page.text, 'lxml')

    try:
        pdf = pdf_page_soup.find_all('object')[0]['data']
    except:
        print("Couldn't download this file",file_name)
        return

    f_path = file_name+'.pdf'
    full_path = os.path.join(subj_path,f_path)

    down_page = session.get(pdf)
    if not os.path.exists(full_path):
        open(full_path,'wb').write(down_page.content)

        print("Downloaded " + file_name)

#download_pdf('http://photon.bits-goa.ac.in/lms/mod/resource/view.php?id=18924','tut_2')
#download_pdf(page_link, file_name)

#This function is to download the ppts
def download_ppt(pg_link, file_name,subj_path):

    f_path = file_name+'.ppt'
    full_path = os.path.join(subj_path,f_path)


    down_page = session.get(pg_link)
    if not os.path.exists(full_path):
        open(full_path,'wb').write(down_page.content)

        print("Downloaded " + file_name)

#This function is to download the word documents
def download_docx(pg_link, file_name,subj_path):

    f_path = file_name+'.docx'
    full_path = os.path.join(subj_path,f_path)

    down_page = session.get(pg_link)

    if not os.path.exists(full_path):
        open(full_path,'wb').write(down_page.content)

        print("Downloaded " + file_name)


#This function downloads all the resources(word,pdf,ppt)
def download_resources(links,subj_path):

    time.sleep(1)

    for resource in links:

        if(resource[1]=='pdf'):
            download_pdf(resource[0],resource[2],subj_path)
        elif(resource[1]=='powerpoint'):
            download_ppt(resource[0],resource[2],subj_path)
        elif(resource[1]=='document'):
            download_docx(resource[0],resource[2],subj_path)
        else:
            print("No resource to download")


    print("All downloads Completed")


        #elif(resource[1]=='folder'):
        #    download_from_folder()


#era_links = links_in_course(era)

#download_resources(era_links)


def download_from_folder(course_link, subj_path):
    course_page = session.get(course_link)
    course_page_content_soup = BeautifulSoup(course_page.text,'lxml')

    resource_links = course_page_content_soup.find_all('li', class_ ='activity folder modtype_folder')
    file_names = []
    r_links = []
    for li in resource_links:

        folder_tags = li.find_all('a')
        folder_link = folder_tags[0]['href']

        folder_page = session.get(folder_link)
        folder_page_soup = BeautifulSoup(folder_page.text, 'lxml')

        inside_link = folder_page_soup.find_all('span', class_ = 'fp-filename-icon')


        for span in inside_link:
            a_link = span.find('a')
            r_link = a_link['href']

            r_links.append(r_link)


        name_link = folder_page_soup.find_all('span', class_ = "fp-filename")

        for files in name_link[1:]:
            file_names.append(files.string)



    new_dict = dict(zip(r_links, file_names))

    for item in new_dict:

        time.sleep(1)

        f_path = new_dict[item]
        full_path = os.path.join(subj_path,f_path)

        down_page = session.get(item)
        if not os.path.exists(full_path):
            open(full_path, 'wb').write(down_page.content)

        #open(file_name+'.ppt','wb').write(down_page.content)

            print("Downloaded " + new_dict[item])


    #print(r_links)
    #print(file_names)

def make_folders(link_dict):

    subject_paths = {}
    for item in link_dict:

        course_name = link_dict[item]
        print(course_name)

        path = os.getcwd()
        subject_path = os.path.join(path,"Moodle Materials", course_name)
        subject_paths[course_name] = subject_path

        if not os.path.exists(subject_path):
            os.makedirs(subject_path)

    return subject_paths

#print((sub_paths))

def main_function(link_dict,sub_paths):

    for item in link_dict:

        each_subject_folder_path = sub_paths[link_dict[item]]

        #print(each_subject_folder_path)
        #if("ALGEB" not in each_subject_folder_path):
        #    continue

        links_in_each_course = links_in_course(item)

        download_resources(links_in_each_course,each_subject_folder_path)
        download_from_folder(item,each_subject_folder_path)

        print("Downloads completed for ",link_dict[item])

    print("All Downloads Completed for All Subjects!")


sub_paths = make_folders(link_dict)
main_function(link_dict, sub_paths)
