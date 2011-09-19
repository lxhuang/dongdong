var curr_category = -1;
var query_limit   = 4;

function isLocationSelected(src) {
	local = readCookie("geo");
	if( local == null ) {
		setFailStatus("Please choose location first");
		return false;
	}
	curr_category = $(src).attr("value");
	return true;
}

function showDeal(src) {
	curr_category = $(src).attr("value");
	local = $("#menu_location").attr("city");
	if( local == "" ) {
		setFailStatus("Please choose location first");
		return;
	}
	//retrieveDeals(local, curr_category, query_limit, 0, NaN, NaN);
}

function showNextPageDeal() {
	if( $("#content_deals_container .content_deal_item").length==0 || curr_category==-1 ) {
		setFailStatus("Please choose category first");
		return;
	}
	local = $("#menu_location").attr("city");
	last_id=$("#content_deals_container .content_deal_item:last").attr("deal_id");
	//retrieveDeals(local, curr_category, query_limit, NaN, NaN, last_id);
}

function showPrevPageDeal() {
	if( curr_category==-1 ) {
		setFailStatus("Please choose category first");
		return;
	}
	local = $("#menu_location").attr("city");
	first_id=$("#content_deals_container .content_deal_item:first").attr("deal_id");
	//retrieveDeals(local, curr_category, query_limit, NaN, first_id, NaN);
}

function showDealDetailsImg(src) {
	url = $(src).attr("src");
	pid = $(src).attr("pid")
	$("#deal_details_img_photo").attr("src", url).attr("pid", pid);
}

function showTheDeal(src) {}

function showThePerson(src) {}

function addDealItem(item) {
	category = item.category;
	created_at = item.created_at;
	disp_addr = item.disp_addr;
	deal_id = item.id;
	max_price = item.max_price;
	min_price = item.min_price;
	fb_uid = item.seller_fbid;
	username = item.seller_name;
	simple_desc = item.simple_desc;
	
	$deal_item = $("<div/>").attr({
		"class": "content_deal_item",
		"deal_id": deal_id,
		"category": category
	});
	
	$deal_item_body = $("<div/>").attr("class", "content_deal_item_body");
	$deal_simple_desc = $("<div/>").attr("class", "deal_simple_desc").html(
		"<a href=\"deal/"+deal_id+"\">"+simple_desc+"</a>"
	);
	
	$deal_price = $("<div/>").attr("class", "deal_price").html(min_price+"$-$"+max_price);
	$deal_item_body.append($deal_simple_desc).append($deal_price);
	
	$sep = $("<div/>").attr("class", "sep");
	
	$deal_item_accessory = $("<div/>").attr("class", "content_deal_item_accessory");
	$deal_seller = $("<span/>").attr("class", "deal_seller").attr("fbid", fb_uid).html(
		"<a href=\"#\" onclick=\"showThePerson(this); return false;\">"+username+"</a>"
	);
	$deal_date = $("<span/>").attr("class", "deal_date").html(created_at);
	$deal_addr = $("<span/>").attr("class", "deal_addr").html(disp_addr);
	$deal_item_accessory.append($deal_seller).append($deal_date).append($deal_addr);
	
	$deal_item.append($deal_item_body).append($sep).append($deal_item_accessory);
	
	$("#content_deals_container").append($deal_item);
}

// support different ways to retrieve deals
// 1. where category=%s, city=%s, and use offset and limit 
// 2. where category=%s, city=%s, and use more-than(mt) and limit
// 3. where category=%s, city=%s, and use less-than(lt) and limit
function retrieveDeals(local, category, limit, offset, morethan, lessthan) {
	query_url = baseURL+"deal?local="+local+"&category="+category+"&limit="+limit;
	if( !isNaN(offset) )
		query_url = query_url+"&offset="+offset;
	else if( !isNaN(morethan) )
		query_url = query_url+"&mt="+morethan;
	else if( !isNaN(lessthan) )
		query_url = query_url+"&lt="+lessthan;
	
	$.get(
		query_url,
		function(dat) {
			if(dat.length==0) {
				setSuccessStatus("No more deals available");
			} else {
				$("#content_deals_container").fadeOut(200,function(){
					$("#content_deals_container").html("");
					for(i=0; i<dat.length; i++) {
						item = dat[i];
						addDealItem(item);
					}
					$("#content_deals_container").fadeIn(400);
				});
			}
		},
		"json"
	);
}

/////////////////////////////////////
// Conversation
/////////////////////////////////////
function showConversationInput(src) {
	var uid = readCookie("fbid");
	if( uid == null ) {
		setFailStatus("Log in Facebook first");
		return;
	}
	$(src).next().next().show();
}
function cancelConversationInput() {
	$("#social_message").val("");
	$("#social_message").parent().hide();
}
function sendConversation() {
	$with_uid = $("span.deal_details_seller").attr("fbid");
	$uid = readCookie("fbid");
	$message = $("#social_message").val();
	$dealid = $("#content_deal_details").attr("dealid");
	$.post(
		baseURL+"conversation",
		"t=0&dealid="+$dealid+"&uid="+$uid+"&to="+$with_uid+"&msg="+$message,
		function(dat) {
			if(dat.err) {
				setFailStatus("Message cannot be delivered. Please retry.");
				$("#social_message").val("");
				return;
			} else {
				setSuccessStatus("Message delivered");
				cancelConversationInput();
				return;
			}
		},
		"json"
	);
}

function clearUnread(uid) {
	$unread = $("div.conversation_contact[uid="+uid+"]").find(".conversation_contact_unread");
	$unread.html("");
}
function constructMessage(msg_id, msg, date, uid, with_uid, deal_id, is_sender, append_to_back) {
	// uid: the login user
	// withuid: the remote user
	// append_to_back: insert at last or front
	$message = $("<div/>").attr({
		"msg_id": msg_id,
		"uid": uid,
		"with_uid": with_uid,
		"deal_id": deal_id
	});
	
	if( is_sender )
		$message.attr("class", "conversation_message selected");
	else
		$message.attr("class", "conversation_message");
	
	$body = $("<div/>").attr("class", "conversation_message_content").html(msg);
	$acce = $("<div/>").attr("class", "conversation_message_control").html(
		"<span class='message_date'>"+date+"</span>" +
		"<span class='message_control'><a href='#' onclick='replyMessage(this); return false;'>Reply</a></span>" +
		"<div class='sep'></div>"
	);
	
	$message.append($body).append($acce);
	if( append_to_back )
		$("#conversation_messages").append($message);
	else
		$("#conversation_messages").prepend($message);
}
function sendReplyMessage(src) {
	$message = $(src).parent().parent();
	$msg_id = $message.attr("msg_id");
	$uid = $message.attr("uid");
	$with_uid = $message.attr("with_uid");
	$dealid = $message.attr("deal_id");
	$textarea = $(src).parent().find("textarea");
	$msg = $textarea.val();
	
	$.post(
		baseURL+"conversation",
		"t=0&dealid="+$dealid+"&uid="+$uid+"&to="+$with_uid+"&msg="+$msg,
		function(dat) {
			if(dat.err) {
				setFailStatus("Message cannot be delivered. Please retry.");
				$textarea.val("");
				return;
			} else {
				setSuccessStatus("Message delivered");
				$textarea.val("");
				$textarea.parent().remove();
				
				constructMessage($msg_id, $msg, "A minute ago", $uid, $with_uid, $dealid, 1, false);
				
				return;
			}
		},
		"json"
	);
	
}
function cancelReplyMessage(src) {
	$(src).parent().find("textarea").val("");
	$(src).parent().remove();
}
function replyMessage(src) {
	$reply = $("<div/>").attr("id", "conversation_reply").html(
		"<textarea style='margin:10px 0 10px 0' cols=40 rows=3></textarea><br/>"+
		"<a href='#' onclick='sendReplyMessage(this);return false;'>Send</a>"+
		"<span class=vertical_sep>|</span>"+
		"<a href='#' onclick='cancelReplyMessage(this);return false;'>Cancel</a>"
	);
	$(src).parent().parent().after($reply);
}
function showMessages(src) {
	$(".conversation_contact").attr("class", "conversation_contact")
	$(src).attr("class", "conversation_contact selected");
	
	var unread_num = $(src).find(".conversation_contact_unread").html();
	if( unread_num == "" )
		unread_num = 0;
	else
		unread_num = parseInt(unread_num.substring(1,unread_num.length-1));
	
	var uid = readCookie("fbid");
	var with_uid = $(src).attr("uid");
	var deal_id = $(src).attr("dealid");
	
	$("#conversation_messages").html("");
	
	$.post(
		baseURL+"conversation",
		"t=2&dealid="+deal_id+"&uid="+uid+"&with_uid="+with_uid,
		function(dat) {
			clearUnread(with_uid);
			for(i=0; i<dat.length; i++) {
				var msg_id = dat[i].msg_id;
				var msg = dat[i].message;
				var date = dat[i].created_at;
				var is_sender = dat[i].is_sender;
				constructMessage(msg_id, msg, date, uid, with_uid, deal_id, is_sender, true);
			}
			
			// make them read
			if( unread_num>0 ) {
				$.post(
					baseURL+"conversation",
					"t=3&dealid="+deal_id+"&uid="+uid+"&with_uid="+with_uid,
					function(dat) {},
					"text"
				);
			}
		},
		"json"
	) 
}

function constructContact(divId, deal_id, username, id, unread) {
	$contact = $("<div onclick='showMessages(this);return false;'/>").attr({
		"uid": id,
		"dealid": deal_id,
		"class": "conversation_contact"
	});
	
	$contact_name = $("<div/>").attr("class", "conversation_contact_name").html(username);
	$contact_unread = $("<div/>").attr("class", "conversation_contact_unread").html("("+unread+")");
	$sep = $("<div/>").attr("class", "sep");
	$contact.append($contact_name).append($contact_unread).append($sep);
	$("#"+divId).append($contact);
}
function showContacts(src) {
	$("#conversation_deals .conversation_deal").attr("class", "conversation_deal")
	$(src).attr("class", "conversation_deal selected");
	
	$deal_id = $(src).attr("id");
	$uid = readCookie("fbid");
	
	$("#conversation_contacts_container").html("");
	$("#conversation_messages").html("");
	
	$.post(
		baseURL+"conversation",
		"t=1&dealid="+$deal_id+"&uid="+$uid,
		function(dat) {
			for(i=0; i<dat.length; i++) {
				var username = dat[i].username;
				var unread = dat[i].unread;
				var id = dat[i].id;
				constructContact("conversation_contacts_container", $deal_id, username, id, unread);
			}
		},
		"json"
	)
}


/////////////////////////////////////
// JQuery initialization
/////////////////////////////////////
$(document).ready(function(){
	var addr = $("#deal_details_location").attr("val");
	geocoder = new google.maps.Geocoder();
	geocoder.geocode(
		{"address": addr},
		function(results, status) {
			if( status != google.maps.GeocoderStatus.OK ) {
				$("#deal_details_location").html("<span style=\"background-color: #F2CBD5\">"+addr+" may not be valid address</span>");
				return;
			}
			var myOptions = {
				zoom: 13,
				center: results[0].geometry.location,
				mapTypeId: google.maps.MapTypeId.ROADMAP
			};
			map = new google.maps.Map(document.getElementById("deal_details_location"), myOptions);
			marker = new google.maps.Marker({
 				position: results[0].geometry.location,
 				map: map,
 				draggable: false
 			});
 			
 			var infowindow = new google.maps.InfoWindow( {content: "<div style='font-size:11px;font-family:Arial;'>"+addr+"</div>"} );
 			google.maps.event.addListener(marker, 'click', function(){infowindow.open(map, marker);});
		}
	);
});