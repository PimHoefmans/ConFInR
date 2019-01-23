function visualizeSequenceLength(data) {
    var sequenceChart = new CanvasJS.Chart("sequenceImage", {
        animationEnabled: true,
        exportEnabled: true,
        zoomEnabled: true,
        theme: "light2",
        title: {
            text: "Distribution of sequence length"
        },
        axisX: {
            title: "Sequence length",
            interval: 1
        },
        axisY: {
            title: "Count"
        },
        legend: {
            cursor: "pointer",
            verticalAlign: "bottom",
            horizontalAlign: "left",
            dockInsidePlotArea: false
        },
        data: [{
            type: "column",
            showInLegend: true,
            name: "Forward reads",
            indexLabel: "{y}",
		    indexLabelFontColor: "#00000",
		    indexLabelPlacement: "inside",
            dataPoints: data["fw_seq_length"]
        },
            {
                type: "column",
                showInLegend: true,
                name: "Reverse reads",
                indexLabel: "{y}",
		        indexLabelFontColor: "#00000",
		        indexLabelPlacement: "inside",
                dataPoints: data["rv_seq_length"]
            }]
    });
    sequenceChart.render()
    enable_buttons();
}