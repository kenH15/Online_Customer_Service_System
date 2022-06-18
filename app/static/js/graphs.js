var date_arr = []
var data = []
var fn

function make_record(_date, _num) {
    date_arr.push(_date)
    data.push(_num)
}


function draw_chatting_graph() {
    var x_coor = []
    var y_coor = []
    var start_date = document.getElementById('startDate').value
    var end_date = document.getElementById('endDate').value
    start_date = new Date(start_date.replace(/-/g, "/"))
    end_date = new Date(end_date.replace(/-/g, "/"))
    for (index in date_arr) {
        cur_date = date_arr[index]
        cur_date = new Date(cur_date.replace(/-/g, "/"))
        if (cur_date >= start_date && cur_date <= end_date) {
            x_coor.push(date_arr[index])
            y_coor.push(data[index])
        }
    }
    fn('spline', 'graph', x_coor, y_coor, '日期', '数量')
}

function draw_todays_graph() {
    fn('spline', 'graph', date_arr, data, '时间', '数量')
}

function draw_area_graph() {
    var x_coor = []
    var y_coor = []
    var area_coor = []
    var start_date = document.getElementById('startDate').value
    var end_date = document.getElementById('endDate').value
    start_date = new Date(start_date.replace(/-/g, "/"))
    end_date = new Date(end_date.replace(/-/g, "/"))
    for (index in date_arr) {
        cur_date = date_arr[index]
        cur_date = new Date(cur_date.replace(/-/g, "/"))
        if (cur_date >= start_date && cur_date <= end_date) {
            area_coor.push(data[index])
        }
    }

    area_coor.sort()
    for (var i = 0; i < area_coor.length;) {
        var count = 0
        for (var j = i; j < area_coor.length; j++) {
            if (area_coor[i] === area_coor[j]) {
                count++
            }
        }
        x_coor.push(area_coor[i])
        y_coor.push(count)
        i += count
    }


    fn('column', 'graph', x_coor, y_coor, '区域', '数量')
}


function init_graph() {
    var charts = []
    var colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"];
    Highcharts.setOptions({
        colors: colors,
        global: {
            useUTC: false
        }
    })

    function makeChart(graph_type, divId, x_coor, y_coor, x_title, y_title) {
        var chart = new Highcharts.Chart({
            chart: {
                renderTo: divId,
                type: graph_type
            },
            title: {
                text: '',
            },
            xAxis: {
                title: {
                    enabled: false,
                },
                categories: x_coor,
            },
            yAxis: {
                title: {
                    enabled: false,
                }
            },
            plotOptions: {
                series: {
                    marker: {
                        enabled: false
                    },
                    states: {
                        hover: {
                            lineWidth: 5
                        }
                    },
                    shadow: false,
                    events: {
                        mouseOver: function (event) {
                            this.chart.series[this.index].graph.attr({
                                style: 'opacity:1;z-index:99;'
                            })
                        },
                        mouseOut: function (event) {
                            this.chart.series[this.index].graph.attr({
                                style: ''
                            })
                        },
                        legendItemClick: function (event) {
                            var seriesIndex = this.index
                            var series = this.chart.series

                            if (series.length <= 1) {
                                return true
                            }

                            var showAll = false
                            var checkIndex = 0
                            if (checkIndex == seriesIndex) {
                                checkIndex = 1
                            }

                            if (this.visible) {
                                if (!series[checkIndex].visible) {
                                    showAll = true
                                }
                            }

                            for (var i = 0; i < series.length; i++) {
                                if (!showAll && series[i].index != seriesIndex) {
                                    series[i].hide()
                                }
                                else {
                                    series[i].show()
                                }
                            }
                            series = null
                            return false
                        }
                    }
                },
                column: {
                    pointPadding: 0.45,
                    borderWidth: 0
                }
            },
            legend: {

            },
            credits: {
                enabled: false
            },
            tooltip: {
                formatter: function () {
                    return '<span style="color:' + this.series.color + ';font-weight:bold;">' + x_title + '</span><b>' + this.x +
                        '</b><br/><span style="color:' + this.series.color + ';font-weight:bold;">' + y_title + '</span><b>' + this.y + '</b>'
                },
                crosshairs: true
            },
            series: [{
                name: x_title,
                data: y_coor
            }]
        }, function (chartObj) {
            $.each(chartObj.legend.allItems, function (i, item) {
                $.each(item.legendItem, function (j, element) {
                    if (!element) return
                    $(element.element).hover(function () {
                        item.graph.attr({
                            style: 'opacity:1;z-index:99;'
                        })
                    }, function () {
                        item.graph.attr({
                            style: ''
                        })

                    })
                })

            })
        })
        return chart
    }

    fn = makeChart
}