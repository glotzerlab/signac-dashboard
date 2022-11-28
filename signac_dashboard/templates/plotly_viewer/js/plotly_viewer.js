function draw_plot(element) {
    data = JSON.parse(element.getAttribute("data-plotly-data"));
    layout = JSON.parse(element.getAttribute("data-plotly-layout"));

    Plotly.newPlot(element, data, layout);
}

$(document).on('turbolinks:load', function() {
    $('.plotly_viewer').each((index, element) => {
        draw_plot(element);
    });
})
