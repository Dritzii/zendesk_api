import PyPDF2
import textract
import tabula
import pandas

from tika import parser
from azure.storage.blob import BlockBlobService
from io import BytesIO




class pdf_file():
    def __init__(self,location,page):
        self.location = location
        self.pdfFileObj = open(self.location, 'rb')
        self.pdfReader = PyPDF2.PdfFileReader(self.pdfFileObj)
        self.pageObj = self.pdfReader.getPage(page)
        self.account_name = 'devblobdatazendesk'
        self.account_key = 'Ve77nc2T1Ieo0xGhzb86OBTPFM8L5KTGZkpQ4PAqdgrEpNx9Ej7VqZEc6Giemsf+hXriYK8xKMSonVP7REJUFQ=='
        self.file_path = "C:/Users/John Pham/Desktop/test.pdf"

    def get_numPages(self):
        noPages = self.pdfReader.numPages
        print(noPages)
       

    def get_text(self):
        text = self.pageObj.extractText()
        print(text)
        
    def blob_upload(self):
        print("connecting to blob storage")
        blob_service = BlockBlobService(account_name = self.account_name,account_key = self.account_key)
        blob_service.create_blob_from_path('csv-blob', blob_name= 'test.pdf',file_path=self.file_path )
        generator = blob_service.list_blobs('csv-blob')
        for blob in generator:
            print("\t Blob name: " + blob.name)









if __name__ == '__main__':
    pdf_file('C:/Users/John Pham/Desktop/test.pdf',0).blob_upload()