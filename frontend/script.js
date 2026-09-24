const API_BASE_URL = "http://127.0.0.1:8000";

const DEVICE_ID = "PLANT-001";


// ---------------------------------------------------------
// Fetch Latest Sensor Data
// ---------------------------------------------------------

async function fetchLatestData() {

    try {

        const response = await fetch(
            `${API_BASE_URL}/api/latest?device_id=${DEVICE_ID}`
        );

        if (!response.ok) {

            throw new Error(
                "No sensor data available"
            );

        }

        const data = await response.json();

        updateDashboard(data);

    }

    catch (error) {

        console.error(error);

        showMessage(
            "Waiting for sensor data...",
            true
        );

    }

}


// ---------------------------------------------------------
// Update Dashboard
// ---------------------------------------------------------

function updateDashboard(data) {

    document.getElementById(
        "moisture"
    ).textContent =
        `${data.soil_moisture}%`;


    document.getElementById(
        "temperature"
    ).textContent =
        `${data.temperature} °C`;


    document.getElementById(
        "humidity"
    ).textContent =
        `${data.humidity}%`;


    document.getElementById(
        "pump"
    ).textContent =
        data.pump_status;


    const statusElement =
        document.getElementById(
            "plantStatus"
        );


    statusElement.textContent =
        data.plant_status;


    if (
        data.plant_status ===
        "HEALTHY"
    ) {

        statusElement.className =
            "status healthy";

    }

    else {

        statusElement.className =
            "status needs-water";

    }


    document.getElementById(
        "threshold"
    ).value =
        data.threshold;


    document.getElementById(
        "lastUpdate"
    ).textContent =
        formatDate(data.timestamp);

}


// ---------------------------------------------------------
// Fetch History
// ---------------------------------------------------------

async function fetchHistory() {

    try {

        const response = await fetch(
            `${API_BASE_URL}/api/history?device_id=${DEVICE_ID}&limit=10`
        );

        if (!response.ok) {

            return;

        }

        const result =
            await response.json();

        const table =
            document.getElementById(
                "historyTable"
            );

        table.innerHTML = "";


        result.data
            .slice()
            .reverse()
            .forEach(reading => {

                const row =
                    document.createElement(
                        "tr"
                    );


                row.innerHTML = `

                    <td>
                        ${formatDate(
                            reading.timestamp
                        )}
                    </td>

                    <td>
                        ${reading.soil_moisture}%
                    </td>

                    <td>
                        ${reading.temperature}°C
                    </td>

                    <td>
                        ${reading.humidity}%
                    </td>

                `;


                table.appendChild(row);

            });

    }

    catch (error) {

        console.error(
            "History error:",
            error
        );

    }

}


// ---------------------------------------------------------
// Manual Watering
// ---------------------------------------------------------

async function waterPlant() {

    try {

        const response = await fetch(
            `${API_BASE_URL}/api/water`,
            {
                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body: JSON.stringify({
                    device_id:
                        DEVICE_ID
                })
            }
        );


        const data =
            await response.json();


        if (!response.ok) {

            throw new Error(
                data.detail ||
                "Watering failed"
            );

        }


        showMessage(
            `Plant watered successfully. Moisture: ${data.moisture_before}% → ${data.moisture_after}%`,
            false
        );


        fetchLatestData();

        fetchHistory();

    }

    catch (error) {

        showMessage(
            error.message,
            true
        );

    }

}


// ---------------------------------------------------------
// Update Threshold
// ---------------------------------------------------------

async function updateThreshold() {

    const threshold =
        Number(
            document.getElementById(
                "threshold"
            ).value
        );


    if (
        threshold < 0 ||
        threshold > 100
    ) {

        showMessage(
            "Threshold must be between 0 and 100.",
            true
        );

        return;

    }


    try {

        const response = await fetch(
            `${API_BASE_URL}/api/threshold`,
            {
                method: "PUT",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body: JSON.stringify({
                    threshold:
                        threshold
                })
            }
        );


        const data =
            await response.json();


        if (!response.ok) {

            throw new Error(
                "Threshold update failed"
            );

        }


        showMessage(
            `Threshold updated to ${data.threshold}%`,
            false
        );


        fetchLatestData();

    }

    catch (error) {

        showMessage(
            error.message,
            true
        );

    }

}


// ---------------------------------------------------------
// Message Display
// ---------------------------------------------------------

function showMessage(
    message,
    isError
) {

    const element =
        document.getElementById(
            "message"
        );


    element.textContent =
        message;


    element.style.display =
        "block";


    if (isError) {

        element.style.background =
            "#ffe1e1";

    }

    else {

        element.style.background =
            "#dff5e1";

    }


    setTimeout(() => {

        element.style.display =
            "none";

    }, 4000);

}


// ---------------------------------------------------------
// Date Formatting
// ---------------------------------------------------------

function formatDate(timestamp) {

    if (!timestamp) {

        return "--";

    }


    const date =
        new Date(timestamp);


    return date.toLocaleString();

}


// ---------------------------------------------------------
// Initial Load
// ---------------------------------------------------------

fetchLatestData();

fetchHistory();


// ---------------------------------------------------------
// Automatic Dashboard Refresh
// ---------------------------------------------------------

setInterval(() => {

    fetchLatestData();

    fetchHistory();

}, 5000);