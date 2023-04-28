$("#submit").click(() => {
  // $.post(
  //   "/login",
  //   JSON.stringify({ email: email.val(), password: password.val() }),
  //   function (response) {
  //     alert(response);
  //   },
  //   "json"
  // );
  const submitBtn = document.querySelector("#submit");
  submitBtn.classList.add("disabled");

  const email = $("#email");
  const password = $("#password");

  $.ajax({
    type: "POST",
    url: "",
    data: JSON.stringify({ email: email.val(), password: password.val() }),
    contentType: "application/json",
    dataType: "json",
    success: function (response) {
      if ("error" in response) {
        submitBtn.classList.remove("disabled");  
        $("#error")
          .html(`<div class="alert alert-danger d-flex" data-mdb-color="danger">
            <i class="material-icons-round me-2"> gpp_maybe </i>
            ${response.error}
          </div>`);
      }
      else {
        window.location.href = response.url;
      }
    },
    error: function (xhr, status, error) {
        submitBtn.classList.remove("disabled");  
        $("#error")
        .html(`<div class="alert alert-danger d-flex" data-mdb-color="danger">
            <i class="material-icons-round me-2"> gpp_maybe </i>
            ${error}
          </div>`);
    },
  });
});
