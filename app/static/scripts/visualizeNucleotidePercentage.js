function visualizeNucleotidePercentages(nucleotidePercentagesData, div, title="Clustered Nucleotide Percentage") {
    var nucleotideChart = new CanvasJS.Chart(div, {
        animationEnabled: true,
        zoomEnabled: true,
        exportEnabled: true,
        theme: "light2",
        title: {
            text: title
        },
        axisX: {
            title: "Nucleotide"
        },
        axisY: {
            title: "Percentage",
            maximum: 100
        },
        data: [{
            type: "bubble",
            toolTipContent: "Nucleotide: {label} <br/>Percentage: {bin}% <br/>N. sequences: {z}",
            dataPoints: nucleotidePercentagesData
        }]
    });
    nucleotideChart.render();
    enable_buttons();
}