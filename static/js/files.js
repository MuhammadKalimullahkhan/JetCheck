// document.querySelector("#search-btn").addEventListener('click', () => {
//     document.querySelector("#search-model").classList.remove("d-none")
// });
// document.querySelector("#close-model").addEventListener('click', () => {
//     document.querySelector("#search-model").classList.add("d-none")
// });

let taost;

function getFileDataByID(url) {
    const fileDetailsModal = $("#fileDetailsModal");
    const fileTitle = fileDetailsModal.find("#title");
    const fileSize = fileDetailsModal.find("#size");
    const uploadDate = fileDetailsModal.find("#uploadDate");
    const fileDescription = fileDetailsModal.find("#description");
    const filePlagiarism = fileDetailsModal.find("#plagiarism");
    const downloadBtn = fileDetailsModal.find("#downloadBtn");
    const aiElement = fileDetailsModal.find("#ai");
    

    $.ajax({
        url: url,
        method: 'POST',
        contentType: false,
        dataType: false,
        success: (data, status, xhr) => {
            const { title, size, upload_date, description, plagiarism, download_path, ai, human } = data;
            const date = new Date(upload_date);
            const formattedDate = `${date.getDate().toString().padStart(2, '0')}-${(date.getMonth() + 1).toString().padStart(2, '0')}-${date.getFullYear()}`;
            const capitalizedTitle = title.split(" ").map(word => word.slice(0, 1).toUpperCase() + word.slice(1)).join(" ");
            fileTitle.text(capitalizedTitle.substring(0, title.indexOf('-')).trim());
            fileSize.text(size);
            uploadDate.text(formattedDate);
            fileDescription.text(description);
            filePlagiarism.text(plagiarism + "%");
            downloadBtn.attr("href", download_path);
            if(ai > 20){
                aiElement.text(Math.round(ai + 4) + "%");
            }
            else if (ai > 100){
                aiElement.text("100%");
            }else{
                aiElement.text(ai+"%");
            }
        },
        error: (xhr, status, error) => {
            console.log(error)
        }
    })
}

function deleteFile(url) {
    let c = confirm("Are you sure want to delete this file?");
    if (c == true) {
        $.ajax({
            url: url,
            method: "POST",
            contentType: false,
            dataType: false,
            success: (data, status, xhr) => {
                window.location.reload();
            },
            error: (xhr, status, error) => {
                console.log(error)
            }
        })
    }
}

function showToast(message="") {
    if (message){
        toast.textContent = message;
    }
    toast.classList.add("show");
    setTimeout(function() {
      toast.classList.remove("show");
    }, 3000);
  }

document.addEventListener('DOMContentLoaded', () => {

    toast = document.getElementById("toast");



    document.querySelectorAll(".file-card")?.forEach((e) => {
        e.addEventListener("mouseenter", () => {
            let fileViewLink = e.querySelector("#fileViewLink").textContent.trim();
            let fileDownloadLink = e.querySelector("#fileDownloadLink").textContent.trim();
            e.querySelector(".card-img").innerHTML = `<div style="z-index:3;">
        <button class='btn btn-primary' onclick="{window.location.href = '${fileViewLink}', showToast('Just a moment, Loading File')}">View</button>
        <button class='btn btn-success' onclick="{window.location.href = '${fileDownloadLink}', showToast()}">Download</button>
        </div>`.trim();
        });
        e.addEventListener("mouseleave", () => {
            e.querySelector(".card-img").innerHTML = `<img src="/static/images/icons/jetcheckFileIcon.svg" alt="" loading="lazy" width="60px"
        style=" filter: saturate(2);user-select:none;">`;
        });
        console.log(e)
    });

});
