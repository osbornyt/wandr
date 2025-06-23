from pypdf import PdfReader, PdfWriter 
from pypdf.generic import NameObject, BooleanObject
import pdfplumber
import io

def populate_shift_ticket_form(form_data):
    with open("pdfs/shiftticket_pdf.pdf", "rb") as pdf_file:
        reader = PdfReader(pdf_file)
        writer = PdfWriter()

        acro_form = reader.trailer["/Root"].get("/AcroForm")
        if acro_form:
            writer._root_object.update({
                NameObject("/AcroForm"): acro_form
            })
            acro_form.update({NameObject("/NeedAppearances"): BooleanObject(True)})

        # fields = reader.get_fields()
        # for name, field in fields.items():
        #     print(f"{name}: {field.get('/V')} (Export values: {field.get('/AP')})")

        for page in reader.pages:
            writer.add_page(page)

        answer_1 = next((answer for answer in form_data if answer.question_number == 1), None)
        answer_2 = next((answer for answer in form_data if answer.question_number == 2), None)
        answer_3 = next((answer for answer in form_data if answer.question_number == 3), None)
        answer_4 = next((answer for answer in form_data if answer.question_number == 4), None)
        answer_5 = next((answer for answer in form_data if answer.question_number == 5), None)
        answer_6 = next((answer for answer in form_data if answer.question_number == 6), None)
        answer_7 = next((answer for answer in form_data if answer.question_number == 7), None)
        answer_8 = next((answer for answer in form_data if answer.question_number == 8), None)
        answer_9 = next((answer for answer in form_data if answer.question_number == 9), None)
        answer_10 = next((answer for answer in form_data if answer.question_number == 10), None)
        answer_11 = next((answer for answer in form_data if answer.question_number == 11), None)
        answer_14 = next((answer for answer in form_data if answer.question_number == 14), None)
        answer_16 = next((answer for answer in form_data if answer.question_number == 16), None)
        answer_17 = next((answer for answer in form_data if answer.question_number == 17), None)
        answer_19 = next((answer for answer in form_data if answer.question_number == 19), None)

        writer.update_page_form_field_values(writer.pages[0], {
            "LAGREEMENT NUMBER": answer_1.answer,
            "CONTRACTOR name": answer_2.answer,
            "3 INCIDENT OR PROJECT NAME": answer_3.answer,
            "4 INCIDENT NUMBER": answer_4.answer,
            "5 OPERATOR name": answer_5.answer,
            "6 EQUIPMENT MAKE": answer_6.answer,
            "CONTRACTOR": "/On" if answer_8.answer == 'Contractor' else "/Off",
            "GOVERNMENT": "/On" if answer_8.answer == 'Government' else "/Off",
            "7 EQUIPMENT MODEL": answer_7.answer,
            "9 SERIAL NUMBER": answer_9.answer,
            "10 LICENSE NUMBER": answer_10.answer,
            "CONTRACTOR wet": "/On" if answer_11.answer == 'Contractor' else "/Off",
            "GOVERNMENT dry": "/On" if answer_11.answer == "Government" else "/Off",
            "a I": "/On" if answer_16.answer == "Inspected and under agreement" else "/Off",
            "b Released by Government": "/On" if answer_16.answer == "Released by Government" else "/Off",
            "c Withdrawn by Contractor": "/On" if answer_16.answer == "Withdrawn by Contractor" else "/Off",
            "13 EQUIPMENT USE": answer_14.answer,
            "16 INVOICE POSTED BY Rccordcrs initials": answer_17.answer,
            "19 DATE SIGNED": answer_19.answer,
        })

        table_map = {
            "0,0": "Textfield",
            "0,1": "Textfield0",
            "0,2": "Textfield1",
            "0,3": "Textfield2",
            "0,4": "Textfield3",
            "1,0": "Textfield4",
            "1,1": "Textfield5",
            "1,2": "Textfield6",
            "1,3": "Textfield7",
            "1,4": "Textfield8",
            "2,0": "Textfield9",
            "2,1": "Textfield10",
            "2,2": "Textfield11",
            "2,3": "Textfield12",
            "2,4": "Textfield13",
            "3,0": "Textfield14",
            "3,1": "Textfield15",
            "3,2": "Textfield16",
            "3,3": "Textfield17",
            "3,4": "Textfield18"
        }

        table_answers = [table_answer for table_answer in form_data if table_answer.question_number == 13]

        # match row and col in table answers to table_map
        mapped_table_answers = {
            table_map[f"{table_answer.table_row},{table_answer.table_col}"]: table_answer.answer
            for table_answer in table_answers
            if f"{table_answer.table_row},{table_answer.table_col}" in table_map
        }

        writer.update_page_form_field_values(writer.pages[0], mapped_table_answers)

        with open("media/pdfs/generated.pdf", "wb") as f:
            writer.write(f)


def get_form_tables(pdf_file_name, max_pages=None):
    """
    Extracts tables from a PDF file using pdfplumber, with optional page limit.

    Args:
        pdf_file_name (str): The path to the PDF file.
        max_pages (int, optional): The maximum number of pages to process.
                                   If None, all pages will be processed.

    Returns:
        list: A list of tables, where each table is a list of rows,
              and each row is a list of cell values.
    """
    tables = []

    with pdfplumber.open(pdf_file_name) as ro_pdf:
        pages_to_process = ro_pdf.pages[:max_pages] if max_pages else ro_pdf.pages
        for page in pages_to_process:
            for table in page.extract_tables():
                tables.append(table)

    return tables


def get_form_data(form_tables, field, text_to_remove=None):
    """
    Extracts specific data from a nested table structure (list of tables),
    based on the field name and a predefined position mapping.

    Args:
        form_tables (list): A list of tables extracted from an RO PDF file, where each table is a list of rows,
                            and each row is a list of cell values.
        field (str): The name of the field to extract (e.g., "project_name", "resource").
                     * Should be defined in the field_positions variable.
                     * Register new fields in the field_positions variable with their responding indices/positions.
                     * To find positions/indices use a sample RO form(assumed to have same shape always).
        text_to_remove (str, optional): Text to be removed from the extracted cell. Defaults to None.

    Returns:
        str: The cleaned value extracted from the table cell.
    """

    field_positions = {
        "project_name": [0, 0, 4],
        "incident_number": [0, 0, 8],
        "resource": [1, 1, 5],
        "request_number": [1, 1, 0],
        "resource_assigned": [1, 1, 12],
    }

    data_position = field_positions[field]

    # tables[table_index][row][index/position]
    data = form_tables[data_position[0]][data_position[1]][data_position[2]]

    if text_to_remove:
        data = data.replace(text_to_remove, " ")

    return clean_data(data)


def clean_data(data):
    return data.replace("\n", " ").strip()


def populate_evaluation_form(form_data):
    output_pdf_buffer = io.BytesIO()
    with open("pdfs/evaluation.pdf", "rb") as pdf_file:
        reader = PdfReader(pdf_file)
        writer = PdfWriter()

        acro_form = reader.trailer["/Root"].get("/AcroForm")
        if acro_form:
            writer._root_object.update({
                NameObject("/AcroForm"): acro_form
            })
            acro_form.update({NameObject("/NeedAppearances"): BooleanObject(True)})

        for page in reader.pages:
            writer.add_page(page)

        writer.update_page_form_field_values(writer.pages[0],form_data)
        writer.write(output_pdf_buffer)

        # writer.update_page_form_field_values(writer.pages[0], {
        #     "ContractorCompany Name": "Company X",
        #     "Resource Type and Equipment ID EngineDozerWater Tenderetc": "Equipment X",
        #     "Fire Name and Number": "Equipment X",
        #     "Equipment Resource Order": "E-XXX",
        #     "Agreement Number": "XXXXXXXXXXXXX",
        #     "Contracting Officer Name": "Jane Doe",
        # })

        # with open("media/generated/pdfs/filled_evaluation.pdf", "wb") as f:
        #     writer.write(f)
        # return "media/generated/pdfs/filled_evaluation.pdf"
    output_pdf_buffer.seek(0)

    # Return the bytes content of the PDF
    return output_pdf_buffer.getvalue()


def validate_pdf(pdf_path, search_text):
    try:
        with open(pdf_path, 'rb') as file:
            reader = PdfReader(file) # Use PdfReader from pypdf
            
            # Check if the PDF has any pages
            if not reader.pages:
                return "PDF contains no pages."

            # Access the first page (index 0)
            first_page = reader.pages[0]
            
            # Extract text from the first page
            first_page_text = first_page.extract_text()
            
            if first_page_text:
                # Check if the search_text is present in the extracted text
                # We use .lower() on both to make the search case-insensitive
                if search_text.lower() in first_page_text.lower():
                    return "OK"
                else:
                    return "File Mismatch"
            else:
                return "No extractable text found"

    except Exception as e:
        return "Could not read PDF file. It might be corrupted or encrypted"

def mine_RO(file):
    tables = get_form_tables(file)
    resource = get_form_data(tables, "resource").split(',')
    summary = {
        'project_name': get_form_data(tables, "project_name", '2.Incident / Project Name'),
        'incident_number': get_form_data(tables, 'incident_number', '3. Incident / Project'),
        'make': resource[0].strip(),
        'model': resource[1].strip(),
        'request_number': get_form_data(tables, "request_number"),
        'resource_assigned': get_form_data(tables, "resource_assigned")
    }
    return summary


class AgreementPDFExtractor:
    """
    Extracts specific information from a structured agreement PDF, such as
    contract numbers, contracting officer details, contractor details, and vendor information.
    """

    def __init__(self, pdf_path):
        """
        Initialize the extractor with the path to a PDF file.

        Args:
            pdf_path (str): Path to the agreement PDF file.
        """
        self.pdf_path = pdf_path
        try:
            reader = PdfReader(pdf_path)
            self.pages = reader.pages
        except FileNotFoundError:
            print(f"Error: PDF file not found at '{pdf_path}'")

        self._tables = self._extract_tables()

    def _extract_tables(self):
        """
        Extracts tables from the first page of the PDF using pdfplumber.

        Returns:
            list: List of extracted tables.
        """
        tables = []
        with pdfplumber.open(self.pdf_path) as agreement_pdf:
            page_to_process = agreement_pdf.pages[0]
            for table in page_to_process.extract_tables():
                tables.append(table)
        return tables

    def _get_vendor_info_page(self):
        """
        Finds the page number that contains 'Vendor Information'.

        Returns:
            int or None: Page index if found, otherwise defaults to 2 or None.
        """
        try:
            for i, page in enumerate(self.pages):
                text = page.extract_text()
                if text and "Vendor Information".lower() in text.lower():
                    return i
            return None
        except Exception:
            return 2

    def get_contract_number(self):
        """
        Extracts the contract number from the first page.

        Returns:
            str or None: The extracted contract number or None if not found.
        """
        start_marker = "Agreement #:"
        end_marker = "w/"
        text = self.pages[0].extract_text()

        if start_marker in text and end_marker in text:
            start = text.find(start_marker) + len(start_marker)
            end = text.find(end_marker)
            return text[start:end].strip()
        return None

    def get_co_number(self):
        """
        Extracts the contracting officer's number.

        Returns:
            str: Contracting officer's number or an empty string if extraction fails.
        """
        try:
            return self._tables[0][1][2].replace("5. SOLICITATION NUMBER\n", "").replace("4. ORDER NUMBER", "").strip()
        except Exception:
            return ""

    def get_co_name(self):
        """
        Extracts the contracting officer's name.

        Returns:
            str: Contracting officer's name or an empty string if extraction fails.
        """
        try:
            return self._tables[0][2][0].replace("a. NAME\n", "").strip()
        except Exception:
            return ""

    def get_co_telephone_number(self):
        """
        Extracts the contracting officer's phone number.

        Returns:
            str: Contracting officer's phone number or an empty string if extraction fails.
        """
        try:
            return self._tables[0][2][2].replace("b. TELEPHONE NUMBER (No collect\ncalls)\n", "").strip()
        except Exception:
            return ""

    def get_contractor(self):
        """
        Extracts the contractor's name from the last line on the first page.

        Returns:
            str: Contractor name or an empty string if extraction fails.
        """
        try:
            return self.pages[0].extract_text().splitlines()[-1].split("Vendor:")[1].replace("Page: 1", "").strip()
        except Exception:
            return ""

    def get_contractor_telephone(self):
        """
        Placeholder for contractor's telephone number extraction.

        Returns:
            str: Currently returns an empty string.
        """
        try:
            return ""
        except Exception:
            return ""

    def get_service(self):
        """
        Extracts service description from a specific table.

        Returns:
            str: Service description or an empty string if extraction fails.
        """
        try:
            return self._tables[2][2][0].replace("(Use Reverse and/or Attach Additional Sheets as Necessary)", "").strip()
        except Exception:
            return ""

    def get_vendor_info(self):
        """
        Extracts vendor information such as company name, DBA, UEI, EFT, and addresses.

        Returns:
            dict: A dictionary containing vendor details.
        """
        try:
            markers = ["Company Name:", "DBA:", "UEI:", "EFT:", "Company Address:", "Mailing Address:"]
            vendor_info = {}
            vendor_info_page = self._get_vendor_info_page()

            for i in range(len(markers)):
                start_marker = markers[i]
                end_marker = markers[i+1] if not i == len(markers) - 1 else "Contact"
                text = self.pages[vendor_info_page].extract_text()

                if start_marker in text and end_marker in text:
                    start = text.find(start_marker) + len(start_marker)
                    end = text.find(end_marker)
                    result = text[start:end].strip().replace("\n", "")
                    vendor_info[markers[i].replace(":", "")] = result
            return vendor_info
        except Exception:
            return {
                "Company Address": "",
                "Company Name": "",
                "DBA": "",
                "EFT": "",
                "Mailing Address": "",
                "UEI": ""
            }
