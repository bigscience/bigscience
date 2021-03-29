import * as d3_base from "./web_modules/d3.js"
import * as d3geo from "./web_modules/d3-geo-projection.js";
import * as xnet from "./xnet.js"
import noUiSlider from './web_modules/nouislider.js';
import './web_modules/nouislider/distribute/nouislider.css.proxy.js';
import './customSliders.css.proxy.js';

import * as utils from "./utilities.js"

// import "./mingle/philogl.js"
import "./mingle/kdtree.js"
import "./mingle/graph.js"
import "./mingle/mingle.js"

import d3GeoZoom from './web_modules/d3-geo-zoom.js';

const d3 = Object.assign({}, d3_base, d3geo)

let lut = name =>
	d3
		.text(
			`https://raw.githubusercontent.com/1313e/CMasher/master/cmasher/colormaps/${name}/${name}_8bit.txt`
		)
		.then(d => d3.dsvFormat(" ").parseRows(d, d => d3.rgb(d[0], d[1], d[2])))
		.then(l => t => l[Math.floor(t * (l.length - 1e-7))])


const institutionColors = {
	"research center": "#1f77b4",
	"university": "#ff7f0e",
	"college": "#2ca02c",
	"other": "#d62728",
}

export class HeliosMap {
	constructor({
		elementID,
		projectName,
		mapColor = '#B1C3B6',
		projectColor = CC006B,
		projection = d3.geoRobinson()//geoCylindricalEqualArea()
			//  .parallel(37.5)
			// .center([0,40])
			.rotate([-10, 0]),
		// nodes = {},
		// edges = [],
	}) {
		this.projectName = projectName;
		this.mapColor = mapColor;
		this.projectColor = projectColor;
		this.element = document.getElementById(elementID);
		this.element.innerHTML = '';
		this.element.classList.add('scaffold');
		// this.mapElement = document.createElementNS("http://www.w3.org/2000/svg", "svg")
		// this.mapElement.setAttributeNS("http://www.w3.org/2000/xmlns/", "xmlns:xlink", "http://www.w3.org/1999/xlink");
		// this.mapElement.classList.add("mapView")
		// this.element.appendChild(this.mapElement);

		// this.mapElement = document.createElement("canvas");
		// this.element.appendChild(this.mapElement);
		// this.mapElement.classList.add("mapView")
		// this.mapContext = this.mapElement.getContext('2d');
		this.plotView = document.createElement("div");
		this.plotView.classList.add("plotView")
		this.element.appendChild(this.plotView);
		this.canvasElement = document.createElement("canvas");
		this.plotView.appendChild(this.canvasElement);
		this.canvasElement.classList.add("edgesView")
		this.context = this.canvasElement.getContext('2d');
		this.nodesElement = document.createElementNS("http://www.w3.org/2000/svg", "svg")
		this.nodesElement.setAttributeNS("http://www.w3.org/2000/xmlns/", "xmlns:xlink", "http://www.w3.org/1999/xlink");
		this.nodesElement.classList.add("nodesView")
		this.plotView.appendChild(this.nodesElement);
		this.mapContext = this.context;

		this.loaderContainer = document.createElement("div");
		this.loaderContainer.classList.add("loaderContainer");
		this.loaderElement = document.createElement("div");
		this.loaderElement.classList.add("loader");
		this.loaderTextElement = document.createElement("div");
		this.loaderTextElement.classList.add("loaderText");
		this.loaderContainer.appendChild(this.loaderElement);
		this.loaderContainer.appendChild(this.loaderTextElement);
		this.element.appendChild(this.loaderContainer);

		this.buttonsPanelElement = document.createElement("div");
		this.buttonsPanelElement.classList.add("buttonsPanel");
		this.inputPanelElement = document.createElement("div");
		this.inputPanelElement.classList.add("inputPanel");
		this.sliderElement = document.createElement("div");
		this.sliderElement.classList.add("timeSlider");

		this.element.appendChild(this.buttonsPanelElement);
		this.buttonsPanelElement.appendChild(this.inputPanelElement);
		this.inputPanelElement.appendChild(this.sliderElement);
		
		// this.legendsElement = document.createElementNS("http://www.w3.org/2000/svg", "svg")
		// this.legendsElement.setAttributeNS("http://www.w3.org/2000/xmlns/", "xmlns:xlink", "http://www.w3.org/1999/xlink");
		// this.legendsElement.classList.add("legendsView")
		this.globalLinks = false;
		this.projection = projection;
		this.geoPath = d3.geoPath().projection(this.projection);
		this.geoPathCanvas = d3.geoPath()
			.projection(this.projection)
			.context(this.mapContext);


		this.transform = new utils.RegularTransform({ x: 0, y: 0, k: 1.0 });
		this.zoom = d3.zoom()
			.scaleExtent([1, 100])
			.on('zoom', (event) => {
				// console.log(event.transform);
				this.transform = new utils.RegularTransform(event.transform);
				this.updateProjection();
				// this.projection;
				// .translate([event.transform.x,event.transform.y])
				// .scale(event.transform.k);
				this.update()
			});

		d3.select(this.canvasElement).call(this.zoom);
		d3.select(this.nodesElement).call(this.zoom);



		// document.getElementById("timeSlider").addEventListener("change", (e)=>{
		// 	console.log("macaco");
		// 	console.log(e.values);
		// });


		this.initialize();
		window.onresize = event => {
			this.willResizeEvent(event);
		};

	}

	async initialize() {
		this.colormap = await lut("amber");
		this.countryData = await d3.json("world-110m.geojson");
		this.progressbar = d3.select(this.loaderContainer);
		this.progresstext = d3.select(this.loaderTextElement);
		this.progresstext.text("Loading data...");

		// this.backgroundMapGroup = d3.select(this.mapElement)
		// 	.append("g")
		// 	.classed("worldMap", true)

		// this.backgroundBorder = this.backgroundMapGroup.selectAll(".sphere")
		// 	.data([{type: "Sphere"}]).enter().append("path")
		// 	.classed("sphere",true)
		// 	.style("fill", this.mapColor)
		// 	.style("stroke", "#dddddd")
		// 	.style("stroke-width", 1);

		// this.backgroundMap = this.backgroundMapGroup.selectAll(".land")
		// 	.data(this.countryData.features)
		// 	.enter()
		// 	.append("path")
		// 	.classed("land",true)
		// 	.attr("fill", "#B1C3B6")
		// 	.attr("stroke", "#dddddd")
		// 	.attr("stroke-width", 1.0);


		this.linksPanel = d3.select(this.nodesElement)
			.append("g")
			.classed("links", true);



		this.nodesPanel = d3.select(this.nodesElement)
			.append("g")
			.classed("nodes", true)


		this.selectedNodes = new Set();
		this.hoverNode = null;
		this.selectedView = d3.select(this.nodesElement).append("g").selectAll(".nodesSelected");

		let network = await xnet.loadXNETFile(`data/institutions_${this.projectName}.xnet`)
		await this.setNetwork(network);
		await this.setupNodesView();
		await this.willResizeEvent(0);
		this.timeSlider.on('update', async (values) => {
			this.minYear = parseInt(values[0]);
			this.maxYear = parseInt(values[1]);
			await this.update();
		});
	}

	async updateProjection() {
		this.width = this.plotView.clientWidth;
		this.height = this.plotView.clientHeight;
		// let rot = this.projection.rotate();
		// this.projection.rotate([rot[0],0]);
		this.projection.fitExtent([[5, 5], [this.width - 5, this.height - 5]], { type: "Sphere" })
		let currentCenter = this.projection.translate();
		this.projection.translate([this.transform.x + this.transform.k * currentCenter[0], this.transform.y + this.transform.k * currentCenter[1]])
		this.projection.scale(this.projection.scale() * this.transform.k)

		// let tx = Math.min(0, Math.max(this.transform.x, width - width * this.transform.k)),
		// let ty = Math.min(0, Math.max(this.transform.y, height - height * this.transform.k));
		// then, update the zoom behavior's internal translation, so that
		// it knows how to properly manipulate it on the next movement
		this.zoom.translateExtent([[5, 5], [this.width - 5, this.height - 5]])
	}

	async willResizeEvent() {
		this.linksPlotData = null;
		let width = this.plotView.clientWidth;
		let height = this.plotView.clientHeight;

		let dpr = window.devicePixelRatio || 1;
		let bsr = this.context.webkitBackingStorePixelRatio ||
			this.context.mozBackingStorePixelRatio ||
			this.context.msBackingStorePixelRatio ||
			this.context.oBackingStorePixelRatio ||
			this.context.backingStorePixelRatio || 1;
		this.contextPixelRatio = dpr / bsr;

		this.canvasElement.style.width = width + "px";
		this.canvasElement.style.height = height + "px";
		// this.svgElement.style.width = width+"px";
		// this.svgElement.style.height = height+"px";
		// this.mapElement.setAttribute('height', "" + height);
		// this.mapElement.setAttribute('width', "" + width);
		this.nodesElement.setAttribute('height', "" + height);
		this.nodesElement.setAttribute('width', "" + width);
		// this.svgElement.width = width+"px";
		// this.svgElement.height = height+"px";
		// this.svgElement.setAttribute('viewBox',`0 0 ${width} ${height}`);
		this.canvasElement.width = this.contextPixelRatio * this.plotView.clientWidth;
		this.canvasElement.height = this.contextPixelRatio * this.plotView.clientHeight;

		this.context.setTransform(1, 0, 0, 1, 0, 0);
		this.context.scale(this.contextPixelRatio, this.contextPixelRatio);

		this.previousGlobalLink = false;


		this.updateProjection();
		this.update()
	}

	async updateBackground() {
		// this.mapContext.clearRect(0,0,this.canvasElement.width,this.canvasElement.height);

		// this.backgroundMap
		// 	.attr("d", this.geoPath);
		// this.backgroundBorder
		// 	.attr("d", this.geoPath)

		this.mapContext.save()
		this.mapContext.strokeStyle = '#dddddd';
		this.mapContext.fillStyle = "#f9fcff";
		this.mapContext.beginPath();
		this.geoPathCanvas({ type: "Sphere" })
		this.mapContext.fill();
		this.mapContext.stroke();

		// this.context.lineWidth = 0.5;
		this.mapContext.strokeStyle = '#dddddd';
		this.mapContext.fillStyle = this.mapColor;
		this.mapContext.beginPath();
		this.geoPathCanvas(this.countryData)
		this.mapContext.fill();
		this.mapContext.stroke();



		// 	.attr("fill", "#B1C3B6")
		// 	.attr("stroke", "#dddddd"){type: "Sphere"}
		// 	.style("fill", "#f9fcff")
		// 	.style("stroke", "#dddddd")
		this.mapContext.restore()
	}

	async update() {
		this.yearsSet = new Set(Array.from({ length: this.maxYear - this.minYear + 1 }, (x, yearIndex) => yearIndex + this.minYear));

		await this.updateNodesPositions();
		await this.updateNodesView();
		await this.updateSelectedNodes(true);

		this.context.clearRect(0, 0, this.canvasElement.width, this.canvasElement.height);
		await this.updateBackground();
		this.renderLinks();
		if (!this.globalLinks || !this.previousGlobalLink) {
			this.progressbar.style("display", null);
			this.progresstext.text("Processing edges...");
			if (this.timer) {
				clearTimeout(this.timer);
			};
			this.timer = setTimeout(async () => {
				this.previousGlobalLink = this.globalLinks;
				await this.setupLinks();
				this.progressbar.style("display", "none");
			}, 1000);
		}
		// requestAnimationFrame(()=>this.renderLinks());
	}

	async setNetwork(network) {

		this.network = network;
		this.nodes = [];
		this.minYear = null;
		this.maxYear = null;
		let sizeMax = 0;
		for (let nodeIndex = 0; nodeIndex < this.network.nodesCount; nodeIndex++) {
			let node = {};
			let networkProperties = this.network.verticesProperties;
			for (const propertyName in networkProperties) {
				if (Object.hasOwnProperty.call(networkProperties, propertyName)) {
					node[propertyName] = networkProperties[propertyName][nodeIndex];
				}
			}

			node.size = Math.pow(node["Strength"], 0.5);
			sizeMax = Math.max(sizeMax, node.size)
			node.id = nodeIndex;

			node.visible = true;
			if (node.Name.startsWith("Unlisted")) {
				node.unlisted = true;
			} else {
				node.unlisted = false;
			}

			if (Object.hasOwnProperty.call(node, "years")) {
				node["years"] = new Set(node["years"].split(" ").map(d => parseInt(d)));
				for (const year of node["years"]) {
					if (this.minYear == null) {
						this.minYear = year;
					} else {
						this.minYear = Math.min(this.minYear, year)
					}
					if (this.maxYear == null) {
						this.maxYear = year;
					} else {
						this.maxYear = Math.max(this.maxYear, year)
					}
				}
			}



			this.nodes.push(node);
		}
		this.nodes.forEach(node => {
			node.size = node.size / sizeMax * 8 + 2;
			if (node.Field in institutionColors) {
				node.color = institutionColors[node.Field];
			} else {
				node.color = institutionColors["other"];
			}
		});


		this.minRangeYear = this.minYear;
		this.maxRangeYear = this.maxYear;

		let intFormater = { to: d => ("" + Math.round(d)) };
		this.timeSlider = noUiSlider.create(this.sliderElement, {
			start: [this.minYear, this.maxYear],
			step: 1,
			behaviour: "tap-drag",
			tooltips: [intFormater, intFormater],
			connect: true,
			range: {
				'min': this.minYear,
				'max': this.maxYear
			},
			pips: {
				mode: 'steps',
				density: 3,
				format: intFormater
			}
		});

		this.yearColor = d3.scaleSequential(this.colormap)
			.domain([this.minRangeYear, this.minRangeYear + (this.maxRangeYear - this.minRangeYear)])


		this.edgesYears = this.network.edgesProperties["years"]
			.map(yearString => new Set(yearString.split(" ").map(d => parseInt(d))));


		// color,
		// title,
		// tickSize = 6,
		// width = 320,
		// height = 44 + tickSize,
		// marginTop = 18,
		// marginRight = 0,
		// marginBottom = 16 + tickSize,
		// marginLeft = 0,
		// ticks = width / 64,
		// tickFormat,
		// tickValues

		this.legendsElement = utils.legend({
			color: d3.scaleSequential([this.minRangeYear, this.maxRangeYear], this.colormap),
			title: "First year of collaboration",
			tickFormat: "d",
		})

		this.legendsCategories = document.createElement("div");
		utils.swatches({
			color:institutionColors,
			columns:null,
			element:this.legendsCategories,
			format: (d=>d.charAt(0).toUpperCase() + d.slice(1)),
			});

		this.legendsPanel = document.createElement("div");
		this.legendsPanel.classList.add("legendsView");

		this.legendsPanel.appendChild(this.legendsCategories);
		this.legendsPanel.appendChild(this.legendsElement);
		this.element.appendChild(this.legendsPanel);
		
	}

	async setupNodesView() {
		let nodeElements = this.nodesPanel.selectAll(".node")
			.data(this.nodes);
		nodeElements.exit().remove()
		let instance = this;
		let newNodeElements = nodeElements
			.enter()
			.append("circle")
			.classed("node", true)
			.attr("r", 0)
			.attr("fill", d => d.color)
			.attr("stroke", d => d3.rgb(d.color).darker(0.85))
			.attr("stroke-width", "1.5px")
			.on("mouseover", function (event, d) {
				instance.hoverNode = d;

				d3.select(this).attr("r", d.size * 1.25)
					.attr("stroke", d3.rgb(d.color).darker(1))
					.attr("stroke-width", 3);
				// hoverText.attr("fill", d.color)
				// displayProperties.forEach((displayProperty,i)=>{
				// // .text(`${displayProperty=="name"?d.name:d[displayProperty]}\n${d[displayProperty]}`);

				// hoverText.append("tspan")
				// .attr("dy","1.2em")
				// .attr("x","0")
				// .style("font-size",i==0?"15px":"13px")
				// 	.text(`${displayProperty=="name"?d.name:d[displayProperty]}`);
				// });
				instance.updateSelectedNodes();
				event.stopPropagation();
			})
			.on("mouseout", function (event, d) {
				d3.select(this).attr("r", d => d.size)
					.attr("stroke", d => d3.rgb(d.color).darker(0.85))
					.attr("stroke-width", 1.5);
				// hoverText.text(null).select("tspan").remove();
				instance.hoverNode = null;
				instance.updateSelectedNodes();
				event.stopPropagation();
			})
			.on("click", function (event, d) {
				if (!event.shiftKey) {
					instance.selectedNodes.clear();
				}
				if (instance.selectedNodes.has(d.id)) {
					console.log("unselecting " + d.id);
					instance.selectedNodes.delete(d.id);
				} else {
					console.log("selecting " + d.id);
					instance.selectedNodes.add(d.id);
				}
				instance.updateSelectedNodes();
				event.stopPropagation();
			})
		d3.select(this.nodesElement).on("click", function (event, d) {
			if (!event.shiftKey) {
				instance.selectedNodes.clear();
				instance.updateSelectedNodes();
			}
		});

		newNodeElements.transition()
			.duration(500)
			.attr("r", d => d.size);

		this.nodesView = newNodeElements
			.merge(nodeElements);
	}

	async updateNodesView() {
		this.nodesView
			.attr("cx", d => d.x)
			.attr("cy", d => d.y)
			.style("display", d => d.visible ? null : "none");
	}

	async updateNodesPositions() {
		this.nodes.forEach(node => {
			let projectedXY = this.projection(node.Position);
			node.x = projectedXY[0];
			node.y = projectedXY[1];
			if (node.x < 0 || node.y < 0 || node.x > this.width || node.y > this.height) {
				node.outOfBounds = true;
			} else {
				node.outOfBounds = false;
			}
			let interSet = utils.setIntersection(this.yearsSet, node["years"])
			if (node.outOfBounds || node.unlisted || interSet.size == 0) {
				node.visible = false;
			} else {
				node.visible = true;
			}
		});
	}

	async updateSelectedNodes(justUpdate = false) {
		let verticalOffset = -10;
		if (!justUpdate) {
			// console.log("updating...");
			// console.log(Array.from(selectedNodes).map(d=>nodeByID[d]))
			let selectedNodesArray = Array.from(this.selectedNodes).map(d => this.nodes[d]).filter(d => d)

			if (this.hoverNode && !this.selectedNodes.has(this.hoverNode.id)) {
				selectedNodesArray.push(this.hoverNode);
			}

			this.selectedView = this.selectedView.data(selectedNodesArray);
			this.selectedView.exit().remove();
			let selectedViewNew = this.selectedView.enter()
				.append("g")
				.classed("nodesSelected", true)
				.classed("nointeraction", true);

			selectedViewNew.append("path").attr("d",
				`M ${-verticalOffset * 1},${verticalOffset + 3} L ${0},${0} L ${+verticalOffset * 1},${verticalOffset + 3} z`)
			let textView = selectedViewNew.append("g")
				.attr("transform", (d, i) => ("translate(" + 0 + "," + verticalOffset + ")"))
				.classed("textbox", true);
			textView.append("text").classed("outline", true);
			textView.append("text").classed("name", true);
			this.selectedView = selectedViewNew.merge(this.selectedView);

		}
		this.selectedView
			.attr("transform", (d, i) => ("translate(" + d.x + "," + d.y + ")"));

		this.selectedView.select(".name")
			.attr("fill", d => d3.rgb(d.color).darker(1))
			.attr("font-size", "15px")
			.attr("text-anchor", "middle")
			.text(d => d.Name);

		this.selectedView.select(".outline")
			.attr("fill", "white")
			.attr("stroke", "white")
			.attr("stroke-width", 3)
			.attr("font-size", "15px")
			.attr("text-anchor", "middle")
			.style('opacity', 0.9)
			.text(d => d.Name);

		this.selectedView.select("path")
			.attr("fill", d => d3.rgb(d.color).darker(1))
			.attr("stroke", "white")
			.style('opacity', 0.9)
			.attr("stroke-width", 1)

	}

	async setupLinks() {
		let minYears = this.network.edgesProperties["year"];
		// let pvalues = this.network.edgesProperties["alpha_ij"].map(d=>d);
		let pvalues = this.network.weights.map(d => 1.0 / d);

		let weights = this.network.weights.map(d => d);

		let edges = this.network.edges;
		let nodes = this.nodes;

		let edgesIndices = [];
		let outgoing = [];

		for (let edgeIndex = 0; edgeIndex < edges.length; edgeIndex++) {
			let edge = edges[edgeIndex];
			let fromIndex = edge[0];
			let toIndex = edge[1];
			if (!this.globalLinks && !nodes[fromIndex].visible && !nodes[toIndex].visible) {
				continue;
			}
			let interSet = utils.setIntersection(this.yearsSet, this.edgesYears[edgeIndex])
			if (interSet.size > 0) {
				if (!this.globalLinks && (!nodes[fromIndex].visible || !nodes[toIndex].visible)) {
					pvalues[edgeIndex] *= 4;
				}
				edgesIndices.push(edgeIndex);
			}
		}

		edgesIndices.sort((firstIndex, secondIndex) => pvalues[firstIndex] - pvalues[secondIndex])
		// edgesIndices.sort((firstIndex,secondIndex)=>-weights[firstIndex]+weights[secondIndex])


		if (edgesIndices.length == 0) {
			return;
		}

		edgesIndices = edgesIndices.slice(0, 1000);

		let edgeBundlingData = [];

		let weightMinMax = d3.extent(edgesIndices.map(i => weights[i]))

		let weightMinMaxGlobal = d3.extent(weights)

		edgesIndices.forEach((index) => {
			let edge = edges[index]
			let fromIndex = edge[0];
			let toIndex = edge[1];
			let fromNode = nodes[fromIndex];
			let toNode = nodes[toIndex];
			let partialOpacity = !this.globalLinks && (!fromNode.visible || !toNode.visible);

			let weight = weights[index];
			let minYear = minYears[index];
			let c = d3.color(this.yearColor(minYear))
			c.opacity = 0.10 * weight / weightMinMaxGlobal[1] + 0.10 * weight / weightMinMax[1] + 0.05;
			// c.opacity=1.0;
			if (partialOpacity) {
				c.opacity = 0.025;
			}
			let entry = {
				id: `${fromIndex}:${toIndex}`,
				name: `${fromIndex}:${toIndex}`,
				data: {
					weight: (2 + weight / weightMinMaxGlobal[1] * 2) * 1.0, //For quadratic use *0.25
					color: c.formatRgb(),
					edgeIndex: index,
					// alpha:0.1,
					coords: [
						nodes[fromIndex].x,
						nodes[fromIndex].y,
						nodes[toIndex].x,
						nodes[toIndex].y,
					]
				}
			}
			edgeBundlingData.push(entry);
		});

		let curviness = 1.0;
		let margin = 0.0;
		// let type = 'BezierSAVE';
		let type = 'QuadraticSAVE';
		let delta = 1.0;
		let angleStrength = 3;
		let neighbors = 15;
		let bundle = new Bundler();

		bundle.options.angleStrength = angleStrength;
		bundle.options.sort = null;

		bundle.setNodes(edgeBundlingData);
		bundle.buildNearestNeighborGraph(neighbors);
		bundle.MINGLE();

		this.bundle = bundle;
		this.linksPlotData = [];
		bundle.graph.each((node) => {
			let theEdges = node.unbundleEdges(delta);
			Bundler.Graph['render' + type](this.linksPlotData, theEdges, {
				margin: margin,
				delta: delta,
				angleStrength: angleStrength,
				curviness: curviness,
				scale: 1.0,
			});
		})

		this.linkTransform = new utils.RegularTransform({
			x: this.transform.x,
			y: this.transform.y,
			k: this.transform.k
		});

		// const performAnimation = () => {
		// 	this.context.clearRect(0,0,this.canvasElement.width,this.canvasElement.height);
		// 	request = requestAnimationFrame(performAnimation);
		// 	updateBundle();
		// }

		// updateBundle();
		this.context.clearRect(0, 0, this.canvasElement.width, this.canvasElement.height);
		this.updateBackground();
		this.renderLinks();

		// console.log(this.linksPlotData);
		// requestAnimationFrame(performAnimation);
		// console.log(context.toString())
		// this.linksView.setAttribute("d", context.toString());

		//...

		// cancelAnimationFrame(request)

	}

	// renderLinks(){
	// 	if(this.linksPlotData){
	// 		this.context.save();
	// 		let totalScale = 1.0;
	// 		this.context.translate(this.transform.x, this.transform.y);
	// 		this.context.scale(this.transform.k, this.transform.k);

	// 		totalScale*=this.transform.k;

	// 		if(this.linkTransform){
	// 			let inverseTransform = this.linkTransform.inverse();
	// 			this.context.translate(inverseTransform.x, inverseTransform.y);
	// 			this.context.scale(inverseTransform.k, inverseTransform.k);
	// 			totalScale*=inverseTransform.k;
	// 		}

	// 		this.linksPlotData.forEach(entry => {
	// 			let edgeIndex = entry.edgeIndex;
	// 			let interSet = utils.setIntersection(this.yearsSet,this.edgesYears[edgeIndex])
	// 			if(interSet.size==0 ){
	// 				return;
	// 			}
	// 			this.context.strokeStyle = entry.color;
	// 			this.context.lineWidth = entry.width/totalScale;
	// 			this.context.beginPath();
	// 			if(entry.hasOwnProperty("moveTo")){
	// 				let start = entry.moveTo;
	// 				this.context.moveTo(start[0], start[1]);
	// 			}
	// 			if(entry.hasOwnProperty("bezierCurveTo1")){
	// 				let [c1,c2,end] = entry.bezierCurveTo1;
	// 				// this.context.bezierCurveTo(c1[0], c1[1], c2[0], c2[1], end[0], end[1]);
	// 			}
	// 			if(entry.hasOwnProperty("lineTo")){
	// 				let start = entry.lineTo;
	// 				this.context.lineTo(start[0], start[1]);
	// 			}
	// 			if(entry.hasOwnProperty("bezierCurveTo2")){
	// 				let [c1,c2,end] = entry.bezierCurveTo2;
	// 				this.context.bezierCurveTo(c1[0], c1[1], c2[0], c2[1], end[0], end[1]);
	// 			}
	// 			this.context.stroke();
	// 			if(entry.shallClose){
	// 				this.context.closePath();
	// 			}
	// 		});
	// 		this.context.restore();
	// 	}

	// // ctx.moveTo(start[0], start[1]);
	// // ctx.bezierCurveTo(c1[0], c1[1], c2[0], c2[1], end[0], end[1]);
	// // ctx.lineTo(start[0], start[1]);
	// // ctx.bezierCurveTo(c1[0], c1[1], c2[0], c2[1], end[0], end[1]);
	// }

	// renderLinksALT(){
	// 	if(this.bundle){
	// 		console.log("Drawing...")
	// 		this.context.save();
	// 		let totalScale = 1.0;
	// 		this.context.translate(this.transform.x, this.transform.y);
	// 		this.context.scale(this.transform.k, this.transform.k);

	// 		totalScale*=this.transform.k;

	// 		if(this.linkTransform){
	// 			let inverseTransform = this.linkTransform.inverse();
	// 			this.context.translate(inverseTransform.x, inverseTransform.y);
	// 			this.context.scale(inverseTransform.k, inverseTransform.k);
	// 			totalScale*=inverseTransform.k;
	// 		}

	// 		let curviness = 1.0;
	// 		let margin = 0.0;
	// 		// let type = 'BezierSAVE';
	// 		let type = 'Bezier';
	// 		let delta = 1.0;
	// 		let angleStrength = 3;
	// 		this.linksPlotData = [];
	// 		this.bundle.graph.each((node)=>{
	// 			let theEdges = node.unbundleEdges(delta);
	// 			Bundler.Graph['render' + type](this.context, theEdges, {
	// 				margin: margin,
	// 				delta: delta,
	// 				angleStrength:angleStrength,
	// 				curviness: curviness,
	// 				scale: 1.0,
	// 			});
	// 		});
	// 		this.context.restore();
	// 	}
	// }
	renderLinks() {
		// this.context.clearRect(0,0,this.canvasElement.width,this.canvasElement.height);

		if (this.linksPlotData) {
			this.context.save();
			let totalScale = 1.0;
			this.context.translate(this.transform.x, this.transform.y);
			this.context.scale(this.transform.k, this.transform.k);

			totalScale *= this.transform.k;

			if (this.linkTransform) {
				let inverseTransform = this.linkTransform.inverse();
				this.context.translate(inverseTransform.x, inverseTransform.y);
				this.context.scale(inverseTransform.k, inverseTransform.k);
				totalScale *= inverseTransform.k;
			}

			this.linksPlotData.forEach(entry => {
				let edgeIndex = entry.edgeIndex;
				let interSet = utils.setIntersection(this.yearsSet, this.edgesYears[edgeIndex])
				if (interSet.size == 0) {
					return;
				}
				this.context.strokeStyle = entry.color;
				this.context.lineWidth = entry.width / totalScale;
				this.context.stroke(entry.path);
			});
			this.context.restore();
		}

		// ctx.moveTo(start[0], start[1]);
		// ctx.bezierCurveTo(c1[0], c1[1], c2[0], c2[1], end[0], end[1]);
		// ctx.lineTo(start[0], start[1]);
		// ctx.bezierCurveTo(c1[0], c1[1], c2[0], c2[1], end[0], end[1]);
	}

	renderLinksSVG() {
		if (this.linkTransform) {
			let inverseTransform = this.linkTransform.inverse();
			this.linksPanel.attr("transform", this.transform + " " + inverseTransform);
		} else {
			this.linksPanel.attr("transform", this.transform)
		}
		let linkElements = this.linksPanel.selectAll(".link")
			.data(this.linksPlotData.filter(entry => {
				let edgeIndex = entry.edgeIndex;
				let interSet = utils.setIntersection(this.yearsSet, this.edgesYears[edgeIndex])
				if (interSet.size == 0) {
					return false;
				} else {
					return true;
				}
			}));

		linkElements.exit().remove();

		let newLinkElements = linkElements
			.enter()
			.append("path")
			.classed("link", true)
			.attr("fill", "none")
			.attr("vector-effect", "non-scaling-stroke")

		// newLinkElements.transition()
		// 	.duration(500)
		// 	.attr("r", d => d.size);

		this.linksView = newLinkElements
			.merge(linkElements);

		this.linksView
			.attr("stroke", d => d.color)
			.attr("stroke-width", d => d.width + "px")
			.attr("d", entry => {
				let context = d3.path();
				if (entry.hasOwnProperty("moveTo")) {
					let start = entry.moveTo;
					context.moveTo(start[0], start[1]);
				}
				if (entry.hasOwnProperty("bezierCurveTo1")) {
					let [c1, c2, end] = entry.bezierCurveTo1;
					context.bezierCurveTo(c1[0], c1[1], c2[0], c2[1], end[0], end[1]);
				}
				if (entry.hasOwnProperty("lineTo")) {
					let start = entry.lineTo;
					context.lineTo(start[0], start[1]);
				}
				if (entry.hasOwnProperty("bezierCurveTo2")) {
					let [c1, c2, end] = entry.bezierCurveTo2;
					context.bezierCurveTo(c1[0], c1[1], c2[0], c2[1], end[0], end[1]);
				}
				// if(entry.shallClose){
				// 	context.closePath();
				// }
				return context;
			});

		// this.context.clearRect(0,0,this.canvasElement.width,this.canvasElement.height);
		// if(this.linksPlotData){
		// 	this.context.clearRect(0,0,this.canvasElement.width,this.canvasElement.height);
		// 	this.linksPlotData.forEach(entry => {
		// 		let edgeIndex = entry.edgeIndex;
		// 		let interSet = setUtils.intersection(this.yearsSet,this.edgesYears[edgeIndex])
		// 		if(interSet.size==0 ){
		// 			return;
		// 		}
		// 		this.context.strokeStyle = entry.color;
		// 		this.context.lineWidth = entry.width;
		// 		this.context.beginPath();
		// 		if(entry.hasOwnProperty("moveTo")){
		// 			let start = entry.moveTo;
		// 			this.context.moveTo(start[0], start[1]);
		// 		}
		// 		if(entry.hasOwnProperty("bezierCurveTo1")){
		// 			let [c1,c2,end] = entry.bezierCurveTo1;
		// 			this.context.bezierCurveTo(c1[0], c1[1], c2[0], c2[1], end[0], end[1]);
		// 		}
		// 		if(entry.hasOwnProperty("lineTo")){
		// 			let start = entry.lineTo;
		// 			this.context.lineTo(start[0], start[1]);
		// 		}
		// 		if(entry.hasOwnProperty("bezierCurveTo2")){
		// 			let [c1,c2,end] = entry.bezierCurveTo2;
		// 			this.context.bezierCurveTo(c1[0], c1[1], c2[0], c2[1], end[0], end[1]);
		// 		}
		// 		this.context.stroke();
		// 		this.context.closePath();
		// 	});
		// }

		// ctx.moveTo(start[0], start[1]);
		// ctx.bezierCurveTo(c1[0], c1[1], c2[0], c2[1], end[0], end[1]);
		// ctx.lineTo(start[0], start[1]);
		// ctx.bezierCurveTo(c1[0], c1[1], c2[0], c2[1], end[0], end[1]);
	}
}

let projectToData = {
	"atlas":{
		name:"ATLAS",
		mapColor:"#BBB2B6",
		color:"#CC006B"
	},
	"babar":{
		name:"BaBar",
		mapColor:"#B1C3B6",
		color:"#008758"
	},
	"ligo":{
		name:"LIGO",
		mapColor:"#B1A58C",
		color:"#903C22"
	},
	"icecube":{
		name:"IceCube",
		mapColor:"#AFB9C9",
		color:"#1E6099"
	},
}

let projectsOrder = ["atlas","babar","ligo","icecube"];

d3.select("#selectionmenu")
	.selectAll("a")
	.data(projectsOrder)
	.enter()
	.append("a")
	.attr("href",d=>"#"+projectToData[d].name)
	.style("--color",d=>projectToData[d].color)
	.append("span")
	.text(d=>projectToData[d].name);


function locationHashChanged() {
	let projectCode = location.hash.substring(1).toLowerCase();
	let projectData = projectToData[projectCode];
	d3.selectAll("#selectionmenu")
	.selectAll("a")
	.classed("selected",d=>d==projectCode);
	
	window.heliosMap = new HeliosMap({
		elementID: "netviz",
		projectName: projectData.name,
		mapColor: projectData.mapColor,
		projectColor: projectData.color
	});
}

window.addEventListener('hashchange', locationHashChanged);

d3.select(".question").on("click", function(event, d) {
	if(d3.select("#helpscreen").style("display")=="none"){
		d3.select("#helpscreen").style("display",null);
	}else{
		d3.select("#helpscreen").style("display","none");
	}
});
d3.select("#helpscreen").on("click", function(event, d) {
	d3.select("#helpscreen").style("display","none");
	
});
if(!window.location.hash){
	window.location.hash = "#ATLAS";
}else{
	locationHashChanged();
}






