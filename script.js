function uploadImage() {
    const file = document.getElementById("imageUpload").files[0];
    const q1 = document.getElementById("q1").value;
    const q2 = document.getElementById("q2").value;
    const q3 = document.getElementById("q3").value;

    document.getElementById("questionBox").classList.remove("hidden");
    document.getElementById("resultCard").classList.remove("hidden");

    if (!file) {
        document.getElementById("result").innerHTML =
            '<p class="error">Please upload an image first.</p>';
        return;
    }

    const formData = new FormData();
    formData.append("file", file);
    formData.append("q1", q1);
    formData.append("q2", q2);
    formData.append("q3", q3);

    document.getElementById("result").innerHTML = "<p>Processing image...</p>";

    fetch("http://127.0.0.1:5000/predict", {
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

        document.getElementById("result").innerHTML = `
            <div class="result-line"><span class="result-title">Disease:</span> ${data.disease}</div>
            <div class="result-line"><span class="result-title">Confidence:</span> ${data.confidence}%</div>
            <div class="result-line"><span class="result-title">Description:</span> ${data.description}</div>
            <div class="result-line"><span class="result-title">Solution:</span> ${data.solution}</div>
            <div class="result-line"><span class="result-title">Preventive Actions:</span> ${data.prevention}</div>
            <div class="result-line"><span class="result-title">Verification Note:</span> ${data.verification_note}</div>
        `;
    })
    .catch(error => {
        document.getElementById("result").innerHTML =
            `<p class="error">Connection error: ${error}</p>`;
    });
}