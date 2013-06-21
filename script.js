// 
var dataFile = "data.json";
var display = "upvote_ratio";

//get anchor
function getAnchor() {
    //console.log("butts");
    return (document.URL.split('#').length > 1) ? document.URL.split('#')[1] : null;
}

var width = 960,
    height = 600;

var rScale,
    upvoteScale,
    nsfwScale,
    participationScale;

function colorGenerator(d)
{
  if(display == "upvote_ratio")
    scaled = upvoteScale(d.upvote_ratio);
  else if(display == "nsfw")
    scaled = nsfwScale(d.nsfw);
  else
    scaled = participationScale(d.average_comments/d.subscribers);
  return "rgb("+Math.round(scaled[0])+","+Math.round(scaled[1])+","+Math.round(scaled[2])+")";
}

var force = d3.layout.force()
    .charge(-120)
    .linkDistance(20)
    .size([width, height]);

var node,
    link;

var svg = d3.select("body").append("svg")
    .attr("width", width)
    .attr("height", height);

d3.json(dataFile, function(graph) {
/*  var k = Math.sqrt(graph.nodes.length / (width * height));

force
    .charge(-10 / k)
    .gravity(10 * k);*/

force.nodes(graph.nodes)
     .links(graph.links)
     .start();

rScale = d3.scale.linear()
    .domain([d3.min(graph.nodes, function(d) {return d.subscribers;})
            ,d3.max(graph.nodes, function(d) {return d.subscribers;})])
    .range([3,20])
    .clamp(true);


upvoteScale = d3.scale.linear()
    .domain([.5 ,1])
    .range([[255,255,255],[255,128,0]]);

nsfwScale = d3.scale.linear()
    .domain([0,1])
    .range([[255,255,255],[255,0,0]]);

participationScale = d3.scale.linear()
    .domain([0,.3])
    .range([[255,255,255],[255,0,128]]);

//building arrows
svg.append("svg:defs").selectAll("marker")
    .data(["arrow"])      // Different link/path types can be defined here
  .enter().append("svg:marker")    // This section adds in the arrows
    .attr("id", String)
    .attr("viewBox", "0 -5 10 10")
    .attr("refX", 15)
    .attr("refY", -1.5)
    .attr("markerWidth", 3)
    .attr("markerHeight", 3)
    .attr("orient", "auto")
  .append("svg:path")
    .attr("d", "M0,-5L10,0L0,5");


  link = svg.append("svg:g").selectAll(".link")
      .data(graph.links)
    .enter().append("line")
      .attr("class", "link")
      .attr("marker-end", "url(#arrow)");

  //building node circles
  node = svg.append("svg:g").selectAll(".node")
      .data(graph.nodes)
    .enter().append("g")
    .attr("class","node")
      .call(force.drag);

  node.append("circle")
      .attr("class", "node")
      .attr("r", function(d) {return rScale(d.subscribers);})
      .attr("stroke-opacity", .3)
      .attr("fill", colorGenerator );


  node.append("title")
      .text(function(d) { return d.name + "\n" + d.subscribers + "\n" +d.upvote_ratio; });

  d3.selectAll(".node").on('mouseover', function() {
        d3.select(this).style("stroke-opacity",1);
        d3.select(this).append("text")
            .attr("x", 8)
          .attr("y", 8)
          .classed("label", true)
          .text(function(d) {return d.name;});
  });
  d3.selectAll(".node").on('mouseout', function() {
        d3.select(this).style("stroke-opacity",.3);
        d3.select(this).select("text").remove();
  });

  force.on("tick", function() {
    link.attr("x1", function(d) { return d.source.x; })
        .attr("y1", function(d) { return d.source.y; })
        .attr("x2", function(d) { return d.target.x; })
        .attr("y2", function(d) { return d.target.y; });

    node.attr("transform", function(d) {
        return "translate(" + d.x + "," + d.y + ")";
      });
  });
});

$( "select" ).on( "change", function() {
        console.log("change");
        display = $( "select" ).val();
        node.selectAll("circle")
            .transition()
            .attr("fill",colorGenerator);
      });