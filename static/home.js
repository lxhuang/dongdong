var access_token = "";
var facebook_name = "";
var facebook_gender = "";
var facebook_location = "";
var facebook_uid = "";
var facebook_mail = "";
var facebook_thumb = "";

/////////////////////////////////
// facebook
/////////////////////////////////
function loginCallback(response) {
	if( response.session ) {
		access_token = response.session.access_token;
		facebook_uid = readCookie("fbid");
		if( facebook_uid!=null ) {
			$("#menu_user").html(readCookie("name"));
			$("#menu_user").next().show();
			$("#menu_auth").html("Logout").click(function(){logoutFacebook(); return false;});
			return;
		}
		// query user information
		FB.api('/me?access_token='+access_token,function(response){
			setSuccessStatus("Welcome "+response.name);
			
			// by setting cookie, we can get rid of requesting graph api
			// when log out, we should erase the two cookies
			setCookie("fbid", response.id);
			setCookie("name", response.name)
			
			facebook_name = response.name;
			facebook_gender = response.gender;
			facebook_uid = response.id;
			facebook_mail = response.email;
			if( response.location )
				facebook_location = response.location.name;
				
			// query user thumbnail
			FB.api({
				method: "fql.query",
				query: "SELECT pic FROM user WHERE uid="+response.id
			}, function(response){
				facebook_thumb = response[0].pic;
				$.post(	// check whether this user is new or not
					baseURL+"user/register", "t=0&fbid="+facebook_uid,
					function(dat){
						if(dat=="-1") {	// if this is a new user, show registration box
							$("#content_user_register").show();
									
							$("#dongname").val(facebook_name);
							$("#fbname").val(facebook_name);
							$("#email").val(facebook_mail);
							$("#gender").val(facebook_gender);
							
							if( facebook_location!="" ) {
								var facebook_city = jQuery.trim(facebook_location.split(",")[0]);
								var facebook_state = jQuery.trim(facebook_location.split(",")[1]);
								var city_of_state = cities[facebook_state];
								
								$("#state").val(facebook_state);
								$("#city").html("");
								for( i=0; i<city_of_state.length; i++ ) {
									$("#city").append("<option value=\""+city_of_state[i]+"\">"+city_of_state[i]+"</option>");
								}
								$("#city").val(facebook_city);
							}
							
							// save every login user
							saveUserInfo();
						}
					},
					"text"
				);
			});

			// change the login part in menu
			$("#menu_user").html(facebook_name);
			$("#menu_user").next().show();
			$("#menu_auth").html("Logout").click(function(){logoutFacebook(); return false;});
		});
	} else {
		setFailStatus("Facebook login fails");
	}
}
function loginFacebook() {
	FB.login(function(response){
		loginCallback(response);
	}, {perms: 'read_friendlists,read_stream,publish_stream,email'});
}
function logoutFacebook() {
	FB.logout(function(response){
		$("#menu_user").html("");
		$("#menu_user").next().hide();
		$("#menu_auth").html("Log in").click(function(){loginFacebook(); return false;});
		access_token = "";facebook_name = "";facebook_gender = "";
		facebook_location = "";facebook_uid = "";facebook_mail = "";facebook_thumb = "";
		clearContent();
		setSuccessStatus("Log out Facebook");
		eraseCookie("fbid");
		eraseCookie("name");
	});
}

//Ensure: to perform an action, you need to login Facebook first
function authenticateByFB(f) {
	FB.getLoginStatus(function(response){
		if( response.session ) {
			loginCallback(response);
			if(f) {
				f();
			}
		} else {
			FB.login(function(response){
				loginCallback(response);
			}, {perms: 'read_friendlists,read_stream,publish_stream,email'});
		}
	});
}
function checkLoginStatus() {
	FB.getLoginStatus(function(response){
		//if( response.session ) {
		if( response.status === "connected" ) {
			loginCallback(response);
		}
	});
} 

/////////////////////////////////
// utility
/////////////////////////////////
function switchContentTo(divId) {
	if( $("#content .content:visible").length == 0 ) {
		$("#content #"+divId).fadeIn(200);
	} else {
		$("#content .content:visible").fadeOut(400,function(){
			$("#content #"+divId).fadeIn(200);
		});
	}
}
function setCookie(key,value,days) {
	if (days) {
		var date = new Date();
		date.setTime(date.getTime()+(days*24*60*60*1000));
		var expires = "; expires="+date.toGMTString();
	}
	else var expires = "";
	document.cookie = key+"="+value+expires+"; path=/";
}
function eraseCookie(key) {
	setCookie(key,"",-1);
}
function readCookie(key) {
	key = key+"=";
	ca = document.cookie.split(";");
	for( i=0; i<ca.length; i++ ) {
		c = ca[i];
		c = jQuery.trim(c);
		if( c.indexOf(key)==0 )
			return c.substring(key.length,c.length);
	}
	return null;
}

/////////////////////////////////
// interact with publishing deals
/////////////////////////////////
function uploadDone() {
	// callback of uploading photos
	var ret = frames["upload_target"].document.getElementsByTagName("body")[0].innerHTML;
	var dat = eval("("+ret+")");
	if( dat.err ) {
		setFailStatus(dat.err);
		return;
	} else {
		if(dat.pid==-1) {
			setFailStatus("Woops..Something goes wrong..Retry please");
			return;
		}
		setSuccessStatus("Image uploaded!");
			
		$("#deal_img_container img").attr("src", baseURL+"static/upload_img/"+dat.filename).attr("pid", dat.pid);
		$("#content_publish_deal_img_list").append("<img onclick=\"showDealImg(this); return false;\" class=\"deal_img_list_item\" src=\""+baseURL+"static/upload_img/"+dat.filename+"\" width=80px height=80px pid="+dat.pid+">");
		$("#content_publish_deal_img").show();
	}
}
function showDealImg(src) {
	var url = $(src).attr("src");
	var pid = $(src).attr("pid");
	$("#deal_img_container img").attr("src", url).attr("pid", pid);
}
function showBlurredAddr() {
	if( $("#deal_disp_addr_container").is(":visible") ) {
		$("#deal_disp_addr").val("");
		$("#deal_disp_addr_container").hide();
	} else {
		var city = $("#sld_addr_city").html().substring(2);
		$("#deal_disp_addr").val(city);
		$("#deal_disp_addr_container").show();
	}
}
function changeDealDefaultAddr(new_addr) {
	$("#sld_addr_city").html("@ "+new_addr);
}
function publishDeal() {
	if( facebook_uid=="" ) {
		setFailStatus("Please login to Facebook first");
		return;
	}
	
	var category = $("#deal_category").val();
	if( category==-1 ) {
		setFailStatus("Please choose a category");
		return;
	}
	
	var simple_desc = jQuery.trim($("#deal_simple_desc").val());
	if( simple_desc == "" ) {
		setFailStatus("Fill one sentence description");
		return;
	}
	var addr = jQuery.trim($("#deal_sld_addr").val());
	var city = $("#sld_addr_city").html().substring(2);
	var concrete_addr = ( (addr=="") ? "" : (addr+",") ) + city;
	
	var disp_addr = "";
	if( $("#deal_disp_addr_container").is(":visible") ) {
		disp_addr = $("#deal_disp_addr").val();
	} else {
		disp_addr = ( (addr=="") ? "" : (addr+",") ) + city;
	}
	
	var min_price = jQuery.trim($("#deal_min_price").val());
	var max_price = jQuery.trim($("#deal_max_price").val());
	if( min_price == "" || max_price == "" ) {
		setFailStatus("Fill min and max price");
		return;
	}
	if( isNaN(parseFloat(min_price)) || isNaN(parseFloat(max_price)) ) {
		setFailStatus("Min and max price must be numbers");
		return;
	}
	if( parseFloat(max_price)<parseFloat(min_price) ) {
		setFailStatus("Min price cannot be larger than max price");
		return;
	}
	
	var desc  = $("#deal_details").val();
	var phone = jQuery.trim($("#deal_phone").val());
	var email = jQuery.trim($("#deal_email").val());
	
	var imgs = "";
	var img_array = $("#content_publish_deal_img_list img");
	for( i=0; i<img_array.length; i++ ) {
		imgs = imgs + $(img_array[i]).attr("pid");
		if( i<img_array.length-1 )
			imgs = imgs + "|";
	}
	
	$.post(
		baseURL+"publish",
		"fbid="+facebook_uid+"&category="+category+"&simdesc="+simple_desc+"&addr="+concrete_addr+"&dispaddr="+disp_addr+
			"&min="+min_price+"&max="+max_price+"&details="+desc+"&phone="+phone+"&email="+email+"&imgs="+imgs,
		function(dat) {
			if( dat.err ) {
				setFailStatus("Please try to publish your deal again.");
				return;
			} else {
				setSuccessStatus("Your deal has been published");
				clearDealPublish();
				return;
			}
		},
		"json"
	);
}

function clearDealPublish() {
	$("#deal_category").val("-1");
	$("input[name=deal_photo]").val("");
	$("#deal_simple_desc").val("");
	$("#deal_sld_addr").val("");
	$("#deal_disp_addr_container").hide();
	$("#deal_min_price").val("");
	$("#deal_max_price").val("");
	$("#deal_details").val("");
	$("#deal_phone").val("");
	$("#deal_email").val("");
	$("#deal_addr_blur").attr("checked", false);
	$("#content_publish_deal_img_list").html("");
	$("#deal_img_container").html("<img id=\"deal_img_photo\" src=\"\"/>");
	$("#content_publish_deal_img").hide();
}
function showPublishDeal() {
	switchContentTo("content_publish_deal");
}

////////////////////////////////
// search the deals
/////////////////////////////////
function showSearch() {
	switchContentTo("content_search_deal");
}
function searchDeal() {
	$category = $("#search_category").val();
	if( $category == -1 ) {
		setFailStatus("Please choose category first");
		return;
	}
	
	$keywords = $("#search_keyword").val();
	$keywords = jQuery.trim($keywords)
	
	$min_price = jQuery.trim( $("#search_min_price").val() );
	$max_price = jQuery.trim( $("#search_max_price").val() );
	
	new_url = baseURL+"search?category="+$category;
	if( $keywords != "" ) {
		$keywords = $keywords.replace(" ", "+");
		new_url = new_url+"&q="+$keywords;
	}
	if( $min_price != "" )
		new_url = new_url+"&min="+$min_price;
	if( $max_price != "" )
		new_url = new_url+"&max="+$max_price;
	
	window.location = new_url;
}

////////////////////////////////
// Wishlist
/////////////////////////////////
function showWishlist() {
	var uid = readCookie("fbid");
	window.location = baseURL+"wishlist?uid="+uid;
}
function constructNewWish(divId, $content, $wish_id, $created_at) {
	$wishlist_item = $("<div/>").attr("class", "wishlist_item").attr("wish_id", $wish_id);
	$wishlist_item_content = $("<div/>").attr("class", "wishlist_item_content").html(
		"<span class=\"wishlist_item_content_text\">"+$content+"</span>" +
		"<span class=\"wishlist_item_content_date\">"+$created_at+"</span>"
	);
	$wishlist_item_control = $("<div/>").attr("class", "wishlist_item_control").html(
		"<a onclick=\"closeWish(this); return false;\" href=\"#\">Close</a>"
	);
	$sep = $("<div/>").attr("class", "sep");
	$wishlist_item.append($wishlist_item_content).append($wishlist_item_control).append($sep).hide();
	$("#"+divId).prepend($wishlist_item);
	$wishlist_item.fadeIn(200);
}
function postNewWish(src) {
	$input = $(src).parent();
	$category = $input.find("#wishlist_category").val();
	if( $category==-1 ) {
		setFailStatus("Please choose category");
		return;
	}
	
	$content = $input.find("#wishlist_textarea").val();
	$content = jQuery.trim($content);
	if( $content == "" ) {
		setFailStatus("No content");
		return;
	}
	
	$uid = readCookie("fbid");
	$.post(
		baseURL+"wishlist",
		"t=1&uid="+$uid+"&category="+$category+"&content="+$content,
		function(dat) {
			if( dat.id ) {
				wish_id = parseInt(dat.id);
				if( wish_id==-1 ) {
					setFailStatus("Error in publishing your wish. Please retry.");
					return;
				} else {
					$input.find("#wishlist_category").val("-1");
					$input.find("#wishlist_textarea").val("");
					constructNewWish("wishlist_items", $content, dat.id, "A minute ago");
				}
			}
		},
		"json"
	);
}
function closeWish(src) {
	$item = $(src).parent().parent();
	$id = $item.attr("wish_id");
	$.post(
		baseURL+"wishlist",
		"t=2&id="+$id,
		function(dat) {
			if(dat.success) {
				setSuccessStatus("You successfully close your wish");
				$item.remove();
			}
		},
		"json"
	)
}


////////////////////////////////
// clear the content area
/////////////////////////////////
function clearContent() {
	$("#dongname").val(""); $("#street").val(""); $("#phone").val(""); $("#fbname").val(""); $("#email").val("");
	clearDealPublish();
	
	$("#content_user_register").hide();
	$("#content_publish_deal").hide();
	$("#content_search_deal").hide();
}

////////////////////////////////
// Conversation
/////////////////////////////////
function showConversation() {
	var uid = readCookie("fbid");
	window.location = baseURL+"conversation?uid="+uid;
}

////////////////////////////////
// Show deals
/////////////////////////////////
function showDeals() {
	var val = readCookie("geo");
	if( val==null ) {
		setFailStatus("Please choose location first");
		return;
	}
	window.location = baseURL+"deal";
}

/////////////////////////////////
// interact with user info
/////////////////////////////////
function saveUserInfo() {
	var username = jQuery.trim($("#dongname").val());
	if( username == "" ) {
		setFailStatus("Please fill Dong-Dong Name");
		return;
	}
	if( facebook_uid == "" ) {
		setFailStatus("Log in Facebook first");
		return;
	}
	var phone = jQuery.trim($("#phone").val());
	var street = jQuery.trim($("#street").val());
	var fbu = jQuery.trim($("#fbname").val());
	var fbmail = jQuery.trim($("#email").val());
	var fbgender = $("#gender :selected").val();
	var city = $("#city :selected").val();
	var state = $("#state :selected").val();
	
	if( $("#first_prompt").is(":visible") ) {
		$.post(
			baseURL+"user/register",
			"t=1&username="+username+"&phone="+phone+"&addr="+street+"&fbid="+facebook_uid+"&fbu="+facebook_name+
				"&fbthumb="+facebook_thumb+"&fbmail="+facebook_mail+"&fbgender="+fbgender+"&fbloc="+city+","+state,
			function(dat) {
				if(dat!="-1") {
					$("#first_prompt").hide();
					//setSuccessStatus("Saved!");
				}
			},
			"text"
		); 
	} else {
		$.post(
			baseURL+"user/register",
			"t=3&username="+username+"&fbid="+facebook_uid+"&phone="+phone+"&addr="+street+"&fbmail="+fbmail+"&fbloc="+city+","+state,
			function(dat) {
				if(dat!="-1") {
					setSuccessStatus("Saved!");
				}
			},
			"text"
		);
	}
}

function showUserInfo() {
	$.post(
		baseURL+"user/register",
		"t=2&fbid="+facebook_uid,
		function(dat) {
			$("#first_prompt").hide();
			
			switchContentTo("content_user_register");
			
			$("#dongname").val(dat.username);
			$("#phone").val(dat.phone);
			$("#street").val(dat.home_address);
			$("#fbname").val(dat.fb_username);
			$("#email").val(dat.fb_email);
			$("#gender").val(dat.fb_gender);
			var loc = dat.fb_location;
			var city = loc.split(",")[0];
			var state = loc.split(",")[1];
			var city_of_state = cities[state];
			
			$("#state").val(state);
			$("#city").html("");
			for( i=0; i<city_of_state.length; i++ ) {
				$("#city").append("<option value=\""+city_of_state[i]+"\">"+city_of_state[i]+"</option>");
			}
			$("#city").val(city);
		},
		"json"
	);
}

/////////////////////////////////
// status
/////////////////////////////////
function closeStatus() {
	$("#status").hide();
}
function setSuccessStatus(text) {
	$("#status_content").html(text);
	$("#status").attr("class", "status_success").show();
	setTimeout("closeStatus();", 4000);
}
function setFailStatus(text) {
	$("#status_content").html(text);
	$("#status").attr("class", "status_fail").show();
	setTimeout("closeStatus();", 4000);
}

/////////////////////////////////
// geolocation of HTML5
/////////////////////////////////
function getCityName(addr) {
	var tokens = addr.split(",");
	var local = jQuery.trim(tokens[tokens.length-3]);
	return local;
}
function geo_success(p) {
	var lat = p.coords.latitude;
	var lng = p.coords.longitude;
	var geocoder = new google.maps.Geocoder();
	var latLng = new google.maps.LatLng(lat, lng);
	geocoder.geocode({'latLng': latLng}, function(results, status){
		if( status == google.maps.GeocoderStatus.OK ) {
			if( results[0] ) {
				var local_city = getCityName(results[0].formatted_address);
				$("#menu_location").attr("city", local_city.toLowerCase()).html(local_city);
				$("#sld_addr_city").html("@ "+local_city);
				// set cookie
				local_city = local_city.replace(/ /g, "-");
				setCookie("geo",local_city);
			}
		} else {
			$("#menu_location").attr("city", "").html("Choose Location");
			setFailStatus("Sorry, we cannot detect your location");
		}
	});
}
function geo_error() {
	$("#menu_location").attr("city", "").html("Choose Location");
	setFailStatus("Sorry, we cannot detect your location. Please choose location to start browsing.");
}
function changeLocation() {
	$("#menu_change_local").show();
}
function setLocation() {
	var local_city = $("#menu_city :selected").val();
	$("#menu_location").attr("city", local_city.toLowerCase()).html(local_city);
	$("#menu_change_local").hide();
	// set cookie
	local_city = local_city.replace(/ /g, "-");
	setCookie("geo",local_city);
	
	// deal's default address
	// tornado get_cookie will break at space
	changeDealDefaultAddr(local_city.replace(/-/g, " "));
}

/////////////////////////////////
// JQuery initialization
/////////////////////////////////
var deal_upload_button = null;
$(document).ready(function(){
	// for uploading photo (ajax flavor)
	document.getElementById("deal_upload_photo_form").onsubmit=function() {
		setSuccessStatus("Image uploading...");
		document.getElementById("deal_upload_photo_form").target = "upload_target";
		document.getElementById("upload_target").onload = uploadDone;
	}
	
	// state and city in menu
	for(i=0; i<states.length; i++)
		$("#menu_state").append("<option value=\""+states[i]+"\">"+states[i]+"</option>");
	$("#menu_state").change(function(){
		new_state = $("#menu_state :selected").val(); city_of_state = cities[new_state];
		$("#menu_city").html("");
		for( i=0; i<city_of_state.length; i++ )
			$("#menu_city").append("<option value=\""+city_of_state[i]+"\">"+city_of_state[i]+"</option>");
	});
	
	// geolocation
	// first check cookie
	var cookie_local = readCookie("geo");
	if( cookie_local ) {
		cookie_local = cookie_local.replace(/-/g, " ");
		$("#menu_location").attr("city", cookie_local.toLowerCase()).html(cookie_local);
		$("#sld_addr_city").html("@ "+cookie_local);
	} else {
		if( geo_position_js.init() ) {
			geo_position_js.getCurrentPosition(geo_success, geo_error);
		}
	}
	
	// state and city in user info
	for(i=0; i<states.length; i++)
		$("#state").append("<option value=\""+states[i]+"\">"+states[i]+"</option>");
	$("#state").change(function(){
		new_state = $("#state :selected").val(); city_of_state = cities[new_state];
		$("#city").html("");
		for( i=0; i<city_of_state.length; i++ )
			$("#city").append("<option value=\""+city_of_state[i]+"\">"+city_of_state[i]+"</option>");
	});
	
	// check whether this user has already logged in Facebook
	checkLoginStatus();
	
});