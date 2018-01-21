var draw_pr_rank = (function() {
    // set the dimensions and margins of the graph
    const margin = {
            top: 20,
            right: 20,
            bottom: 30,
            left: 40
        },
        width = 960 - margin.left - margin.right,
        height = 500 - margin.top - margin.bottom;

    // set the ranges
    const x = d3.scaleBand()
        .range([0, width])
        .padding(0.1);
    const y = d3.scaleLinear()
        .range([height, 0]);

    // append the svg object to the body of the page
    // append a 'group' element to 'svg'
    // moves the 'group' element to the top left margin
    const svg = d3.select("body").append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform",
            "translate(" + margin.left + "," + margin.top + ")");
    console.log(data)

    // Scale the range of the data in the domains
    x.domain(data.map(function(d) {
        return d.zh;
    }));
    y.domain([0, d3.max(data, function(d) {
        return d.my;
    })]);
    svg.selectAll(".bar")
        .data(data)
        .enter().append("rect")
        .attr("class", "bar")
        .attr("x", function(d) {
            return x(d.zh);
        })
        .attr("width", x.bandwidth())
        .attr("y", function(d) {
            return y(d.my);
        })
        .attr("height", 0)
        .transition()
        .duration(200)
        .delay(function(d, i) {
            return i * 150;
        })
        .attr("height", function(d) {
            return height - y(d.my);
        });
    // add the x Axis
    svg.append("g")
        .attr("transform", "translate(0," + height + ")")
        .call(d3.axisBottom(x));
    // add the y Axis
    svg.append("g").call(d3.axisLeft(y));

})();

var draw_line_chart = (function() {

    // Set the dimensions of the canvas / graph
    var margin = {
            top: 30,
            right: 20,
            bottom: 30,
            left: 50
        },
        width = 600 - margin.left - margin.right,
        height = 270 - margin.top - margin.bottom;

    // Parse the date / time
    var parseDate = d3.timeParse("%d-%b-%y");

    // Set the ranges
    var xScale = d3.scaleTime().range([0, width]);  
    var yScale = d3.scaleLinear().range([height, 0]);

    // Define the axes
    var xAxis = d3.axisBottom(xScale)
        //.scale(xScale);

    var yAxis = d3.axisLeft(yScale)
        //.scale(yScale);

    // Define the line
    var valueline = d3.line()
        .x(function(d) {
            return xScale(d.date);
        })
        .y(function(d) {
            return yScale(d.close);
        });

    // Adds the svg canvas
    var svg = d3.select("body")
        .append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform",
            "translate(" + margin.left + "," + margin.top + ")");

    // Get the data
    data = [{
        date: "1-May-12",
        close: 58.13
    }, {
        date: "30-Apr-12",
        close: 53.98
    }, {
        date: "27-Apr-12",
        close: 67.00
    }, {
        date: "26-Apr-12",
        close: 89.70
    }, {
        date: "25-Apr-12",
        close: 99.00
    }, {
        date: "24-Apr-12",
        close: 13.028
    }, {
        date: "23-Apr-12",
        close: 16.670
    }, {
        date: "20-Apr-12",
        close: 23.498
    }, {
        date: "19-Apr-12",
        close: 34.544
    }, {
        date: "18-Apr-12",
        close: 44.334
    }, {
        date: "17-Apr-12",
        close: 54.370
    }, {
        date: "16-Apr-12",
        close: 58.013
    }, {
        date: "13-Apr-12",
        close: 60.523
    }, {
        date: "12-Apr-12",
        close: 62.277
    }, {
        date: "11-Apr-12",
        close: 62.620
    }, {
        date: "10-Apr-12",
        close: 62.844
    }, {
        date: "9-Apr-12",
        close: 63.623
    }, {
        date: "5-Apr-12",
        close: 63.368
    }];

    //d3.csv("data.csv", function(error, data) {
    data.forEach(function(d) {
        d.date = parseDate(d.date);
        d.close = +d.close;
    });

    // Scale the range of the data
    xScale.domain(d3.extent(data, function(d) {
        return d.date;
    }));
    yScale.domain([0, d3.max(data, function(d) {
        return d.close;
    })]);

    // Add the valueline path.
    svg.append("path")
        .attr("class", "line")
        .attr("d", valueline(data))
        .style("stroke", "DeepSkyBlue")
        .style("fill", "none");

    // Add the X Axis
    svg.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + height + ")")
        .call(xAxis);

    // Add the Y Axis
    svg.append("g")
        .attr("class", "y axis")
        .call(yAxis);
})();