document.addEventListener('DOMContentLoaded', function() {
    var myChart = document.getElementById('myChart');

    var trace1 = {
        x: chartData.labels,
        y: chartData.datasets[0].data,
        mode: 'lines',
        name: '<span style="color:red; font-weight: bold; font-size: 18px;" >CO</span>',
        line: {
            color: 'rgba(255, 0, 0, 1)',
            width: 2,
        },
        hovertemplate: 'CO: %%{y:.2f}<extra></extra>',
        mode:"lines"
    };

    var trace2 = {
        x: chartData.labels,
        y: chartData.datasets[1].data,
        mode: 'lines',
        name: '<span style="color:lime; font-weight: bold; font-size: 18px;">CO2</span>',
        line: {
            color: 'rgba(0, 255, 0, 1)',
            width: 2,
        },
        hovertemplate: 'CO2: %%{y:.2f}<extra></extra>',
        mode:"lines"
    };

    var trace3 = {
        x: chartData.labels,
        y: chartData.datasets[2].data,
        mode: 'lines',
        name: '<span style="color:blue; font-weight: bold; font-size: 18px;">CH4</span>',
        line: {
            color: 'rgba(0, 0, 255, 1)',
            width: 2,
        },
        hovertemplate: 'CH4: %%{y:.2f}<extra></extra>',
        mode:"lines"
    };

    var layout = {          
        height:310,
        margin: {
            l: 60,
            r: 60,
            b: 30,
            t: 25,
            pad: 0
        },
        yaxis: {
            title: '% Gas',
            range: [-5, 55],
            tickvals: [-5, 0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55],
            tickformat: '.2f'
            
        },
        legend: {
            orientation:"h",
            x: 0.5, // Yatayda ortalanmış
            y: 1.1, // Üst kısımda
            xanchor: 'center',
            yanchor: 'top',
        },       
        hovermode:"x unified"
    };

    var config = {
        modeBarButtonsToRemove: ['zoomOut2d','zoomIn2d','toggleSpikelines','hoverClosestCartesian','hoverCompareCartesian'],    
        displaylogo : false,
        displayModeBar : true,       
        responsive: false
    };

    var data = [trace1, trace2, trace3];
    Plotly.newPlot(myChart, data, layout, config);   
});
