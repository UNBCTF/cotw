var entityMap = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#39;',
    '/': '&#x2F;',
    '`': '&#x60;',
    '=': '&#x3D;'
};

function escapeHtml (string) {
    return String(string).replace(/[&<>"'`=\/]/g, function (s) {
    return entityMap[s];
    });
}

// Function to construct the table
function buildTable(data, spot) {
    let table = "";
    var headert = "Time (UTC)";
    
    if (spot === "current/") {
        spot = "#current-solves";
    } else {
        spot = "#leaderboard";
	headert = "Points";
    }
    
    if (data["message"] == "") {
        table = $('<p>No Solves yet. Check back later!</p>');
    } else {
        // Create the table element
        table = $('<table style="display:block;overflow-y:auto;overflow-x:hidden;height:250px;"></table>');

        // Add table header (optional)
        let headerRow = $('<tr></tr>');
        const headers = ["Username", headert];
        headers.forEach(header => {
            headerRow.append(`<th style="padding: 8px;">${header}</th>`);
        });
        table.append(headerRow);

        // Loop through each row in the message array and create table rows
        data.message.forEach(rowData => {
            let row = $('<tr></tr>');  // Create a new row
            rowData.forEach(cellData => {
            row.append(`<td style="padding: 8px;">${escapeHtml(cellData)}</td>`); // Add each cell to the row
            });
            table.append(row); // Add the row to the table
        });
    }

    // Append the table to the container (e.g., a div with id="table-container")
    $(spot).html(table);
}

function checkAnswer(inputId, outputId) {
    var userInput = document.getElementById(inputId).value;

    // Check if input is in correct format regex '^UNBCTF{[.*]}$'
    if (userInput.match(/^UNBCTF{.*}$/) === null) {
        showOutput(outputId, 'Remember: all flags are like UNBCTF{...}', 'warning');
        return;
    }
 
    fetch("https://cotw.unbcybersec.com/check/", {
        method: "POST",
        body: "flag="+ userInput,
        headers: {"Content-type": "application/x-www-form-urlencoded; charset=UTF-8"}
    }).then((response) => response.json()).then((json) => {
        if (json["message"] === "Correct") {
            showOutput(outputId, 'Success! You got the flag!', 'success');
            setTimeout(1000)
            $('#exampleModal').modal('show')
        } else {
            showOutput(outputId, 'Incorrect. Try harder!', 'danger');
        }
    });
}

function showOutput(outputId, message, type) {
    var outputDiv = document.getElementById(outputId);
    outputDiv.className = 'alert alert-' + type + ' mt-2 mb-0';
    outputDiv.role = 'alert';
    outputDiv.textContent = message;
}

function loadTables(value) {
    fetch("https://cotw.unbcybersec.com/" + value, {
        method: "GET",
    }).then((response) => response.json()).then((json) => {
        buildTable(json, value);
    });
}

function getCSRF(name) {
  const match = document.cookie
                .match(new RegExp("(^| )" + name + "=([^;]+)"));
  if (match) return match[2];
  return null;
}

document.getElementById("user-submit").addEventListener("click", function () {
	var sdata = document.getElementById("username").value;
	fetch("https://cotw.unbcybersec.com/submit-solve/", {
        method: "POST",
        body: "username=" + sdata,
	credentials: "same-origin",
        headers: {"Content-type": "application/x-www-form-urlencoded; charset=UTF-8", "X-CSRF-TOKEN": getCSRF("csrf_access_token")}
    }).then((response) => response.json()).then((json) => {
        if (json["message"] === "Submitted") {
            showOutput("submit-output", 'Points added to user successfully!', 'success');
            setTimeout(1000)
            $('#exampleModal').modal('hide')
        } else {
            showOutput("submit-output", json["message"], 'danger');
        }
    });
});

endpoints = ["current/", "global/"]
endpoints.forEach(loadTables)
