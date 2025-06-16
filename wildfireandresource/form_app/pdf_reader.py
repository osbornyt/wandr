import os
from pypdf import PdfReader, PdfWriter
from pypdf.generic import NameObject, BooleanObject
import pdfplumber
import copy

def create_contract(text,contract_no):
    contract = {}
    lines = text.splitlines()
    contract['contract_no'] = contract_no
    contract['solicitation_no'] = lines[1]
    contract['solicitor'] = lines[2]
    contract['solicitor_phone'] = lines[3]
    service = lines[11]
    index = 12
    for i in range(10):
        line = lines[index + i]
        if line == contract_no:
            index = index + i
            break
    for i in range(index-11-2):
        service = service + lines[12+i]
    contract['service'] = service
    contract['contractor_name'] = lines[index+1]
    contract['contractring_officer'] = lines[index+2]
    contract['naics'] = lines[index + 3]
    contract['amount'] = lines[index + 4]
    contract['contractor_tel'] = lines[index + 5]
    contract['award_date'] = lines[index + 6]
    contract['contractor_signed_date'] = lines[index + 7]
    contract['officer_signed_date'] = lines[index + 8]
    contract['effective_date'] = lines[index + 9] + lines[index + 10]
    contract['issue_date'] = lines[index + 11]
    contract['offer_due_date'] = lines[index + 12]
    contract['issuer'] = lines[index + 13] + "\n" + lines[index + 14] + "\n" +lines[index + 15] + "\n" + lines[index + 16] +  "\n" + lines[index + 17]
    return contract

def read_pypdf(pdf_path):
    try:
        reader = PdfReader(pdf_path)
        page = reader.pages[0]
        text = page.extract_text()
        contract_no = ""
        start_marker = "Agreement #:"
        end_marker = "w/"
        if start_marker in text and end_marker in text:
            start = text.find(start_marker) + len(start_marker)
            end = text.find(end_marker)
            contract_no =  text[start:end].strip()
        remaining_text = text[text.find(contract_no):]
        contract = create_contract(remaining_text,contract_no)
        resource_names = []
        start_marker = "SOI for"
        end_marker = "- Unique"
        resource_pages = []              
        for i in range(10):
            resource_text = reader.pages[1+i].extract_text()
            if "Vendor Information" in resource_text:
                break
            else:
                resource_pages.append(i+1)
                lines = resource_text.splitlines()
                for line in lines:
                    if "Table" in line:
                        start = line.find(start_marker) + len(start_marker)
                        end = line.find(end_marker)
                        resource_names.append(line[start:end].strip())
                        
        markers = ["Company Name:", "DBA:", "UEI:", "EFT:", "Company Address:", "Mailing Address:"]
        vendor_info = {}
        
        for i in range(len(markers)):
            start_marker = markers[i]
            end_marker = markers[i+1] if not i == len(markers) - 1 else "Contact"
            
            if start_marker in resource_text and end_marker in resource_text:
                start = resource_text.find(start_marker) + len(start_marker)
                end = resource_text.find(end_marker)
                result = resource_text[start:end].strip().replace("\n", "")
                vendor_info[markers[i].replace(":", "")] = result
        #print(vendor_info)
        resources = []
        with pdfplumber.open(pdf_path) as agreement_pdf:
            entry = {}
            index = 0
            for page in resource_pages:
                page_to_process = agreement_pdf.pages[page]
                for table in page_to_process.extract_tables():
                    for row in table:
                        if 'Status' in row[0]:
                            if entry:
                                temp = copy.deepcopy(entry)
                                temp['name'] = resource_names[index]
                                index = index + 1
                                resources.append(temp)

                        if 'Resource Information' not in row[0]:    
                            entry[row[0].replace(":", "")] = row[1]
            entry['name'] = resource_names[index]
            resources.append(entry)
        result = {}
        result['contract'] = contract
        result['resources'] = resources
        result['vendor'] = vendor_info
        return result
    except FileNotFoundError:
        print(f"Error: PDF file not found at '{pdf_path}'")


