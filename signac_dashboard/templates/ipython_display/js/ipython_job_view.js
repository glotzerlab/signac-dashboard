window.addEventListener('load', activateJobStatepointDisplay);

function activateJobStatepointDisplay() {
    var nodes = window.document.getElementsByClassName('collapsible');

    for (let i = 0; i < nodes.length; i++) {
        nodes[i].addEventListener('click', function() {
            this.classList.toggle('show');
            var node_content = this.nextElementSibling;
            if (node_content.style.display === 'block') {
                node_content.style.display = 'none';
            } else {
                node_content.style.display = 'block';
            }
        });
    }
}
