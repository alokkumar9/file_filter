
import logging
import os.path
import json
from zipfile import ZipFile
import pandas as pd
from adobe.pdfservices.operation.auth.credentials import Credentials
from adobe.pdfservices.operation.exception.exceptions import ServiceApiException, ServiceUsageException, SdkException
from adobe.pdfservices.operation.pdfops.options.extractpdf.extract_pdf_options import ExtractPDFOptions
from adobe.pdfservices.operation.pdfops.options.extractpdf.extract_element_type import ExtractElementType
from adobe.pdfservices.operation.execution_context import ExecutionContext
from adobe.pdfservices.operation.io.file_ref import FileRef
from adobe.pdfservices.operation.pdfops.extract_pdf_operation import ExtractPDFOperation

def zip_to_json(result):
  result.save_as("output/ExtractTextInfoFromPDF.zip")
  with ZipFile("output/ExtractTextInfoFromPDF.zip", 'r') as zObject:
    zObject.extractall(path="/content/extracted")
    print('unzipped')
    #zObject.extract('structuredData.json',path="/extracted")
    zObject.close()
    with open('/content/extracted/structuredData.json', 'r') as f:
      json_data = json.load(f)
      os.remove("output/ExtractTextInfoFromPDF.zip")
      return json_data

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
def fetch_json(file_ref):
  try:
      # get base path.
      # base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

      # Initial setup, create credentials instance.
      # credentials = Credentials.service_principal_credentials_builder(). \
      #     with_client_id(os.getenv('PDF_SERVICES_CLIENT_ID')). \
      #     with_client_secret(os.getenv('PDF_SERVICES_CLIENT_SECRET')). \
      #     build()
      credentials = Credentials.service_principal_credentials_builder(). \
        with_client_id('0662a4d18be548ccb3a03ea982eae5e3'). \
        with_client_secret('p8e-Tz_CYtSdoa5xsus0vzZYWz3bm-ZLvh8Z'). \
        build()
      # Create an ExecutionContext using credentials and create a new operation instance.
      execution_context = ExecutionContext.create(credentials)
      extract_pdf_operation = ExtractPDFOperation.create_new()

      # Set operation input from a source file.
      # source = FileRef.create_from_local_file(base_path + "/resources/extractPdfInput.pdf")
      source = file_ref

      extract_pdf_operation.set_input(source)

      # Build ExtractPDF options and set them into the operation
      extract_pdf_options: ExtractPDFOptions = ExtractPDFOptions.builder() \
          .with_element_to_extract(ExtractElementType.TEXT) \
          .build()
      extract_pdf_operation.set_options(extract_pdf_options)

      # Execute the operation.
      result: FileRef = extract_pdf_operation.execute(execution_context)

      if os.path.isfile("/content/extracted/structuredData.json"):
        os.remove('/content/extracted/structuredData.json')
        json_data=zip_to_json(result)

        print("file replaced with new")
      else:
        json_data=zip_to_json(result)

      return json_data

  except (ServiceApiException, ServiceUsageException, SdkException):
    logging.exception("Exception encountered while executing operation")


def json_manage(file_source):
  file_ref = FileRef.create_from_local_file(file_source)
#   file_ref=FileRef.createFromStream(file_source)
  print(file_ref)
  json_data=fetch_json(file_ref)
  return json_data

# Here elements is array
def json_to_dataframe(json_data):
  elements=json_data["elements"]

  pages,path,texts=[],[],[]
  count=1;

  for element in elements:
    if any("Font" in key for key in element):
      #print(str(count)+"    "+str(element["Page"])+"        "+element["Text"]+"\n")
      pages.append(element["Page"])
      path.append(element["Path"])
      texts.append(element["Text"])
      count+=1
  data_panda=pd.DataFrame()
  data_panda["page"]=pages
  data_panda["path"]=path
  data_panda["text"]=texts
  return data_panda