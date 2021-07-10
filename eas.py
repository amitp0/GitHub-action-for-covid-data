import pyrebase
import requests
import cv2
from PIL import Image
import pytesseract
import re
import json
import base64
import pandas as pd
from pdf2image import convert_from_bytes

CONFIG=b'eyJhcGlLZXkiOiAiQUFBQUFGaVJuR3M6QVBBOTFiSHBBLWZmVTF4YkZhdVhyMzhzYmhDMU4tNU10TWRWaTUzSWZrN01fNHNPTmZMNlZuSUw0Nm52bnZva3o0SXR2N3RITGlmb05makJrUWdncFFIMG5HbU5UT0RzUTJodFA0WVpLRktXTGNvZWs1aUFrQkdJX0hmbWRrME51ZGhPSlpQT1ExTk4iLCAiYXV0aERvbWFpbiI6ICJtdW1iYWlmaWdodHNjb3ZpZDE5LmZpcmViYXNlYXBwLmNvbSIsICJkYXRhYmFzZVVSTCI6ICJodHRwczovL211bWJhaWZpZ2h0c2NvdmlkMTktZGVmYXVsdC1ydGRiLmZpcmViYXNlaW8uY29tLyIsICJzdG9yYWdlQnVja2V0IjogIm11bWJhaWZpZ2h0c2NvdmlkMTkuYXBwc3BvdC5jb20ifQ=='
decode=base64.b64decode(CONFIG.decode('utf-8'))
config=json.loads(decode)
firebase = pyrebase.initialize_app(config)
db = firebase.database()

pdf_link="https://stopcoronavirus.mcgm.gov.in/assets/docs/Dashboard.pdf"
img_name=["status","containmentZones","microcontainmentZones","data","vaccination"]
cropped_img_name=["containmentZones_val","containmentZones_ward","data_active","data_confirmed","data_deceased","data_recovered","data_ward","microcontainmentZones_val","microcontainmentZones_ward","status_dtd","status_gr","status_pos","status_ward","vaccination_all"]
page_numbers=[2,16,17,22,37]

def save_images():
  pdf_file=requests.get(pdf_link,verify=False).content
  with open('file.pdf','wb') as handler:
    handler.write(pdf_file)
  images = convert_from_bytes(open('file.pdf','rb').read(),dpi=300,first_page=1,last_page=38)
  for x in range(len(img_name)):
    images[page_numbers[x]-1].save((img_name[x]+'.png'))

def clean_images():
  for x in img_name:
    print(x)
    cv2.imwrite((x+'.png'),blur_bw(cv2.imread(x+'.png')))
    
def blur_bw(img):
  grayscale = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
  thresh = 255 - cv2.threshold(grayscale, 200, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
  kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(2,3))
  erode = cv2.erode(thresh,kernel)
  blur = cv2.blur(erode,(1,3))
  return blur

def crop_images(img,crop_coord,imgFormat):
    org_img=Image.open(img).crop(crop_coord).save(imgFormat)

def inv_images(imgpath):
  for x in range(len(imgpath)):
    cv2.imwrite(imgpath[x],255-cv2.imread(imgpath[x]))
  threshold(imgpath)

def threshold(imgpath):
  for x in range(len(imgpath)):
    cv2.imwrite(imgpath[x],cv2.threshold(cv2.imread(imgpath[x]),200,255,cv2.THRESH_BINARY)[1])

def namestr(obj):
  namespace=globals()
  return [name for name in namespace if namespace[name] is obj]

def remove_rect():
  for x in cropped_img_name:
    for y in range(8):
     image = cv2.imread(x+'.png')

     gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
     thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

     horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (50,1))
     detected_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, horizontal_kernel, iterations=1)
     cnts = cv2.findContours(detected_lines, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
     cnts = cnts[0] if len(cnts) == 2 else cnts[1]
     for c in cnts:
       cv2.drawContours(image, [c], -1, (255,255,255), 5)

     vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1,50))
     detected_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN,vertical_kernel, iterations=1)
     cnts = cv2.findContours(detected_lines, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
     cnts = cnts[0] if len(cnts) == 2 else cnts[1]
     for c in cnts:
       cv2.drawContours(image, [c], -1, (255,255,255), 5)
 
     repair_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1,1))
     result = 255 - cv2.morphologyEx(255 - image, cv2.MORPH_CLOSE, repair_kernel, iterations=2)

     cv2.imwrite(x+'.png',result)

def to_str():
  global list_str,strvar
  for x in range(len(strvar)):
    list_str[strvar[x]]=re.sub("[ ]","\n",list_str[strvar[x]])
    list_str[strvar[x]]=re.sub("[^a-zA-Z]"," ",list_str[strvar[x]])
    list_str[strvar[x]]=re.sub(' +', '\n',list_str[strvar[x]])
    list_str[strvar[x]]=list_str[strvar[x]].splitlines()
    list_str[strvar[x]]=list(filter(None,list_str[strvar[x]]))
    list_str[strvar[x]] = [str(i) for i in list_str[strvar[x]]]
    list_str[strvar[x]]= [j.upper() for j in list_str[strvar[x]]]

def to_int():
  global list_int,intvar
  for x in range(len(intvar)):
    list_int[intvar[x]]=re.sub("[,.%]","",list_int[intvar[x]])
    list_int[intvar[x]]=re.sub("[^0-9]"," ",list_int[intvar[x]])
    list_int[intvar[x]]=re.sub(' +', '\n',list_int[intvar[x]])
    list_int[intvar[x]]=list_int[intvar[x]].splitlines()
    list_int[intvar[x]]=list(filter(None,list_int[intvar[x]]))
    list_int[intvar[x]] = [int(i) for i in list_int[intvar[x]]]

def clean_str_data():
  global strvar
  for x in range(len(strvar)):
    for y in range(len(strvar[x])):
      print(y)
      a=strlist[x][y]
      if a=="SS":
          a="S"
      elif a=="CC":
            a="C"
      elif a=="I":
            a="T"

save_images()
clean_images()
crop_images('containmentZones.png',(1709,343,2953,2137),'containmentZones_val.png')
crop_images('containmentZones.png',(1511,346,1677,2119),'containmentZones_ward.png')

crop_images('microcontainmentZones.png',(1663,321,2942,2080),'microcontainmentZones_val.png')
crop_images('microcontainmentZones.png',(1472,325,1642,2084),'microcontainmentZones_ward.png')

crop_images('status.png',(451,1904,3699,1946),'status_ward.png')
crop_images('status.png',(451,1955,3699,1997),'status_pos.png')
crop_images('status.png',(451,2014,3699,2056),'status_dtd.png')
crop_images('status.png',(451,2070,3699,2112),'status_gr.png')

crop_images('vaccination.png',(684,742,1454,1423),'vaccination_all.png')

crop_images('data.png',(3006,328,3144,2010),'data_active.png')
crop_images('data.png',(1256,325,2448,2035),'data_confirmed.png')
crop_images('data.png',(2790,328,2932,2006),'data_deceased.png')
crop_images('data.png',(2557,326,2727,2017),'data_recovered.png')
crop_images('data.png',(1119,328,1200,2045),'data_ward.png')

inv_images(['data_deceased.png','status_ward.png'])
remove_rect()

intvar=['containmentZones_val','data_active','data_confirmed','data_deceased','data_recovered','microcontainmentZones_val','status_dtd','status_gr','status_pos', 'vaccination_all']
strvar=['containmentZones_ward','microcontainmentZones_ward','status_ward','data_ward']

list_str = {k: [] for k in strvar}
list_int = {k: [] for k in intvar}

for x in range(len(strvar)):
  imgfile=(strvar[x])+".png"
  list_str[strvar[x]]=pytesseract.image_to_string(Image.open((imgfile)),config='--psm 6 --oem 3')
  

for x in range(len(intvar)):
  imgfile=(intvar[x])+".png"
  list_int[intvar[x]]=pytesseract.image_to_string(Image.open((imgfile)),config='--psm 6 --oem 3')

to_int()
to_str()

for x in list_str:
  for y in range(len(list_str[x])):
    if list_str[x][y]=="SS":
        list_str[x][y]="S"
    elif list_str[x][y]=="CC":
        list_str[x][y]="C"
    elif list_str[x][y]=="I":
       list_str[x][y]="T"

data_primary = {'ward':list_str['data_ward'],'confirmed':list_int['data_confirmed'],'active':list_int['data_active'],'recovered':list_int['data_recovered'],'deceased':list_int['data_deceased']}
df_pri = pd.DataFrame(data_primary)

data_containment={'ward':list_str['containmentZones_ward'],'containmentZones':list_int['containmentZones_val']}
df_containment=pd.DataFrame(data_containment)

data_microcontainment={'ward':list_str['microcontainmentZones_ward'],'microcontainmentZones':list_int['microcontainmentZones_val']}
df_microcontainment=pd.DataFrame(data_microcontainment)

df_containment.join(df_microcontainment.set_index('ward'), on='ward')
df_final=df_pri.join(df_containment.join(df_microcontainment.set_index('ward'), on='ward').set_index('ward'), on='ward')

df_final=(df_final.sort_values(by='ward')).reset_index(drop='True')
print(df_final)

result = df_final.to_json(orient="index")
parsed = json.loads(result)
data=json.dumps(parsed)
data_c=json.loads(data)
db.child("ward").set(data_c)
