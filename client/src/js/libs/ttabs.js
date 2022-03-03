console.log("log parser_base.js");


define(['jquery', "MathJax/MathJax"],
       function($, emathjax){
	   // emathjax = require('MathJax/MathJax');
	   function Tabs(options){
	       /*
		Create editable field tab for each input in ``tabs_ids``
		All ``tabs_ids``, ``tabs_contents``,
		``input_buttons_callbacks`` must have same length.
		
		- ``div_id`` -- id for div, which be used.
		
		- ``subdiv_id_name`` -- name for sub id's, which be used.

		- ``header`` -- header for title.
		
		- ``tabs_ids`` -- list with names for each tab.
		(ex: ["lex", "cs_0"])

		- ``tabs_contents`` -- default content of each field.
		(ex: ["U'=a*(D[U,{x,2}]+ D[U,{y,2}])",
		"abelian(G) \\and subgroup(H, G,) => abelian(H)"])

		- ``buttons_names`` -- list of names for `parse` buttons.

		- ``tabs_buttons_callbacks`` [optional] -- callbacks for
		each buttons for all tabs which accepted
		(tab_id, tab_content_text_div_id) args.

		- ``dialog_edit_callback`` [optional] -- callback for buttons
		which accepted (tab_content_text_div_id) args.
		
		
		// for init:
		self.tabs = new tabs.Tabs({
	           div_id: "scene",
	           subdiv_id_name: "parser",
		   header: "header",
	           tabs_ids: ["parser", "out"],
	           tabs_contents: ["2+2", "4"],
		   buttons_names: ["save"],
	           tabs_buttons_callbacks: [function(tab_id, tab_content_text_div_id)]
	           dialog_edit_callback: function(tab_content_text_div_id)
		});

		// load data from json
		tabs.load({
	           tabs_ids: ["parser", "out"],
	           tabs_contents: ["2+2", "4"],
	        })

		Fields:

		# FOR tabs:

		"tab_content_" -- div, where content for each tab will be stored.

		"tab_content_text_"+subdiv_id_name+"_div_"+ elm -- is name of div
		(inside ``tab_content_``), where text will be rendered.
		# END FOR
		
		# FOR dialog:

		"dialog_"+ subdiv_id_name +"_input" -- is name of div, where dialog
		will be created.
		
		"dialog_editor" -- div inside dialog, where content will be edit by user
		# END FOR
		*/

	       var self = this;
	       // self.net = net;
	       options || (options = {});
	       console.log("options = ", options);
	       self.content_width_percent = "91";
	       self.content_height_px = "300";
	       
	       var div_id = options.div_id;
	       self.set_div_id(div_id);
	       var subdiv_id_name = options.subdiv_id_name || "parser";
	       self.set_subdiv_id_name(subdiv_id_name);
	       
	       self.header = options.header || "header";
	       
	       self.data = {};
	       self.data["tabs_ids"] = options.tabs_ids
		   || ["tab0", "tab1"];
	       self.data["tabs_contents"] = options.tabs_contents
		   || ["tab0 contents", "tab1 contents"];

	       self.buttons_names = options.buttons_names || [subdiv_id_name];

	       // ``parse`` button for each tab. see default for format:
	       self.tabs_buttons_callbacks = options.tabs_buttons_callbacks
		   || [function(tab_id, tab_content_text_id){
			   return(function(event){
			       console.log("clicked at element:");
			       console.log(tab_id);
			       var text = $("#"+tab_content_text_id).text();
			       console.log("default button clicked:");
			       console.log(text);
			       console.log(tab_content_text_id);
			       /*
				// var math = document.getElementById(to_parse_div_id);
				MathJax.Hub.Queue(["Typeset", MathJax.Hub, to_parse_div_id]);
				*/
			   });}];

	       // when clicked at dialogs ``Edit`` button
	       self.dialog_edit_callback = options.dialog_edit_callback
		   || 
		   function(tab_content_text_div_id){
		       return(
			   function(event) {
			       /*
				Update ``self.data`` and ``tab_content_text_div_id``
				from dialog editor,
				apply mathjax to text.
				*/
			       console.log("dialog text");
			       var div_native = tab_content_text_div_id;
			   
			       var text = $("#"+self.get_dialog_editor_id()).text();			       
			       console.log(text);
			       $("#"+tab_content_text_div_id).text(text);
			       // $("#"+self.get_tabs_id()).tabs("refresh");
			   
			       // refresh div:
			       let re = new RegExp("&lt;br&gt;", "g");
			       var tmp_html = $("#"+tab_content_text_div_id).html().replace(re, "<br>");
			       // tmp_html;
			       console.log("tmp_html=", tmp_html);
			       $("#"+tab_content_text_div_id).html(tmp_html);
				       
			       // var tmp_html = $("#"+tab_content_text_div_id).clone();
			       // var tmp_parent = $("#"+tab_content_text_div_id).parent();
			       
			       // console.log("tmp_parent = ", tmp_parent[0].id);
			       
			       // $("#"+tab_content_text_div_id).remove();
			       // console.log("tmp_parent = ", $("#"+tmp_parent[0].id));
			       // console.log("tmp_parent.first() = ", $("#"+tmp_parent[0].id).children()[0]);
			       // $(tmp_html).insertBefore($("#"+tmp_parent[0].id).children()[0]);
			       // tmp_html.insertBefore
			       // console.log("tmp_html = ", $("#"+tab_content_text_div_id));
			       // $("#"+tab_content_text_div_id).empty();
			       // $("#"+tab_content_text_div_id).html(tmp_html);
			       
			       console.log("tab_content_text_div_id native = ", div_native);
			   
			       MathJax.Hub.Queue(["Typeset", MathJax.Hub,
						  div_native]);
		       
			       // save to self.data:			       
			       var tab_id_list = div_native.split("_");
			       var tab_id = parseInt(tab_id_list[tab_id_list.length-1], 10);
			       
			       // convert to "\n":
			       var sents = text.split("<br>");
			       var str_input = sents.join("\n");
			  
			       self.data["tabs_contents"][tab_id] = str_input;
			       // self.data["tabs_contents_changed"][tab_id] = true;
			       console.log("self.data:");
			       console.log(self.data);
			       // console.log("MathJax = ", MathJax);
			       // $("#to_parse_div").text(text);
			       $( this ).dialog( "close" );
			   });};
	       self.items_ids = 4;
	       
	       console.log("from init:");
	       console.log("self.data = ", self.data);
	   };

	   // FOR get/set:
	   Tabs.prototype.set_div_id = function(div_id){
	       
	       /*set up div, where tabs will be placed.
		also set up ``sliced_id`` that will be used
		for all sub elements of current tabs (for
		reassuring uniqueness from other tabs,
		created in the scene).
		self.sliced_id must not content "-" symbol
		(for dynamic tabs adding)*/

	       var self = this;
	       self.div_id = div_id;
	       console.log("self.div_id = ", self.div_id);
	       // self.sliced_id = div_id.slice(1);
	       console.log("self.div_id = ", self.div_id);
	       
	   };

	   Tabs.prototype.set_subdiv_id_name = function(subdiv_id_name){

	       /*name for all sub id's, which be used*/

	       var self = this;
	       self.subdiv_id_name = subdiv_id_name;
	       console.log("self.subdiv_id_name = ", self.subdiv_id_name);
	   };

	   Tabs.prototype.get_tabs_id = function(){

	       /*tabs id (wher $().tabs() will be used),
		created inside ``self.dif_id``*/

	       var self = this;
	       
	       var tabs_id = "tabs_"+self.div_id;
	       console.log("self = ", self);
	       
	       console.log("tabs_id = ", tabs_id);
	       return(tabs_id);
	   };

	   Tabs.prototype.get_tab_id = function(id){

	       /*Id for each <li>. Must content single "-" symbol.*/

	       var self = this;
	       var tab_id = "tab_"+ self.div_id+"_id-" + id;
	       console.log("tab_id = ", tab_id);
	       
	       return(tab_id);
	   };

	   Tabs.prototype.get_tabs_uls_id = function(){
	       var self = this;
	       var tabs_uls_id = "collection_ids_" + self.div_id;
	       return(tabs_uls_id);
	   };

	   Tabs.prototype.get_tabs_content_id = function(){
	       var self = this;
	       var tabs_content_id = "collections_data_" + self.div_id;
	       return(tabs_content_id);
	   };

	   Tabs.prototype.get_tab_content_id = function(id){

	       /*id of content for each tab. Must content single "-" symbol.*/

	       var self = this;
	       var tab_content_id = "tab_content_"+self.div_id+"_idd-"+id;
	       console.log("tab_content_id = ", tab_content_id);
	       return(tab_content_id);
	   };
	   
	   Tabs.prototype.get_tab_content_text_id = function(id){

	       /*is name of div (inside ``tabs_content__`` div),
		where text will be rendered.
		must be ended with "_"+id for `create_dialog_callback`*/

	       var self = this;
	       var content_text_id = ("tab_content_text_"+self.subdiv_id_name
				      +  '_'+self.div_id+'_'+"_div_"+id);
	       console.log("tab_content_text_id = ", content_text_id);
	       return(content_text_id);
	   };

	   Tabs.prototype.get_tab_content_button_id = function(tab_id, inner_id){

	       /* div of each button inside ``tab_content_text_`` div
		- ``inner_id`` -- id of each button inside tab.
		*/

	       var self = this;
	       var button_id = "button_"+self.subdiv_id_name+ "_"+tab_id+"_"+inner_id;
	       console.log("button_id = ", button_id);
	       return(button_id);
	   };
        
	   // FOR dialog:
	   Tabs.prototype.get_dialog_id = function(){
	       /*
		is name of div, where dialog
		will be created.
		*/
	       var self = this;
	       var dialog_id = 'dialog_'+ self.subdiv_id_name +'_input_'+self.div_id;
	       console.log("dialog_id = ", dialog_id);
	       return(dialog_id);
	   };

	   Tabs.prototype.get_dialog_editor_id = function(elm){

	       /*div inside dialog, where content will be edit by user*/
	       
	       var self = this;
	       var editor_id = "dialog_editor_"+self.div_id;
	       console.log("dialog_editor_id = ", editor_id);
	       return(editor_id);
	   };
	   // END FOR
	   // END FOR


	   Tabs.prototype.load = function(json_data){
	       /*
		Load tabs from json.

		-- ``json_data`` - must contain "tabs_ids",
		"tabs_contents".
		*/
	       var self = this;
	       self.remove();
	       console.log("from load:");
	       console.log("self.data = ", self.data);
	       self.data = {
		   tabs_ids: json_data["tabs_ids"],
		   tabs_contents: json_data["tabs_contents"]
	       };
	       
	       /*
	       var buttons_callbacks = $.map(json_data["tabs_ids"],
					     self.tabs_buttons_callback);
	       console.log("buttons_callbacks = ", buttons_callbacks);
		*/
	       // END FOR

	       self.create_tabs();
	   };

	   Tabs.prototype.save = function(){
	       
	       /*Save data to server?*/

	       var self = this;
	       /*
	       $.each(self.data["tabs_ids"],
		      function(id, elm){
			  var text = "";
			  // if "empty" sting was added in add_tab
			  // (maybe dont need that)
			  if (self.data["tabs_contents"][id] !== "empty")
			      text = $("#"+self.get_tab_content_text_id(id)).text();
			  else
			      text = "empty";
			  // console.log("text = ", text);
			  self.data["tabs_contents"][id] = text;
		      });
		*/
	       console.log("saved data:");
	       console.log(self.data);
	       return(this.data);
	   };

	   
	   Tabs.prototype.remove = function(){
	       var self = this;
	       $("#"+ self.div_id).empty();
	       // $("#"+self.get_buttons_id()).remove();
	       // $("#"+self.get_dialog_id()).remove();
	       // $("#"+self.get_tabs_id()).remove();
	   };

	   Tabs.prototype.create_tabs = function(){

	       /*Create tabs, apply dialog and callbacks*/

	       var self = this;
	       console.log("from create_tabs");
	       console.log("self.data = ", self.data);
	       
	       var board_str = self.draw_tabs();
	       board_str += self.draw_dialog();
	       $("#"+self.div_id).html(board_str);
	       // $(self.div_id).addClass("above_net_left");

	       self.draw_tabs_content();

	       $("#"+self.get_tabs_id()).tabs();
	       // $(div_id).draggable({handle: "p.ui-widget-header"});
	       /// $("#to_parse_div").css("width", "350");
	       /// $("#to_parse_div").css("height", "50");
	       
	       self.apply_editor_and_buttons();
	   };

	   Tabs.prototype.draw_dialog = function(){
	       var self = this;
	       return(('<div id="'+self.get_dialog_id()+'">'
		       + '<div id="'+self.get_dialog_editor_id()+'" contenteditable="true"'
		       + ' class=""></div>'
		       +'</div>'));
	   };
	   
	   Tabs.prototype.apply_editor_and_buttons = function(){

	       /*for add dialog and ``parse`` button callbacks
		self.tabs_buttons_callback used.*/

	       var self = this;
	       $.each(self.data["tabs_contents"],
		      function(tab_id, elm){
			  // for editor:
			  var edit_id = self.get_tab_content_text_id(tab_id);
			  // var edit_id = "#to_"+subdiv_id_name+ '_'+sliced_id+'_'+"_div_"+id;
			  $("#"+edit_id).on("click",
					self.create_dialog_callback(edit_id));
			  // for parse button:
			  // add buttons to each tab:
			  $.each(self.buttons_names,
				 function(inner_id, elm){
				     var but_id = "#" + self.get_tab_content_button_id(tab_id, inner_id);
				     $(but_id).on("click",
						  self.tabs_buttons_callbacks[inner_id](tab_id, edit_id));
		
				 });
		      });
	   };

	   // FOR dialog:
	   Tabs.prototype.create_dialog_callback = function(tab_content_text_div_id){

	       /* for input editor
		(with contenteditable="true" attribute)
		with use of jquery.dialog.
		self.dialog_edit_callback used for ``Edit`` button.
		*/

	       var self = this;

	       return(function(event){
		   // create dialog
		   console.log("create dialog");
		   console.log("dialog created");
		   var subdiv_id = "#"+self.get_dialog_id();
		   // var subdiv_id = "#edit_" + subdiv_name + "_input";
		   $(subdiv_id).dialog({
		       resizable: true,
		       height: "auto",
		       width: 400,
		       modal: true,
		       open: function(event, ui){
			   console.log("dialog opend");
			   $(subdiv_id).toggleClass("ui-widget ui-corner-all ui-widget-shadow style_editor_dinamic");
			   $("#"+self.get_dialog_editor_id()).toggleClass("ui-widget-content ui-corner-all");

			   var div_native = tab_content_text_div_id;
		   
			   // text from  self.data:			       
			   var tab_id_list = div_native.split("_");
			   var tab_id = parseInt(tab_id_list[tab_id_list.length-1], 10);
			   var text = self.data["tabs_contents"][tab_id];
			   
			   // convert to "<br>":
			   var sents = text.split("\n");
			   var str_input = sents.join("<br>");
			   
			   console.log("used text = ", str_input);
			   
			   $("#"+self.get_dialog_editor_id()).text(str_input);
			   
			   // TODO: bug either of these is not work:
			   // first click after load alwais empty sting in editor
			   // refresh div:
			   /*
			   let re = new RegExp("&lt;br&gt;", "g");
			   console.log("tmp_html0=", $("#"+tab_content_text_div_id).html());
			   var tmp_html = $("#"+tab_content_text_div_id).html().replace(re, "<br>");
			   // tmp_html;
			   console.log("tmp_html=", tmp_html);
			   $("#"+tab_content_text_div_id).html(tmp_html);
			    */
			   // refresh div:
			   // var tmp_html = $("#"+self.get_dialog_editor_id()).html();
			   // console.log("tmp_html = ", tmp_html);
			   
			   // $("#"+self.get_dialog_editor_id()).html(tmp_html);
		   
			   
		       },
		       close: function(event, ui){
			   console.log("dialog closed");
			   $(subdiv_id).toggleClass("ui-widget ui-corner-all ui-widget-shadow style_editor_dinamic");
			   $("#"+self.get_dialog_editor_id()).toggleClass("ui-widget-content ui-corner-all");
			   
		       },
		       buttons: {
			   "Edit": self.dialog_edit_callback(tab_content_text_div_id),
			   Cancel: function() {
			       $( this ).dialog( "close" );
			   }
		       }
		   });
		   // $("#tab_content_text_div_id").toggleClass("ui-widget ui-corner-all ui-widget-shadow");
		   // $("#epi_editor").toggleClass("ui-widget-content ui-corner-all");
		   // get data from self.data

		   // FOR send text to dialog:
		   /*
		   var div_native = tab_content_text_div_id;
		   
		   // text from  self.data:			       
		   var tab_id_list = div_native.split("_");
		   var tab_id = parseInt(tab_id_list[tab_id_list.length-1], 10);
		   var text = self.data["tabs_contents"][tab_id];

		   // convert to "<br>":
		   var sents = text.split("\n");
		   var str_input = sents.join("<br>");
			  
		   console.log("used text = ", str_input);
		   
		   $("#"+self.get_dialog_editor_id()).text(str_input);
		    */
		    
		   // $("#"+self.get_dialog_editor_id()).text($(tab_content_text_div_id).text());
		   console.log("dialog created");
		   // END FOR
	       });
	   };
	   // END FOR
	   
	   Tabs.prototype.draw_tabs_content = function(){

	       /*Draw default content for each tab accordingly,
		adjust area size, apply mathjax.*/

	       var self = this;
	       self.original_content = [];
	       console.log("from draw_tabs_content:");
	       console.log(self.data["tabs_contents"]);
	       $.each(self.data["tabs_contents"],
		      function(id, elm){
			  
			  console.log("tab_content:");
			  console.log(elm);

			  // adding content source to storage:
			  self.original_content.push(elm);

			  
			  var sents = elm.split("\n");
			  var sents_count = sents.length;
			  console.log("sents_count = ", sents_count);

			  var sents_length = $.map(sents, function(elm, id){
			      return(elm.length);});

			  var max_length = sents_length.reduce(function(acc, x){return(acc>x?acc:x);}, 0);
			  console.log("max_length = ", max_length);

			  var str_input = self.draw_tab_content(id, sents.join("<br>"));
			  $("#"+self.get_tab_content_id(id)).html(str_input);

			  var content_width = parseInt(self.content_width_percent, 10)+10;
			  var content_width_text = self.content_width_percent;
			  $("#"+self.get_tab_content_id(id))
			      .css("width", content_width + "%");
			  $("#"+self.get_tab_content_text_id(id))
			      .css("width", content_width_text + "%");    
			
			  var content_height = parseInt(self.content_height_px, 10)+100;
			  var content_height_text = self.content_height_px;
			  
			  $("#"+self.get_tab_content_id(id))
			      .css("height", content_height + "px");
			  // this must be less then previus.
			  // Otherwise will be bug with parser button.
			  $("#"+self.get_tab_content_text_id(id))
			      .css("height", content_height_text + "px");
			
			  $("#"+self.get_tab_content_text_id(id)).css("overflow", "scroll");
			  /*Adaptive area
			  if(max_length > 0){
			      var width_coeff = 7;
			      $("#"+self.get_tab_content_id(id)).css("width", width_coeff*max_length + "px");
			      $("#"+self.get_tab_content_text_id(id)).css("width", width_coeff*max_length + "px");    
			  }
			  if(sents_count > 0){
			      if (sents_count > 10){
				  $("#"+self.get_tab_content_id(id)).css("height", 150 + "px");
				  $("#"+self.get_tab_content_text_id(id)).css("height", 150 + "px");
				  // $("#"+self.get_tab_content_id(id)).css("overflow", "scroll");
				  // $("#"+self.get_tab_content_id(id)).css("owerflow-y", "scroll");
				  // $("#"+self.get_tab_content_id(id)).css("owerflowY", "scroll");
 				  
				  $("#"+self.get_tab_content_text_id(id)).css("overflow", "scroll");
				  $("#"+self.get_tab_content_text_id(id)).css("owerflow-y", "scroll");
				  $("#"+self.get_tab_content_text_id(id)).css("owerflowY", "scroll");
				  // owerflow-x: auto;

			      }
			      else{
				  var height_coeff = 53;
				  var height_t = 7;
				  var height_transform = height_coeff*sents_count+height_t;
				  
				  $("#"+self.get_tab_content_id(id)).css("height", height_transform + "px");
				  $("#"+self.get_tab_content_text_id(id)).css("height", height_transform + "px");
				  }
			  }
			   */
			  $("#"+self.get_tab_content_text_id(id)).tooltip();
			  MathJax.Hub.Queue(["Typeset", MathJax.Hub,
					     self.get_tab_content_text_id(id)]);
			  // $("#to_"+subdiv_id_name+ '_'+sliced_id+'_'+"_div_"+elm).tooltip();
		      });
	       console.log("self.data = ", self.data);
	       console.log("self.data = ", self.data);
	       console.log("self.data = ", self.data);
	   };


	   Tabs.prototype.draw_tab_content = function(id, elm){

	       /*Draw editor div and parser button for each tab*/
	       console.log("from draw_tab_content: ", id);
	       var self = this;
	       var str_input =
		       ('<div id="'+self.get_tab_content_text_id(id)+'" title="click to edit"'
			+ ' class="style_editor_static " style="height: 300px;">'
			+ elm
			+ '</div>'
			// + '<br>'
		       );

	       // add buttons to each tab:
	       $.each(self.buttons_names,
		      function(inner_id, elm){
			  str_input += ('<input id="'
					+ self.get_tab_content_button_id(id, inner_id)
					+ '" type="button"');	  
			  str_input += (' value="'
					+ self.buttons_names[inner_id]
					+ '"  class="ui-button">');		   
		      });
	       	       	
	       return(str_input);
	   };

	   Tabs.prototype.draw_tabs = function(){
	       var self = this;

	       var board_str = 
		       ('<p >'+self.header+'</p>' // class="ui-widget-header"
			+ '<div id="'+self.get_tabs_id()+'">'
			+ '<ul id="'+self.get_tabs_uls_id()+'">');
	       self.items_ids = 0;
	       $.each(self.data["tabs_ids"],
		      function(id, elm){
			  self.items_ids += 1;
			  var idx = self.get_tab_id(id);
			  board_str += ('<li id="'+idx+'"><a href="#' + self.get_tab_content_id(id)
					+ '">'+elm+'</a></li>');});
	       
	       // one more item for feature:
	       self.items_ids += 1;

	       board_str += '</ul>';
	       board_str += '<div id="'+self.get_tabs_content_id()+'">';
	       $.each(self.data["tabs_ids"],
		      function(id, elm){
			  board_str += ('<div id="'+ self.get_tab_content_id(id)
					+ '" style="height:350px;"></div>'
				       );});
	       board_str += '</div>';
	       board_str += '</div>';
	       return(board_str);
	   };
	       
	   return {
	       Tabs: Tabs 
	       };
       });
