$(document).on('turbolinks:load', function() {
    $('.plotly_viewer').each((index, element) => {
        let endpoint = element.getAttribute("data-endpoint")
        let jobid = element.getAttribute("data-jobid")
        jQuery.get(endpoint, {jobid: jobid}, (data, textStatus, response) => {
            let traces = data["traces"]
            let layout = data["layout"]
            Plotly.newPlot(element, traces, layout)
        })
    });
})
