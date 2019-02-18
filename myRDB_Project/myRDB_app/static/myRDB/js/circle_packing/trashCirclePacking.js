(function(){
$(document).ready(function(){
    var svg = d3.select("#trashSVG"),
        margin = 20,
        diameter = +svg.attr("width"),
        g = svg.append("g").attr("transform", "translate(" + diameter / 2 + "," + diameter / 2 + ")");

    var color = d3.scaleLinear()
        .domain([-1, 5])
        .range(["hsl(360,100%,100%)", "hsl(0,0%,0%)"])
        .interpolate(d3.interpolateHcl);


    var pack = d3.pack()
        .size([diameter - margin, diameter - margin])
        .padding(2);

    var root = window.trashlistdata;
    console.log(root);

      root = d3.hierarchy(root)
          .sum(function(d) { return d.size; })
          .sort(function(a, b) { return b.value - a.value; });

      var focus = root,
          nodes = pack(root).descendants(),
          view;

      var div = d3.select("body").append("div")
          .attr("class","tooltip")
          .attr("id","trashTooltip")
          .style("opacity",0);

    //TODO: bei erstellen von json color für leaves mitgeben!!!
      var circle = g.selectAll("circle")
        .data(nodes)
        .enter().append("circle")
          .attr("class", function(d) { return d.parent ? d.children ? "node" : "node node--leaf" : "node node--root"; })
          .style("fill", function(d) { return d.children ? color(d.depth) : null; })
          .on("click", function(d) { if(d3.event.defaultPrevented) return;
                console.log("clicked");
              if (focus !== d) zoom(d), d3.event.stopPropagation(); })
          .on("contextmenu",function(d,i){restorefunction(d,i)})
          .on("mouseover",function (d) {
              div.transition()
                  .duration(200)
                  .style("opacity",9)
              div .html(d.data.name+"<br/>")
                  .style("left",(d3.event.pageX)+"px")
                  .style("top",(d3.event.pageY-28)+"px")
          })
          .on("mouseout",function (d) {
              div.transition()
                  .duration(500)
                  .style("opacity",0)
          });

      var leaves = d3.selectAll("circle").filter(function(d){
        return d.children === null;
      });

      //var text = g.selectAll("text")
      //  .data(nodes)
      //  .enter().append("text")
      //    .attr("class", "label")
      //    .style("fill-opacity", function(d) { return d.parent === root ? 1 : 0; })
      //    .style("display", function(d) { return d.parent === root ? "inline" : "none"; })
      //    .text(function(d) { return d.data.name; });

        var node = g.selectAll("circle");
      //var node = g.selectAll("circle,text");
      //.call(d3.drag()
        //                   .on("start",dragstarted)
        //                   .on("drag",dragged)
        //                   .on("end",dragended))

      svg.on("click", function() { zoom(root); });

      zoomTo([root.x, root.y, root.r * 2 + margin]);

      function zoom(d) {
          if (!d.hasOwnProperty('children')) return;
        var focus0 = focus; focus = d;

        var transition = d3.transition()
            .duration(d3.event.altKey ? 7500 : 750)
            .tween("zoom", function(d) {
              var i = d3.interpolateZoom(view, [focus.x, focus.y, focus.r * 2 + margin]);
              return function(t) { zoomTo(i(t)); };
            });
      }

      function zoomTo(v) {
        var k = diameter / v[2]; view = v;
        node.attr("transform", function(d) { return "translate(" + (d.x - v[0]) * k + "," + (d.y - v[1]) * k + ")"; });
        circle.attr("r", function(d) { return d.r * k; });
      }

      //function dragstarted(d){
      //    d3.event.sourceEvent.stopPropagation()
      //    console.log("dragstarted");
      //    d3.select(this).raise().classed("active",true);
      //}
      //function dragged(d) {
      //    console.log("dragged");
      //    d.x += d3.event.dx;
      //    d.y += d3.event.dy;
      //    draw();
      //}
      //function dragended(d) {
      //    console.log("dragended");
      //    d3.select(this).classed("active",false);
      //}
      //function draw() {
      //    var k = diameter / (root.r * 2 + margin);
      //    node.attr("transform", function(d){
      //        return "translate("+(d.x -root.x)*k+","+(d.y-root.y)*k+")";
      //    });
      //    circle.attr("r", function(d){
      //        return d.r*k;
      //    });
      //}
    function updateTrash(updated_data){
          console.log(updated_data);
          root = updated_data;

          svg = d3.select("#trashSVG"),
        margin = 20,
        diameter = +svg.attr("width"),
        g = svg.append("g").attr("transform", "translate(" + diameter / 2 + "," + diameter / 2 + ")");

        color = d3.scaleLinear()
            .domain([-1, 5])
            .range(["hsl(360,100%,100%)", "hsl(0,0%,0%)"])
            .interpolate(d3.interpolateHcl);


        pack = d3.pack()
            .size([diameter - margin, diameter - margin])
            .padding(2);
      root = d3.hierarchy(root)
          .sum(function(d) { return d.size; })
          .sort(function(a, b) { return b.value - a.value; });

      focus = root,
          nodes = pack(root).descendants(),
          view;

      var div = d3.select("body").append("div")
          .attr("class","tooltip")
          .attr("id","trashTooltip")
          .style("opacity",0);

    //TODO: bei erstellen von json color für leaves mitgeben!!!
      circle = g.selectAll("circle")
        .data(nodes)
        .enter().append("circle")
          .attr("class", function(d) { return d.parent ? d.children ? "node" : "node node--leaf" : "node node--root"; })
          .style("fill", function(d) { return d.children ? color(d.depth) : null; })
          .on("click", function(d) { if(d3.event.defaultPrevented) return;
                console.log("clicked");
              if (focus !== d) zoom(d), d3.event.stopPropagation(); })
          .on("contextmenu", function(d,i){restorefunction(d,i)})
          .on("mouseover",function (d) {
              div.transition()
                  .duration(200)
                  .style("opacity",9)
              div .html(d.data.name+"<br/>")
                  .style("left",(d3.event.pageX)+"px")
                  .style("top",(d3.event.pageY-28)+"px")
          })
          .on("mouseout",function (d) {
              div.transition()
                  .duration(500)
                  .style("opacity",0)
          });

      leaves = d3.selectAll("circle").filter(function(d){
        return d.children === null;
      });

      //var text = g.selectAll("text")
      //  .data(nodes)
      //  .enter().append("text")
      //    .attr("class", "label")
      //    .style("fill-opacity", function(d) { return d.parent === root ? 1 : 0; })
      //    .style("display", function(d) { return d.parent === root ? "inline" : "none"; })
      //    .text(function(d) { return d.data.name; });

        node = g.selectAll("circle");
      //var node = g.selectAll("circle,text");
      //.call(d3.drag()
        //                   .on("start",dragstarted)
        //                   .on("drag",dragged)
        //                   .on("end",dragended))

      svg.on("click", function() { zoom(root); });

      zoomTo([root.x, root.y, root.r * 2 + margin]);
    }
    window.updateTrash=function () {
        updateTrash(window.trashlistdata);
    };
    function restorefunction(d,i){
        d3.event.preventDefault();
        var r = confirm("Berechtigung:\n\n"+d.data.name+"\n\nvon Löschliste entfernen\n\nund wiederherstellen?\n\n");
        if (r === true){
            function getCookie(name) {
                var cookieValue = null;
                if (document.cookie && document.cookie !== '') {
                    var cookies = document.cookie.split(';');
                    for (var i = 0; i < cookies.length; i++) {
                        var cookie = jQuery.trim(cookies[i]);
                        // Does this cookie string begin with the name we want?
                        if (cookie.substring(0, name.length + 1) === (name + '=')) {
                            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                            break;
                        }
                    }
                }
                return cookieValue;
            }
            function csrfSafeMethod(method) {
                // these HTTP methods do not require CSRF protection
                return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
            }
            $.ajaxSetup({
                beforeSend: function(xhr, settings) {
                    if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                        xhr.setRequestHeader("X-CSRFToken", getCookie("csrftoken"));
                    }
                }
            });
            var right_type="",right_parent = "",right_grandparent = "";
            if(d.depth===1 && d.hasOwnProperty('children') && d.children[0].hasOwnProperty('children')){
                right_type="af";
            }
            else if((d.depth===2 && d.hasOwnProperty('children') && !d.children[0].hasOwnProperty('children'))||(d.depth===1 && d.hasOwnProperty('children') && !d.children[0].hasOwnProperty('children'))){
                right_type="gf";
                right_parent = d.data.parent;
            }
            else if(d.depth===3||(d.depth===2 && !d.hasOwnProperty('children'))||(d.depth===1 && !d.hasOwnProperty('children'))){
                right_type="tf";
                right_grandparent = d.data.grandparent;
                right_parent = d.data.parent;
            }

            var data = {"X-CSRFToken":getCookie("csrftoken"),"X_METHODOVERRIDE":'PATCH',"user_pk":window.user_pk,"action_type":"restore","right_type":right_type,"right_name":d.data.name,"parent":right_parent,"grandparent":right_grandparent};
            var successful=false;
            $.ajax({type:'POST',
                    data:data,
                    url:'http://127.0.0.1:8000/users/'+window.user_pk+'/',
                    async:false,
                    success: function(res){console.log(res);
                        successful=true},
                    error: function(res){console.log(res);}
                    });
            if(successful===true){
                var trash = window.trashlistdata['children'];
                var rights = window.jsondata['children'];
                var models = window.jsondata_including_delete_list['children'];
                actualize_rights(trash,rights,models,data['right_type'],d);

                d3.select("body").selectAll("#trashTooltip").remove();

                d3.select('#trashSVG').select("g").data(window.trashlistdata).exit().remove();
                updateTrash(window['trashlistdata']);


                d3.select('#circlePackingSVG').select('g').data(window.jsondata).exit().remove();
                window.updateCP();


            }
        }
      }


      function rechain_right_to_rights(right,rights,level){
        var found = false;
        if (level === "af"){
            rights.push(right);
        }
        else if(level === "gf"){
            for (i in rights){
                if (rights[i]['name']===right['parent']) {
                    rights[i]['children'].push(right);
                    found = true;
                    break;
                }
                if (found === true) break;
            }
        }
        else if(level === "tf"){
            for (i in rights){
                var grandparent = rights[i];
                if (grandparent['name']===right['grandparent']){
                    for (j in grandparent['children']){
                        var parent = grandparent["children"][j];
                        if(parent['name']===right['parent']){
                            parent['children'].push(right);
                            found=true;
                            break;
                        }
                        if (found === true) break;
                    }
                }
                if (found === true) break;
            }
        }
      }
      //-------> TODO: an ein level für Rollen denken sobald rollen eingefügt
      function actualize_rights(trash,rights,models,level,d){
        if (d.depth===1){
            for (trash_item in trash) {
                if (trash[trash_item]['name'] === d.data.name) {
                    console.log(trash_item + "," + d.data.name);
                    rechain_right_to_rights(trash[trash_item], rights, level);
                    trash.splice(trash_item, 1);
                    alert("Berechtigung von\n\nLöschliste entfernt\n\nund wiederhergestellt!\n");
                    break;
                }
            }
        }
        else{
            alert("Berechtigung:\n\n"+d.data.name+"\n\nkonnte nicht wiederhergestellt werden!\n\nBerechtigungsbündel können nur\nkomplett wiederhergestellt werden!");
        }
            /*for (trash_item in trash){
                if(trash[trash_item]['name']===d.data.name){
                    console.log(trash_item+","+d.data.name);
                    rechain_right_to_rights(trash[trash_item],rights,level);
                    trash.splice(trash_item,1);
                    alert("Berechtigung von\n\nLöschliste entfernt\n\nund wiederhergestellt!\n");
                    break;
                }
                else{
                    if(trash[trash_item].hasOwnProperty('children')){
                        var trash_lev_2 = trash[trash_item]['children'];
                        for (trash_item_lev_2 in trash_lev_2){
                            if(trash_lev_2[trash_item_lev_2]['name']===d.data.name){
                                console.log(trash_item_lev_2+","+d.data.name);
                                if (d.depth===1) {
                                    rechain_right_to_rights(trash_lev_2[trash_item_lev_2], rights, level);
                                    trash_lev_2.splice(trash_item_lev_2, 1);
                                    alert("Berechtigung von\n\nLöschliste entfernt\n\nund wiederhergestellt!\n");
                                }else {
                                    alert("Berechtigung:\n\n"+d.data.name+"\n\nkonnte nicht wiederhergestellt werden!\n\nBerechtigungsbündel können nur\nkomplett wiederhergestellt werden!");
                                }
                                break;
                            }
                            else{
                                if(trash_lev_2[trash_item_lev_2].hasOwnProperty('children')){
                                    var trash_lev_3 = trash_lev_2[trash_item_lev_2]['children'];
                                    for (trash_item_lev_3 in trash_lev_3){
                                        if(trash_lev_3[trash_item_lev_3]['name']===d.data.name){
                                            console.log(trash_item_lev_3+","+d.data.name);
                                            if(d.depth===1) {
                                                rechain_right_to_rights(trash_lev_3[trash_item_lev_3], rights, level);
                                                trash_lev_3.splice(trash_item_lev_3, 1);
                                                alert("Berechtigung von\n\nLöschliste entfernt\n\nund wiederhergestellt!\n");
                                            }
                                            else{
                                                alert("Berechtigung:\n\n"+d.data.name+"\n\nkonnte nicht wiederhergestellt werden!\n\nBerechtigungsbündel können nur\nkomplett wiederhergestellt werden!");
                                            }
                                            break;
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }*/
      }
    });
}());