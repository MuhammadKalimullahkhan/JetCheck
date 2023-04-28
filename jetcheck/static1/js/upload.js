const form = document.querySelector("#fileUploadForm");
const uploadArea = document.querySelector("#fileUploadArea");
const messageText = form.querySelector("span");
const fileInput = document.querySelector("#fileInput");

uploadArea.addEventListener('click', () => {
    fileInput.click();
});
fileInput.addEventListener('change', () => {
    messageText.style.color = "var(--jc-primary-color)";
    messageText.style.fontSize = "1.3rem";
    messageText.textContent = fileInput.files[0].name

});
form.addEventListener('submit', (event) => {
    event.preventDefault();
    submitForm();
});
uploadArea.addEventListener('dragover', () => {
    event.preventDefault();
    form.classList.add("active");
    messageText.textContent = "Release to Upload File";
})
uploadArea.addEventListener('dragleave', () => {
    form.classList.remove("active");
    messageText.textContent = "Drag & Drop or Click to Browse File"
})
uploadArea.addEventListener('drop', (event) => {
    event.preventDefault();
    fileInput.files = event.dataTransfer.files;
    submitForm();
})

function submitForm() {
    let data = new FormData(form);
    loadingScreen.removeAttribute("hidden");

    $.ajax({
        url: "",
        type: "POST",
        contentType: false,
        processData: false,
        data: data,
        xhrFields: {
            onprogress: function (e) {
                const response = e.currentTarget.response;
                let currentResponse = "";
                let x = response;

                if (response) {
                    x = response.split('\n');
                    x = x.filter((s) => s !== "");
                    currentResponse = x[x.length - 1];

                    loadingScreen.querySelector("h3").textContent = "Please Wait, " + currentResponse;
                }
            }
        },
        success: (data, status, xhr) => {
            if (data.error) {
                alert(data.error)
            }
            // document.querySelector(".loading-screen").setAttribute("hidden", "");
            window.location.href = data.url;
        },
        error: (xhr, status, error) => {
            console.log(error)
            loadingScreen.querySelector("h3").textContent = "Error " + error;
            setTimeout(() => {
                document.querySelector(".loading-screen").setAttribute("hidden", "");
            }, 1000);
        }
    });
}