// domains
const DEV_URL = "http://localhost:8000/";
// const PROD_URL = "https://vipr.pythonanywhere.com/";

let url = DEV_URL; // or PROD_URL in production.

let form_data = {};
let page = 0;
let last_page = 1;
let isFormChanged = false;

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
          const cookie = cookies[i].trim();
          // Does this cookie string begin with the name we want?
          if (cookie.substring(0, name.length + 1) === (name + '=')) {
              cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
              break;
          }
      }
  }
  return cookieValue;
}


function getInitials(name, capitalize = true) {
  // Handle null, undefined, and empty input
  if (!name) {
    return "";
  }

  // Remove leading and trailing spaces, and replace multiple spaces with single spaces
  const cleanName = name.trim().replace(/\s+/g, " ");

  // Split the name into an array of words
  const words = cleanName.split(" ");

  // Extract the first letter of each word
  const initials = words.map((word) => word.charAt(0));

  // Join the initials into a string
  let result = initials.join("");

  // Capitalize the initials if specified
  if (capitalize) {
    result = result.toUpperCase();
  }

  return result;
}

document.addEventListener('DOMContentLoaded', () => {
    fetch(url + 'fetch_form_data/') // Replace 'your_json_file.json' with the actual path
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(jsonData => {
            form_data = jsonData;
            last_page = jsonData.Num_Pages;

        })
        .catch(error => {
            console.error('Error fetching or parsing JSON file configuration:', error);
            document.getElementById('content-main').innerHTML = "<p>Error loading json configuration file.</p>"; // Display an error message
        });
});

function create_shift_ticket(){
    const csrfToken = getCookie('csrftoken'); // Get CSRF token
    document.getElementById("main_section").style.display = "none";
    let project_id = document.getElementById("projectDropdown").value;
    fetch('/create_shift_ticket/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken // Add CSRF token to headers
        },
        body: JSON.stringify({project_id: project_id})
    })
    .then(response => {
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return response.json();
    })
    .then(data => {
        console.log(data);
        document.getElementById("userformid").value = data.user_form_id;
        construct_page(1, "slide-left");
        data.useranswer.forEach(item => {
            document.getElementById(item.question_number + '' + item.table_row + '' + item.table_col).value = item.answer;
        });
            
        page = 2;
            
    })
    .catch(error => {
        console.error('Network error:', error);
    });
}

function continue_form_filling(form_id){
    const csrfToken = getCookie('csrftoken'); // Get CSRF token
    document.getElementById("main_section").style.display = "none";
    fetch('/begin_form_filling/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken // Add CSRF token to headers
        },
        body: JSON.stringify({form_id: form_id})
    })
    .then(response => {
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return response.json();
    })
    .then(data => {
        console.log(data);
        document.getElementById("userformid").value = data.user_form_id;
        construct_page(1, "slide-left");
        data.useranswer.forEach(item => {
            document.getElementById(item.question_number + '' + item.table_row + '' + item.table_col).value = item.answer;
        });
            
        page = 2;
            
    })
    .catch(error => {
        console.error('Network error:', error);
    });
}


function constructInfoPage(slide){
    const userformid = document.getElementById("userformid").value;
    let next_txt = "Begin";

    if(userformid !== "0"){
        next_txt = "Continue";
    }

    document.getElementById('content-main').innerHTML = `<div class="form-container ${slide}">
                    <div class="main-info" style="max-width: 750px;">
                        <h2>${form_data.Title}</h2>
                        <p>${form_data.Info}</p>
                    </div>
                    <div class="main-info" style="max-width: 750px; margin-top: 10px; margin-bottom: 10px;">
                       <div class="form-group" style="display: flex; align-items: center; justify-content: center;">
                            <select id="projectDropdown" name="project" class="form-control" style="text-align:center">
                                <option value="" selected>--- Select a Project or Leave Blank for Manual Entry ---</option>
                                <option value="wapiti">WAPITI</option>
                            </select>
                        </div> 
                    </div>
                    <div class="d-flex justify-content-center mt-4" style="max-width: 750px;">
                        <div class="d-flex justify-content-between" style="width: 300px;">
                            <a href="http://localhost:8000/dashboard" class="btn btn-secondary">Back</a>
                            <button type="button" class="btn btn-primary" id="next-button">${next_txt}</button>
                        </div>
                    </div>
                </div>`;

            // Add event listeners for "Previous" and "Next" buttons here if needed.
            const nextButton = document.getElementById('next-button');

            nextButton.addEventListener('click', () => {
                
                handle_next();
                // Your logic for the next button
            });
}

function construct_last_page(){
    isFormChanged = false;
    let user_form_id= document.getElementById('userformid').value;
    let generatedFormUrl = DEV_URL + "forms/shift-ticket/" + user_form_id;

    document.getElementById('content-main').innerHTML = `<div class="form-container slide-left">
            <div class="main-info">
                <h2>Completed !!</h2>
                <p>Thank you for completing the form. 
                Your submission has been successfully recorded.  
                You may return at any time to review and update your information.  
                Please select "Download" to save a copy of your completed form 
                or "Preview" to review the form before downloading.</p>
            
            <div class="d-flex justify-content-center mt-4">
                <div class="d-flex justify-content-between" style="width: 300px;">
                    <button type="button" class="btn btn-secondary" id="prev-button">Previous</button>
                    <a href=${generatedFormUrl} class="btn btn-info" id="preview-button">Preview</a>
                    <a href=${generatedFormUrl} download class="btn btn-primary" id="download-button">Download</a>
                </div>
            </div>
            </div>
        </div>`;

    const prevButton = document.getElementById('prev-button');

    prevButton.addEventListener('click', () => {
        handle_prev();
        // Your logic for the previous button
    });
}

function construct_page(page_num, slide){
    const userformid = document.getElementById('userformid').value;

    checkFormFillStatus(userformid)
    .then(data => {
        let pageLinks = createPageLinks(data, form_data, page_num)
        document.getElementById('page-nav').innerHTML =  `<ul class="pagination">${pageLinks}</ul>`
    })
    .catch(error => console.error('Error fetching or parsing JSON:', error));

    isFormChanged = false;

    let formHTML = `<form id="myForm"><div class="${slide} form-container"> <h2>Section ${page_num}</h2>`;
        form_data.data.forEach(item => {
            if(item.Page === page_num){
                formHTML += `<div class="mb-3">`

                if (item.Type === "question") {
                    formHTML += `<label for="${item.No}00" class="form-label">${item.No}. ${item.Entry}</label>`;
                    formHTML += `<input type="${item.Answer}" class="form-control" id="${item.No}00" aria-describedby="${item.Entry.replace(/\s+/g, '')}Help" required>`;
                } else if (item.Type === "select") {
                    formHTML += `<label for="${item.No}00" class="form-label">${item.No}. ${item.Entry}</label>`;
                    formHTML += `<select class="form-select" id="${item.No}00" aria-describedby="${item.Entry.replace(/\s+/g, '')}Help" required><option value="">Select an option</option>`
                    for (let i = 0; i < item.Options_Num; i++) {
                        const option = item.Options[i];
                        formHTML += `<option value="${option}">${option}</option>`
                    }
                    formHTML += `</select>`;
                }else if (item.Type === "textarea"){
                    formHTML += `<label for="${item.No}00" class="form-label">${item.No}. ${item.Entry}</label>`;
                    formHTML += `<textarea class="form-control" id="${item.No}00" aria-describedby="${item.Entry.replace(/\s+/g, '')}Help" rows="3"></textarea>`;
                } else if(item.Type === "table"){
                    let tableHTML = `<h2>${item.Entry}</h2>
                     <table class="table table-bordered">
                     <thead><tr>`;

                    // Create table headers
                    item.Cols.forEach(col => {
                        tableHTML += `<th>${col}</th>`;
                    });

                    tableHTML += `</tr></thead><tbody>`;

                    // Create table rows with input fields
                    for (let i = 0; i < item.Rows_num; i++) {
                        tableHTML += `<tr>`;
                        for (let j = 0; j < item.Cols_num; j++) {
                            const inputType = item.Answer[j];
                            tableHTML += `<td><input type="${inputType}" id="${item.No}${i}${j}" class="form-control"></td>`;
                        }
                        tableHTML += `</tr>`;
                    }

                    tableHTML += `</tbody></table>`;
                    formHTML += tableHTML;
                }

                formHTML += `<div id="${item.Entry.replace(/\s+/g, '')}Help" class="form-text">${item.Description}</div>
                </div>`;
            }

        });

        formHTML += `<div class="d-flex justify-content-start mt-4">
                        <div class="d-flex justify-content-between" style="width: 360px;">
            <button type="button" class="btn btn-secondary" id="prev-button">Previous</button>
            <button type="submit" class="btn btn-outline-primary" id="save-button">Save</button>
            <button type="submit" class="btn btn-primary" id="next-button">Save & Proceed.</button>
        </div></div></div>
        
            <!-- pagination -->
            <nav aria-label="page navigation" class="mt-3" id="page-nav">
             
            </nav>
        </form>`;

        document.getElementById('content-main').innerHTML = formHTML;

        // Track form changes
        const form = document.getElementById('myForm');

        form.addEventListener('input', () => isFormChanged = true);
        form.addEventListener('change', () => isFormChanged = true);
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            isFormChanged = false;
        });

        // Add event listeners for "Previous" and "Next" buttons here if needed.
        const prevButton = document.getElementById('prev-button');
        const nextButton = document.getElementById('next-button');
        const saveButton = document.getElementById('save-button');

        prevButton.addEventListener('click', () => {
            handle_prev();
            // Your logic for the previous button
        });

        nextButton.addEventListener('click', () => {
            event.preventDefault();
            handle_next();
            // Your logic for the next button
        });

        saveButton.addEventListener('click', () => {
            event.preventDefault();
            handleSave()
        })
        
        
}



function handle_next() {
    isFormChanged = false;
    const userId = parseInt(document.getElementById("userid").value);
    const formId = parseInt(document.getElementById("formid").value);
    if(page === 0){
        sendUserFormData(userId, formId)
        .then(data => {
            // Process successful response
            document.getElementById("userformid").value = data.user_form_id;
            construct_page(page, "slide-left");
            data.useranswer.forEach(item => {
                document.getElementById(item.question_number + '' + item.table_row + '' + item.table_col).value = item.answer;
            });
            
            
            

        })
        .catch(error => {
            // Handle errors from fetch or server
            console.error("Error sending data:", error);
        });
    }
    else if(page === last_page){
        const userformid =  parseInt(document.getElementById("userformid").value);
        // const myForm = document.getElementById('myForm');
        // if (!myForm.checkValidity()) {
        //     return; // Stop further execution of the click handler
        // }
        sendFormData(userId, formId, page, userformid)
        .then(data => {
            // check filled answers
            if(data.message !== 'data'){
                throw new Error('Could not post data.')
            }
            return fetch(`/forms/check-filled/${userformid}`)
        })
        .then(res=>{
            if(res) return res.json()
        })
        .then(data => {
            if(data.are_filled) {
                construct_last_page();
            } else {
                const modalBody = document.getElementById("unfilled-data");
                let unfilledTemplate = '';
                data.unfilled_answers.forEach(answer => {
                    unfilledTemplate += `<div class="row align-items-start">
                                                    <div class="col">
                                                     Section ${answer.question_page}
                                                    </div>
                                                    <div class="col">
                                                      Entry ${answer.question_number}
                                                    </div>
                                                  </div>`
                });
                modalBody.innerHTML = unfilledTemplate;
                const modal = new bootstrap.Modal(document.getElementById('unfilled-modal'));
                modal.show();
                page -= 1
            }
        })
        .catch(error => {
            // Handle errors from fetch or server
            console.error("Error sending data:", error);
        });
    }
    else {
        const userformid =  parseInt(document.getElementById("userformid").value);
        const myForm = document.getElementById('myForm');
        // if (!myForm.checkValidity()) {
        //     return; // Stop further execution of the click handler
        // }
        sendFormData(userId, formId, page, userformid)
        .then(data => {
            // Process successful response
            construct_page(page, "slide-left");
            data.useranswer.forEach(item => {
                document.getElementById(item.question_number+ '' + item.table_row + '' + item.table_col).value = item.answer;
            });
            if(page === last_page){
                document.getElementById('next-button').textContent = "Finish";
            }
            else if(page > last_page) {
                //handle finish
                page = page;
            }
            
        })
        
        .catch(error => {
            // Handle errors from fetch or server
            console.error("Error sending data:", error);
        });
    }
    page = page + 1;
}

function handle_prev() {
    isFormChanged = false;
    const userformid =  parseInt(document.getElementById("userformid").value);
    
    page = page - 1;
    if(page < 1){
        page = 0;
        constructInfoPage("slide-right");
    }else{
        
        get_form_data_per_page(userformid, page)
        .then(data => {
            // Process successful response
            construct_page(page, "slide-right");
            data.form_data.forEach(item => {
                document.getElementById(item.question_number+ '' + item.table_row + '' + item.table_col).value = item.answer;
            });
            if(page === last_page){
                document.getElementById('next-button').textContent = "Finish";
            }
        })
        .catch(error => {
            // Handle errors from fetch or server
            console.error("Error sending data:", error);
        });
        document.getElementById("prev-button").style.display = "block";
    }
    
    // Add any other logic you want to execute when the button is clicked
}

function pageChangeHandler(chosenPage) {
    event.preventDefault();
    if(isFormChanged) {
        handleFormChange(chosenPage)
        return;
    }
    const userformid =  parseInt(document.getElementById("userformid").value);
    const slideAnimation = page >= chosenPage ? 'slide-right' : 'slide-left'

    page = parseInt(chosenPage);
    if(page < 1){
        page = 0;
        constructInfoPage(slideAnimation);
    }else{
        get_form_data_per_page(userformid, page)
        .then(data => {
            // Process successful response
            construct_page(page, slideAnimation);
            data.form_data.forEach(item => {
                document.getElementById(item.question_number+ '' + item.table_row + '' + item.table_col).value = item.answer;
            });
            if(chosenPage == 2){
            document.getElementById("600").value = equipment_make;
            document.getElementById("700").value = equipment_model;
        }
            if(page === last_page){
                document.getElementById('next-button').textContent = "Finish";
            }
        })
        .catch(error => {
            // Handle errors from fetch or server
            console.error("Error sending data:", error);
        });
        document.getElementById("prev-button").style.display = "block";
    }
    
}

function handleFormChange(chosenPage) {
    const modalBody = document.getElementById("change-action");
    modalBody.innerHTML = `
                            <div>Changes were detected.</div>
                            <div class="d-flex flex-row-reverse">
                                <button type="button" class="btn btn-primary" id="confirm-save-button" data-bs-dismiss="modal">Save</button>
                                <button type="button" class="btn btn-secondary mx-4" id="discard-button" data-bs-dismiss="modal">Discard</button>
                           </div>
                        `;
    const modal = new bootstrap.Modal(document.getElementById('save-modal'));
    const confirmSaveBtn = document.getElementById("confirm-save-button");
    const discardBtn = document.getElementById("discard-button");

    confirmSaveBtn.addEventListener('click', () => {
        handleSave();
        pageChangeHandler(chosenPage);
    });

    discardBtn.addEventListener('click', () => {
        isFormChanged = false;
        pageChangeHandler(chosenPage);
    });

    modal.show();
}

// JavaScript (Client-side)
const sendFormData = async (userId, formId, page_num,userformid, changePage=true) => {
    const currpagedata = [];
    form_data.data.forEach(item => {
        if(item.Page === page_num){
            
            if(item.Type === "table"){
                for (let i = 0; i < item.Rows_num; i++) {
                    for (let j = 0; j < item.Cols_num; j++) {
                        const answerval = document.getElementById(item.No + '' + i + '' +  j).value;
                        if(answerval !== ""){
                            const curranswer = {};
                            curranswer.Answer = answerval;
                            curranswer.No = item.No;
                            curranswer.Page = item.Page;
                            curranswer.Answer_Type = item.Answer[j];
                            curranswer.Col = j;
                            curranswer.Row = i;
                            curranswer.UserFormId = userformid;
                            curranswer.FormId = formId;
                            curranswer.UserId = userId;
                            currpagedata.push(curranswer);
                        }
                        
                    }
                }
            }else{
                const curranswer = {};
                curranswer.Answer = document.getElementById(item.No + '00').value;
                curranswer.No = item.No;
                curranswer.Page = item.Page;
                curranswer.Answer_Type = item.Answer;
                curranswer.Col = 0;
                curranswer.Row = 0;
                curranswer.UserFormId = userformid;
                curranswer.FormId = formId;
                curranswer.UserId = userId;
                currpagedata.push(curranswer);
            }
            
            
        }
    });
    const pagedata = {};
    pagedata.user_form_id = userformid;
    pagedata.form_data = currpagedata;
    pagedata.currpage = changePage ? page_num + 1 : page_num;
    try {
      const response = await fetch(url + 'save_form_data/', { // Replace with your Django view URL
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCookie('csrftoken'), // Include CSRF token for Django
        },
        body: JSON.stringify(pagedata),
      });
  
      if (!response.ok) {
          const errorData = await response.json(); // Get error details from the server
          throw new Error(errorData.error || 'Server error'); // Throw an error with message
      }

      return await response.json(); // Return data from the fetch promise
  
    } catch (error) {
      console.error('Error:', error);
      // Handle error (e.g., display error message to the user)
      throw error; // Re-throw error to be handled by caller if needed
    }
  };

const sendUserFormData = async (userId, formId) => {
    try {
      const response = await fetch(url + 'begin_form_filling/', { // Replace with your Django view URL
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCookie('csrftoken'), // Include CSRF token for Django
        },
        body: JSON.stringify({
          user_id: userId,
          form_id: formId,
        }),
      });
  
      if (!response.ok) {
          const errorData = await response.json(); // Get error details from the server
          throw new Error(errorData.error || 'Server error'); // Throw an error with message
      }

      return await response.json(); // Return data from the fetch promise
  
    } catch (error) {
      console.error('Error:', error);
      // Handle error (e.g., display error message to the user)
      throw error; // Re-throw error to be handled by caller if needed
    }
  };

const get_form_data_per_page = async (userformid, page) => {
    try {
      const response = await fetch(url + 'get_form_data_per_page/', { // Replace with your Django view URL
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCookie('csrftoken'), // Include CSRF token for Django
        },
        body: JSON.stringify({
          user_form_id: userformid,
          page: page
        }),
      });
  
      if (!response.ok) {
          const errorData = await response.json(); // Get error details from the server
          throw new Error(errorData.error || 'Server error'); // Throw an error with message
      }

      return await response.json(); // Return data from the fetch promise
  
    } catch (error) {
      console.error('Error:', error);
      // Handle error (e.g., display error message to the user)
      throw error; // Re-throw error to be handled by caller if needed
    }
  };


/**
 * Helper functions
 */

// get the CSRF token (from Django's cookies)
function getCookie(name) {
      let cookieValue = null;
      if (document.cookie && document.cookie !== '') {
          const cookies = document.cookie.split(';');
          for (let i = 0; i < cookies.length; i++) {
              const cookie = cookies[i].trim();
              // Does this cookie string begin with the name we want?
              if (cookie.substring(0, name.length + 1) === (name + '=')) {
                  cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                  break;
              }
          }
      }
      return cookieValue;
  }

// form saving
function handleSave(){
    isFormChanged = false;
    const userId = parseInt(document.getElementById("userid").value);
    const formId = parseInt(document.getElementById("formid").value);
    const userformid =  parseInt(document.getElementById("userformid").value);

    sendFormData(userId, formId, page, userformid, false)
    .then(data => {
        // Process successful response
        construct_page(page, '')
        data.useranswer.forEach(item => {
                document.getElementById(item.question_number + '' + item.table_row + '' + item.table_col).value = item.answer;
        });
    })
    .catch(error => {
        // Handle errors from fetch or server
        console.error("Error sending data:", error);
    });
}

// check form fill status
function checkFormFillStatus(userformid) {
    return fetch(url + `forms/check-filled/${userformid}`)
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    });
}

// create page links
function createPageLinks(formFillStatus, form_data, page) {
    let pageLinks = '';

    for (let i = 1; i <= form_data.Num_Pages; i++) {
        const isCurrentPage = (page === i);

        let color = '#198754';
        let borderWidth = '2px';
        let fontWeightClass = '';

        if (formFillStatus.are_filled) {
            // all filled, keep default green
        } else if (formFillStatus.unfilled_answers) {
            const hasUnfilled = formFillStatus.unfilled_answers.some(ans => ans.question_page === i);
            if (hasUnfilled) {
                color = '#ffc107';
                borderWidth = '2px';
                fontWeightClass = 'fw-bold';
            }
        } else {
            color = '#000';
        }

        if (isCurrentPage) {
            pageLinks += `
                <li class="page-item active">
                    <button style="width: 100px" class="page-link me-2" onclick="pageChangeHandler(${i})">${i}</button>
                </li>`;
        } else {
            pageLinks += `
                <li class="page-item bg">
                    <button
                        style="width: 100px; border: ${borderWidth} solid ${color}; color: ${color}"
                        class="page-link me-2 ${fontWeightClass}"
                        onclick="pageChangeHandler(${i})"
                    >${i}</button>
                </li>`;
        }
    }

    return pageLinks;
}

