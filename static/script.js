function loadContent(contentName) {
    fetch(`/${contentName}`)
        .then(response => response.text())
        .then(data => {
            document.getElementById("content").innerHTML = data;
        })
        .catch(error => {
            console.error('Error:', error);
        });
}
