import selenium
import time
import urllib
#import cv2
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from python_anticaptcha import AnticaptchaClient, ImageToTextTask

import numpy as np
import pandas as pa
from gensim.models import Word2Vec
from gensim.utils import simple_preprocess
from gensim.models import KeyedVectors
import warnings
from scipy.spatial import distance       
warnings.filterwarnings('ignore')



NETWORKING_DATA = pa.read_csv('yourfile.csv',encoding='unicode_escape')  #quesiton path 

def words_embeddings():
    path = r"    "#put the path of the file from https://www.kaggle.com/syedamer/gnewsvector
    word_embeddings_index = {}
    word_vectors = KeyedVectors.load_word2vec_format(path,binary=True)
    for word,vector in zip(word_vectors.vocab,word_vectors.vectors):
         coefs = np.asarray(vector,dtype='float32')
         word_embeddings_index[word] = coefs
        
    return  word_embeddings_index     

word_embeddings_index = words_embeddings() 

## Sum up vectors of each word in a sentence and average it i.e the word_embeddings of the whole senetence
def find_average_sentence_vector(sentence,MODEL,features=300):
    ## Split or tokenize the words in a sentence
    words = sentence.split()
    sentence_vector = np.zeros((features,),dtype='float32')
    total_words = 0
    for word in words:
        #ADD the embedings of each word to the senetence vector
        if word in word_embeddings_index.keys():
            total_words += 1
            sentence_vector = np.add(sentence_vector,MODEL[word])
        
    if total_words>0:
        sentence_vector = np.divide(sentence_vector,total_words)
    return sentence_vector

def similarity_checking_cosine(average_question_to_match):
    similarity_list = []
    for i in range(len(NETWORKING_DATA)):
        question_i = str(NETWORKING_DATA.iloc[i]['Questions'])
        average_question_i = find_average_sentence_vector(question_i,MODEL=word_embeddings_index,features=300)
        cos = distance.cosine(average_question_to_match,average_question_i)
        similarity_list.append(cos)
    return similarity_list


PATH = "C:\Program Files (x86)\chromedriver.exe"

driver = webdriver.Chrome(PATH)

driver.get("https://www.iemcrp.com/")
college = driver.find_element_by_link_text(("Institute of Engineering and Management,Kolkata(104)")).click()
college

with open('captcha67.png', 'wb') as file:
   file.write(driver.find_element_by_xpath("/html/body/div[1]/form[2]/fieldset/img").screenshot_as_png)

captcha_fn = "captcha67.png"
api_key = '' # your api key here, get from -> https://anti-captcha.com/
captcha_fp = open(captcha_fn, 'rb')
client = AnticaptchaClient(api_key)
task = ImageToTextTask(captcha_fp)
job = client.createTask(task)
job.join()
#print(job.get_captcha_text())
captcha_image=job.get_captcha_text()#captcha_image will store the resulted captcha

time.sleep(2)
#to select the dropdown as student
drop_down=Select(driver.find_element_by_id("mtype"))
drop_down.select_by_visible_text("Student")

#to enter username and password use this and captcha
username = driver.find_element_by_id("text1")
username.send_keys("")#enter your Username

password = driver.find_element_by_id("text2")
password.send_keys("")#enter your password

captchacatch = driver.find_element_by_id("text3")
captchacatch.send_keys(captcha_image)

time.sleep(5)

#Gobutton
driver.find_element_by_id("submit1").click()

time.sleep(1)

driver.find_element_by_xpath("/html/body/font/table/tbody/tr[1]/td[1]/table/tbody/tr[7]/td/button").click()#for clicking onlinetest
time.sleep(2)
driver.find_element_by_xpath("/html/body/font/ul/li[2]/a").click()#for clicking to open test section

time.sleep(5)


#enter iemcrp exam code

main_page = driver.current_window_handle #store the current window

iemcrp_examcode = "2020010729" 
table = driver.find_element_by_xpath("/html/body/font/center[2]/table")
for (i,rows) in enumerate(table.find_elements_by_css_selector('tr')):

    #for cells in rows.find_elements_bobjecty_tag_name('td'):
        #print(cells.text)#
        table_rows = []
        table_rows.append(rows.text)
        
        #spliting all wordsrow object
        
        iemcrp_code = [word.split() for word in table_rows][0][0]

        if iemcrp_code!=iemcrp_examcode:#checking if it matches iemcrp code matches with our examcode
            continue

        driver.find_element_by_xpath("/html/body/font/center[2]/table/tbody/tr[{}]/td[11]/a".format(i+1)).click()
        #to handle control to the pop up exam page window
        for handle in driver.window_handles:
            if handle!=main_page:
                exam_page=handle


        driver.switch_to.window(exam_page)#switches to exam page window
        
        try:
            driver.find_element_by_xpath("/html/body/form/fieldset/label[1]").click()#to click stars to give rating
            time.sleep(1)
            driver.find_element_by_id("sub1").click()#to submit rating
        except:
            pass    
        finally:
            time.sleep(4)
            driver.find_element_by_id("submit1").click()#continue button to start exam
            time.sleep(2)
            number_of_question = driver.find_element_by_xpath("/html/body/font/form/table/tbody/tr[1]/td[1]/font[2]").text
            
            for i in range(int(number_of_question)):
                question_list=[]
                answer_list=[]
                question = driver.find_element_by_xpath("/html/body/font/form/table/tbody/tr[2]/td[2]/p[1]").text
                question_list.append(question)
                print(question_list)
                answ_a = driver.find_element_by_xpath("/html/body/font/form/table/tbody/tr[2]/td[2]/p[2]").text
                answ_b = driver.find_element_by_xpath("/html/body/font/form/table/tbody/tr[2]/td[2]/p[3]").text
                answ_c = driver.find_element_by_xpath("/html/body/font/form/table/tbody/tr[2]/td[2]/p[4]").text
                answ_d = driver.find_element_by_xpath("/html/body/font/form/table/tbody/tr[2]/td[2]/p[5]").text
                answer_list.append([answ_a, answ_b,answ_c, answ_d])

                question_to_match = str(question_list[0])
                average_question_to_match = find_average_sentence_vector(question_to_match,MODEL=word_embeddings_index,features=300)
                similarity_list = similarity_checking_cosine(average_question_to_match)
                answer_index = similarity_list.index(min(similarity_list))
                answer = NETWORKING_DATA.iloc[answer_index]['Answers'] 
                         
                answers = [['A. FDM', 'B. TDM', 'C. WDM', 'D. All of these.']] 

                answers = answers[0]
                answers_list = []
                index_list = []
                print(answers) #run shift ctrl b
                for i,word in enumerate(answers):
                    first_text = answers[i]
                    first_answer = first_text.split('.')[1]
                    first_index = first_text.split('.')[0]  
                    answers_list.append(first_answer)
                    index_list.append(first_index)

                answers_dict =  dict(zip(answers_list,index_list))
              
                
                
                ##Find the answer option
                similarity_answers  = []
                for item in answers_list:
                    avg_vector_answer = find_average_sentence_vector(item,MODEL=word_embeddings_index,features=300)
                    answer_current_avg = find_average_sentence_vector(answer,MODEL=word_embeddings_index,features=300)
                    #find cosine similarity
                    similarity_answers.append(distance.cosine(avg_vector_answer,answer_current_avg))
                most_similar_answer = similarity_answers.index(min(similarity_answers))
                #DROP_DOWNLIST FOR ANSWER
                drop_downans = Select(driver.find_element_by_id("select1"))
                drop_downans.select_by_visible_text(index_list[most_similar_answer]) 
                driver.find_element_by_id("submit1").click()
                time.sleep(3)
        driver.quit()
        break           
driver.close()
