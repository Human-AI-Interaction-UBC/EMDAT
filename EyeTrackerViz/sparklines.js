function Sparkline(visID, data, minY, maxY, maxLength){
	// get visualization width and height in pixels (remove "px" string and convert to number)
	this.vis = d3.select("#" + visID);
	this.width = Number(this.vis.style("width").slice(0,-2));
	this.height = Number(this.vis.style("height").slice(0,-2));
	this.maxLength = maxLength;
	this.data = data;
	this.minY = minY;
	this.maxY = maxY;

	// create an SVG element inside the specified div that fully fills the div
	graph = this.vis.append("svg:svg").attr("width", "100%").attr("height", "100%");

	// create a line-drawing function to draw the SVG sparkline
	this.line = (function (spark) {var scale = spark.getScales();
			return d3.svg.line()
			.x(function(d,i) {return scale[0](i); })
			.y(function(d)	 {return scale[1](spark.maxY-d); });
		});

	// display the line by appending an svg:path element with the data line we created above
	graph.append("svg:path")
			.attr("d", this.line(this)(this.data))
			.attr("style", "fill: none; stroke: darkcyan; stroke-width: 1.5px;");
	
	return this;
}

Sparkline.prototype.getScales = function() {
	// scale from domain of values to pixel ranges
	var x = d3.scale.linear().domain([0, this.data.length]).range([0, this.width]);
	var y = d3.scale.linear().domain([0, this.maxY-this.minY]).range([0, this.height]);
	return [x, y];
}

Sparkline.prototype.addData = function(newData) {
	// push the new data to the end of the sparkline data
	this.data.push.apply(this.data, newData);
	console.log(this.data);
	
	// forget the beginning of the data array once it's length increases past the window size
	if (this.data.length > this.maxLength){
		this.data = this.data.slice(-this.maxLength);
	}
	
	// re-draw the line
	this.vis.selectAll("path")
		.attr("d", this.line(this)(this.data));
}