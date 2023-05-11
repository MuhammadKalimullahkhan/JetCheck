


<input type="file" id="myFileInput" accept=".docx">
<script src="https://cdnjs.cloudflare.com/ajax/libs/mammoth/1.5.1/mammoth.browser.min.js" integrity="sha512-GXQyA7vCy/AVkekAX69TNpeV1QQu1m+K5Dhx38qyccm27y8nRDjUozszUdmGVnP/j7w9X5VEBmrXGaBZAORXgg==" crossorigin="anonymous" referrerpolicy="no-referrer"></script>
<div id="progressBarContainer">
  <div id="progressBar"></div>
  <div id="progressText">0%</div>
</div>

<div id="aiContent" style="white-space: pre-wrap;"></div>

<script>
  const myFileInput = document.getElementById('myFileInput');
  myFileInput.addEventListener('change', handleFileSelect, false);

  function handleFileSelect(event) {
    const file = event.target.files[0];

    const reader = new FileReader();
    reader.onload = function (event) {
      const arrayBuffer = event.target.result;
      const fileData = new Uint8Array(arrayBuffer);

      const options = {
        arrayBuffer: fileData,
      };

      const progressBarContainer = document.getElementById('progressBarContainer');
      const progressBar = document.getElementById('progressBar');
      const progressText = document.getElementById('progressText');
      const aiContent = document.getElementById('aiContent');

      mammoth.extractRawText(options)
        .then(result => {
          const text = result.value;
          aiContent.textContent = text;
          // Process the extracted text here
          console.log(text);
        })
        .catch(error => {
          console.error('Error reading Word file:', error);
        })
        .finally(() => {
          progressBarContainer.style.display = 'none';
        });

      const updateProgress = (progress) => {
        progressBar.style.width = `${progress}%`;
        progressText.textContent = `${progress}%`;
      };

      const progressCallback = (progress) => {
        updateProgress(Math.round(progress * 100));
      };

      const loadingTask = mammoth.extractRawText(options, { onProgress: progressCallback });

      progressBarContainer.style.display = 'block';
    };

    reader.readAsArrayBuffer(file);
  }
</script>
