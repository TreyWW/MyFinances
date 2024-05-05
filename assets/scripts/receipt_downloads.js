/**
 * Downloads a file from the specified URL.
 *
 * @param {string} downloadUrl - The URL of the file to be downloaded.
 */

/*#__NO_RENAME__*/
window.download_file = function Download_file(downloadUrl) {
  var xhr = new XMLHttpRequest();
  xhr.open('GET', downloadUrl, true);
  xhr.onload = function () {
    if (this.status === 200) {
      var response = JSON.parse(this.responseText);

      // Use the download_link and filename from the JSON response
      var downloadLink = response.download_link;
      var filename = response.filename;

      // Trigger the download using a link element
      var a = document.createElement('a');
      a.href = downloadLink;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
    }
  };
  xhr.send();
}
