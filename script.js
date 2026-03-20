function uploadImage() {
    let file = document.getElementById("imageUpload").files[0];
    if (!file) {
        alert("Select an image!");
        return;
    }

    let formData = new FormData();
    formData.append("file", file);

    fetch("http://127.0.0.1:5000/predict", {
        method: "POST",
        body: formData
    })
    .then(res => res.json())
    .then(data => {
        document.getElementById("result").innerText = data.result;
    })
    .catch(err => {
        console.log(err);
        document.getElementById("result").innerText = "Error connecting to server";
    });
}