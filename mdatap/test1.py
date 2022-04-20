import sqlite3
import cv2
import os
from pyzbar.pyzbar import decode
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time

driver = webdriver.Chrome("chromedriver.exe")


def BarcodeReader(image):
     
    print("[Decoder] decoding: "+image)
    # read the image in numpy array using cv2
    img = cv2.imread(image)
      
    # Decode the barcode image
    detectedBarcodes = decode(img)
    return detectedBarcodes

def AddCode(data):

    driver.get("https://www.barcodelookup.com/")
    Search = driver.find_element(By.XPATH,"/html/body/section[1]/div/div/div/form/input[2]")
    Search.send_keys(data)
    Search.send_keys(Keys.RETURN)
    try:
        ProductName = driver.find_element(By.XPATH,"//*[@id=\"product\"]/section[2]/div[1]/div/div/div[2]/h4")

        c2.execute("INSERT INTO productscodes VALUES (:productname, :code) ", {"productname":str(ProductName.text),"code":data})
        conn2.commit()
    except:
        print("[driver] nazwy przedmiotu nie znaleziono")

def TryFind(data,Try=0):
    
    c2.execute("SELECT EXISTS(SELECT * FROM productscodes WHERE code = :code)",{"code":data})
    if bool(c2.fetchone()[0]):
        c2.execute("SELECT * FROM productscodes WHERE code = :code",{"code":data})
        return c2.fetchone()
    else:
        if Try == 0:
            AddCode(data)
            return [0]
        else:
            return [0]
          



conn = sqlite3.connect('products.db')
conn2 = sqlite3.connect('productscodes.db')

c = conn.cursor()
c2 = conn2.cursor()



try:
    c.execute("""CREATE TABLE products(
        name text,
        code int,
        count int
                                        ) 
    """)
except:
    print("[DataBase] (Info) Tabela juz istnieje")


try:
    c2.execute("""CREATE TABLE productscodes (
        name text,
        code int
                                        ) 
    """)
except:
    print("[DataBase 2] (Info) Tabela juz istnieje")


def AddProduct(name,code,count):
    c.execute("SELECT EXISTS(SELECT * FROM products WHERE code=:code)",{"code":code})
    if bool(c.fetchone()[0]):
        c.execute("SELECT * FROM products WHERE code = :code",{"code":code})
        count2=c.fetchone()[2]
        
        c.execute("UPDATE products SET count=:count",{"count":int(count2+count)})
    else:
        c.execute("INSERT INTO products VALUES (:productname, :code, :count) ", {"productname":str(name),"code":code,"count":count})


for image in os.listdir(os.getcwd()+"/barcodes"):

    Barcode = BarcodeReader(str(os.getcwd()+"/barcodes/"+image))
    if len(Barcode) !=0:
        print("znaleziono kod kreskowy")
        name=TryFind(int(Barcode[0].data.decode('UTF-8')),Try=0)

        print(name)
        if name != None:
            if name!=[0]:
                AddProduct(name[0],int(Barcode[0].data.decode('UTF-8')),1)
            else:
                name=TryFind(int(Barcode[0].data.decode('UTF-8')),Try=1)
                print(name)
                if name != None:
                    if name!=[0]:
                        AddProduct(name[0],int(Barcode[0].data.decode('UTF-8')),1)
    time.sleep(3)




conn.commit()
try:
    #driver.close()
    print("1")
except:
    print("[Driver] nie można zamknąć ponieważ driver nie istnieje")
