document.addEventListener('DOMContentLoaded', function() {
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);
    var ctx = document.getElementById('myChart').getContext('2d');
    
    var myChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: chartData.labels,
            datasets: [{
                label: 'CO [%]',
                borderColor: 'rgba(255, 0, 0, 1)',
                borderWidth: 2,
                //ubicInterpolationMode: 'monotone',
                data: chartData.datasets[0].data
            }, {
                label: 'CO2 [%]',
                borderColor: 'rgba(0, 255, 0, 1)',
                borderWidth: 2,
                //ubicInterpolationMode: 'monotone',
                data: chartData.datasets[1].data
            }, {
                label: 'CH4 [%]',
                borderColor: 'rgba(0, 0, 255, 1)',
                borderWidth: 2,
                //ubicInterpolationMode: 'monotone',
                data: chartData.datasets[2].data
            }]
        },
        options : {
            responsive: true,
            plugins: {
                tooltip: {
                    mode: 'index',
                    intersect: false
                },
                // zoom: {
                //     zoom: {
                //         wheel: {
                //             enabled: true, // Fare tekerleği ile zoom yapmayı etkinleştir
                //         },
                //         pinch: {
                //             enabled: true // Dokunmatik cihazlarda iki parmakla zoom yapmayı etkinleştir
                //         },
                //         mode: 'xy', // Hem X hem de Y eksenlerinde zoom yapılmasını sağlar
                //     },
                //     pan: {
                //         enabled: true, // Pan işlevselliğini etkinleştirir
                //         mode: 'xy' // Hem X hem de Y eksenlerinde pan yapılmasını sağlar
                //     },
                //     limits: {
                //         x: {min: 'original', max: 'original', minRange: 1},
                //         y: {min: 'original', max: 'original', minRange: 1}
                //     }
                // }
            },
            interaction: {
              intersect: false,
            },
            scales: {
              x: {
                display: true,
                title: {
                  display: true
                }
              },
              y: {
                display: true,
                title: {
                  display: true,
                  text: '% Gas'
                },
                suggestedMin: -5,
                suggestedMax: 55,
                
                ticks: {
                    stepSize: 5,
                    callback: function(value, index, values) {
                        return value.toFixed(2); // Y aksisinde 2 dijit gösterimi
                    }
                }
              }
            },
            animation: {
                duration: 500, // Animasyon süresi milisaniye olarak. Örneğin, 500 milisaniye.
                easing: 'easeInOutQuart', // Animasyon için easing fonksiyonu. 'easeInOutQuart' pürüzsüz bir geçiş sağlar.
            },
            elements: {
                line: {
                    tension: 0.4 // Çizgiler arasındaki kıvrımlılık. 0 doğrusal bir çizgi anlamına gelir.
                },
                point: {
                    radius: 0 // Nokta yarıçapı. 0, noktaların görünmez olmasını sağlar.
                }
            }
        
        }
    });

    socket.on('chart_sensor_data', function(data) {
        if (myChart.data.labels.length > data.MaxPoint) {
            myChart.data.labels.shift();
            myChart.data.datasets.forEach(dataset => dataset.data.shift());
        }
        myChart.data.labels.push(data.time);
        myChart.data.datasets[0].data.push(data.valueCO);
        myChart.data.datasets[1].data.push(data.valueCO2);
        myChart.data.datasets[2].data.push(data.valueCH4);
        myChart.update();
    });
});
