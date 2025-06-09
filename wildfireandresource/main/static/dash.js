// domains
const DEV_URL = "http://localhost:8000/";
// const PROD_URL = "https://vipr.pythonanywhere.com/";

let url = DEV_URL; // or PROD_URL in production.

document.addEventListener('DOMContentLoaded', () => {
    let totalEntries = 19;
    let progressCard = document.getElementById('progress-card');
    progressCard.innerHTML = showProgressCard(0, 19)
        fetch(url + 'fetch_form_data/')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(jsonData => {
            totalEntries = jsonData.data.length;
            return fetch(url + `forms/check-filled/4`)
        })
        .then(response => {
            if (!response.ok && response.status === 404) {
                // throw new Error(`HTTP error! status: ${response.status}`);
                console.error('user form not found')
            }
            return response.json();
        })
        .then(data => {
            let percentage = 0;

            if(data.are_filled) {
                percentage = 100
                progressCard.innerHTML = showProgressCard(percentage, 0)
            } else if(!data.are_filled && data.unfilled_answers) {
                percentage = 100 - Math.floor((data.unfilled_answers.length / totalEntries) * 100);
                progressCard.innerHTML = showProgressCard(percentage, data.unfilled_answers.length)
            } else {
                progressCard.innerHTML = `<p>no form data</p>`
            }

        })
        .catch(error => {
            console.error('Error fetching or parsing JSON:', error);
            contentMain.innerHTML = "<p>Error loading form.</p>"; // Display an error message
        });
});

function showProgressCard(percentage, remainingEntries) {
    return `
        <div class="progress-circle" style="--progress-percentage: ${percentage};">
            <svg viewBox="0 0 69 69">
                <circle cx="50%" cy="50%" r="30"></circle>
                <circle class="progress-value" cx="50%" cy="50%" r="30"></circle>
            </svg>
            <div class="progress-text">${percentage}%</div>
        </div>
        <div>
            <h6 class="card-title">Emergency Equipment Shift Ticket</h6>
            <p class="card-text">${remainingEntries} entry fields remaining</p>
        </div>
    `
}