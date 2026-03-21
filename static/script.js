function showQuestions() {
    const file = document.getElementById("imageUpload").files[0];
    const crop = document.getElementById("cropName").value.trim();
    const city = document.getElementById("cityName").value.trim();

    if (!file) {
        alert("Please upload an image first.");
        return;
    }

    if (!crop) {
        alert("Please enter crop name.");
        return;
    }

    if (!city) {
        alert("Please enter city name.");
        return;
    }

    document.getElementById("questionBox").classList.remove("hidden");
    document.getElementById("resultCard").classList.add("hidden");
}

function uploadImage() {
    const file = document.getElementById("imageUpload").files[0];
    const crop = document.getElementById("cropName").value.trim();
    const city = document.getElementById("cityName").value.trim();
    const q1 = document.getElementById("q1").value;
    const q2 = document.getElementById("q2").value;
    const q3 = document.getElementById("q3").value;

    document.getElementById("resultCard").classList.remove("hidden");

    if (!file) {
        document.getElementById("result").innerHTML =
            '<p class="error">Please upload an image first.</p>';
        return;
    }

    if (!crop) {
        document.getElementById("result").innerHTML =
            '<p class="error">Please enter crop name.</p>';
        return;
    }

    if (!city) {
        document.getElementById("result").innerHTML =
            '<p class="error">Please enter city name.</p>';
        return;
    }

    const formData = new FormData();
    formData.append("file", file);
    formData.append("crop", crop);
    formData.append("city", city);
    formData.append("q1", q1);
    formData.append("q2", q2);
    formData.append("q3", q3);

    document.getElementById("result").innerHTML = "<p>Processing image and weather data...</p>";

    fetch("http://127.0.0.1:5000/api/predict-with-weather", {
        method: "POST",
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            document.getElementById("result").innerHTML =
                `<p class="error">Error: ${data.error}</p>`;
            return;
        }

        const disease = data.disease_result;
        const weather = data.weather_result;
        const advisoryList = weather.advisories
            .map(item => `<li>${item}</li>`)
            .join("");

        document.getElementById("result").innerHTML = `
            <div class="result-line"><span class="result-title">Disease:</span> ${disease.disease}</div>
            <div class="result-line"><span class="result-title">Confidence:</span> ${disease.confidence}%</div>
            <div class="result-line"><span class="result-title">Description:</span> ${disease.description}</div>
            <div class="result-line"><span class="result-title">Solution:</span> ${disease.solution}</div>
            <div class="result-line"><span class="result-title">Preventive Actions:</span> ${disease.prevention}</div>
            <div class="result-line"><span class="result-title">Verification Note:</span> ${disease.verification_note}</div>

            <hr>

            <div class="result-line"><span class="result-title">City:</span> ${weather.city}</div>
            <div class="result-line"><span class="result-title">Crop:</span> ${weather.crop}</div>
            <div class="result-line"><span class="result-title">Weather Advisories:</span></div>
            <ul>${advisoryList}</ul>

            <hr>

            <div class="result-line"><span class="result-title">Combined Tip:</span> ${data.combined_tip}</div>
        `;
    })
    .catch(error => {
        document.getElementById("result").innerHTML =
            `<p class="error">Connection error: ${error}</p>`;
    });
}