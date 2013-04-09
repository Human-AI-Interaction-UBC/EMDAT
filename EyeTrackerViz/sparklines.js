function Sparkline(visID, data, minY, maxY, maxLength){
	this.xOffset = 40;
	this.yOffset = 6;
	// get visualization width and height in pixels (remove "px" string and convert to number)
	this.vis = d3.select("#" + visID);
	this.width = Number(this.vis.style("width").slice(0,-2))-this.xOffset;
	this.height = Number(this.vis.style("height").slice(0,-2))-this.yOffset*2;
	this.maxLength = maxLength;
	this.data = data;
	this.minY = minY;
	this.maxY = maxY;

	// create an SVG element inside the specified div that fully fills the div
	graph = this.vis.append("svg:svg").attr("width", "100%").attr("height", "100%");
	graph.append("svg:line")
		.attr("class", "boundaryLine")
		.attr("x1", 0).attr("y1", this.height+this.yOffset)
		.attr("x2", this.width).attr("y2", this.height+this.yOffset)
		.style("stroke", "black")
		.style("stroke-width", 2)
	graph.append("svg:line")
		.attr("class", "boundaryLine")
		.attr("x1", 0).attr("y1", this.yOffset)
		.attr("x2", this.width).attr("y2", this.yOffset)
		.style("stroke", "black")
		.style("stroke-width", 2)
	graph.append("svg:text")
		.attr("x", this.width)
		.attr("y", this.yOffset*2)
		.text(this.maxY);
	graph.append("svg:text")
		.attr("x", this.width)
		.attr("y", this.height+this.yOffset*2)
		.text(this.minY);

	// create a line-drawing function to draw the SVG sparkline
	this.line = (function (spark, offset) {var scale = spark.getScales();
			return d3.svg.line()
			.x(function(d,i) {return scale[0](i+offset); })
			.y(function(d)	 {return scale[1](spark.maxY-d); });
		});
		
	// offset the x-position of the line by the remaining window size
	var offset = maxLength - data.length;

	// display the line by appending an svg:path element with the data line we created above
	graph.append("svg:path")
			.attr("d", this.line(this, offset)(data))
			.attr("style", "fill: none; stroke: darkcyan; stroke-width: 1.5px;");
	
	return this;
}

Sparkline.prototype.getScales = function() {
	// scale from domain of values to pixel ranges
	var x = d3.scale.linear().domain([0, this.maxLength-1]).range([0, this.width]);
	var y = d3.scale.linear().domain([0, this.maxY-this.minY]).range([this.yOffset, this.height+this.yOffset]);
	return [x, y];
}

Sparkline.prototype.addData = function(newData) {
	// push the new data to the end of the sparkline data
	this.data.push.apply(this.data, newData);
	var offset = 0;
	
	// forget the beginning of the data array once it's length increases past the window size
	if (this.data.length > this.maxLength){
		this.data = this.data.slice(-this.maxLength);
	} else {
		offset = this.maxLength - this.data.length;
	}
	
	// re-draw the line
	this.vis.selectAll("path")
		.attr("d", this.line(this, offset)(this.data));
}