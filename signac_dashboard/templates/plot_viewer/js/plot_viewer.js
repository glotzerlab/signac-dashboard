function draw_plot(element) {
    data = JSON.parse(element.getAttribute("data-plotlydata"));
    layout = JSON.parse(element.getAttribute("data-plotlylayout"));

    Plotly.newPlot(element, data, layout);
}

$(document).on('turbolinks:load', function() {
    $('.plot_viewer').each((index, element) => {
        draw_plot(element);
    });
})
