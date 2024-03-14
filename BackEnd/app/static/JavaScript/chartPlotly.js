document.addEventListener('DOMContentLoaded', function() {
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);
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
        height:330,
        margin: {
            l: 60,
            r: 30,
            b: 30,
            t: 10,
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

    

    socket.on('chart_sensor_data', function(data) {

        if (myChart.data[0].x.length > data.MaxPoint) {
            myChart.data[0].x.shift();  // İlk veri noktasını kaldır
            myChart.data[0].y.shift();
            myChart.data[1].x.shift();  
            myChart.data[1].y.shift();
            myChart.data[2].x.shift();  
            myChart.data[2].y.shift();
        }

        Plotly.extendTraces(myChart, {
             x: [[data.time], [data.time], [data.time]],
             y: [[data.valueCO], [data.valueCO2], [data.valueCH4]]
        }, [0, 1, 2]);          
        
        trace1.name = '<span style="color:red; font-weight: bold; font-size: 18px;">CO</span>: <span style="color:black; font-weight: bold; font-size: 15px;">%'+data.valueCO+'</span>';
        trace2.name = '<span style="color:lime; font-weight: bold; font-size: 18px;">CO2</span>: <span style="color:black; font-weight: bold; font-size: 15px;">%'+data.valueCO2+'</span>';
        trace3.name = '<span style="color:blue; font-weight: bold; font-size: 18px;">CH4</span>: <span style="color:black; font-weight: bold; font-size: 15px;">%'+data.valueCH4+'</span>';
    
       
    });
});
