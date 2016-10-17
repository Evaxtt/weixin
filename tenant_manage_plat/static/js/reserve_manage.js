function getUrlParam(name)
{
	var reg = new RegExp("(^|&)"+ name +"=([^&]*)(&|$)"); //构造一个含有目标参数的正则表达式对象
	var r = window.location.search.substr(1).match(reg);  //匹配目标参数
	if (r!=null) return unescape(r[2]); return null; //返回参数值
} 

function getDaysInMonth(year,month){
	     var d= new Date();
		return new Date(d.getFullYear(), month,0).getDate();
	}
	
	jQuery.fn.isChildAndSelfOf = function(b){ 
	return (this.closest(b).length > 0); 
	}; 
	
	(function($){
        $(window).load(function(){
            //$(".custom_scrollbar").mCustomScrollbar();
			$(".custom_scrollbar").mCustomScrollbar({
				axis:"x", // horizontal scrollbar
				theme:"3d-dark"
			});
			
			for (var t=8;t<22;t++){	
				var time = ''
				time = t + ":00"
				if (t < 10){
					time = "0" + time
				}
				$(".batch_times").append('<option value=' + t + '>' + time + '</option>')
			}
        });		
		
    })(jQuery);

	$(document).ready(function(){			
		
		 $(".date-pick").datePicker({
				clickInput: true,
				createButton: false,
				startDate:'2000-1-1'
			})
		
		$(".date-pick-batch").datePicker({
				clickInput: true,
				createButton: false,
				startDate:'2000-1-1'
			})
		
		var id = getUrlParam('id')		
		$.ajax({
			url:'/stadium/list/',
				type:'POST',
				data:JSON.stringify({}),
				dataType:'json',
				async:false,
				success:function(result){
				if (result.error == 0){
					//alert(JSON.stringify(result))
					for (var i=0;i<result.stadium_list.length;i++){
						var html = []
						html.push('<li><a stadium_id=' + result.stadium_list[i].id + ' href="?id=' + result.stadium_list[i].id + '">' + result.stadium_list[i].name + '</a></li>')
						$("#stadium_select").append(html.join(''))
						if (!id){
							id = result.stadium_list[0].id
						}
						if (result.stadium_list[i].id == id){
							$("#stadium").html(result.stadium_list[i].name)
						}
					}
					
				}
									
									
			},error:function (XMLHttpRequest, textStatus, errorThrown)  {
				$(".qb_quick_tip").css('background','#e96262')
				showBubble("获取信息失败")
			}
		})
		
		
		
		var sport_id = getUrlParam('sport_id')
		
		
		
		$.ajax({
			url:'/sport_type/list/',
				type:'get',
				data:JSON.stringify({}),
				dataType:'json',
				async:false,
				success:function(result){
				if (result.error == 0){
					//alert(JSON.stringify(result))
					for (var i=0;i<result.sport_types.length;i++){
						var html = []
						html.push('<li><a s_id=' + result.sport_types[i].id + ' href="?id=' + id + '&sport_id=' + result.sport_types[i].id + '">' + result.sport_types[i].name + '</a></li>')
						$("#stadium_type_select").append(html.join(''))
						if (!sport_id){
							sport_id = result.sport_types[0].id
						}
						if (result.sport_types[i].id == sport_id){
							$("#stadium_type").html(result.sport_types[i].name)
						}
					}
					
				}
									
									
			},error:function (XMLHttpRequest, textStatus, errorThrown)  {
				$(".qb_quick_tip").css('background','#e96262')
				showBubble("获取信息失败")
			}
		})
	
		//alert(id)
		
		var date = new Date()
		var year = date.getFullYear() 
		var month = date.getMonth() + 1;
		var maxday = getDaysInMonth(year,month)
		
		
		
		var day = date.getDate();
		var day_day = date.getDay()
		
		
		for (var i=0;i<7;i++){
			var weekday = ''
			switch(day_day){
				case 0:
					weekday = '周日';
					break;
				case 1:
					weekday = '周一';
					break;
				case 2:
					weekday = '周二';
					break;
				case 3:
					weekday = '周三';
					break;
				case 4:
					weekday = '周四';
					break;
				case 5:
					weekday = '周五';
					break;
				case 6:
					weekday = '周六';
					break;
			}
			
			if (day > maxday){
				day = day - maxday
				month = month+1
				if (month > 12){
					month = month - 12
					year = year + 1
				}
			}	
			
			if (String(month).length == 1){
				month = '0' + month
			}
			
			var display_day = '' + day
			if (display_day.length == 1){
				display_day = '0' + day
			}	
			
			if (i==0){
				$(".date-pick").val(year + '-' +month + '-' + display_day)	
				$("#choose_date_hide").val(year + '-' +month + '-' + display_day)	
			}
		
			/*if (i==0){
				var html = '<li style="display:inline-block;padding-right:5px;"><a href="#"><button onclick="select(this)" class="btn-new btn-new-selected" type="button" style="text-shadow:none;background-color:#fff;color:#bdbdbd;border-color:#bdbdbd;width:100px;">' + month + '-' + display_day + ' ' + weekday + '</button></a></li>'
			}else{*/
				var html = '<li day=' + day_day + ' full_date=' + year + '-' + month + '-' + display_day + ' style="display:inline-block;padding-right:5px;"><a href="javascript:void(0)"><button onclick="select(this)" class="btn-new" type="button" style="text-shadow:none;background-color:#fff;color:#bdbdbd;border-color:#bdbdbd;width:80px;height:32px;font-size:12px">' + month + '-' + display_day + ' ' + weekday + '</button></a></li>'
			//}
			$("#date_selecter").append(html)	
			day = day + 1	
			day_day = day_day*1 + 1	
			if (day_day > 6){
				day_day = day_day - 7
			}
			
			
		}
		
		$(".breadcrumb").find('li:first button').addClass('btn-new-selected')	
		
		
		get_reserve_infos()
	})
	
	function get_reserve_infos(){
		$("#loadingCover").show()
		var id = getUrlParam('id')
		if (!id){
			id = $("#stadium_select li:first").find("a").attr("stadium_id")			
		}
		id = id * 1
		var sport_id = getUrlParam('sport_id')
		if (!sport_id){
			sport_id = $("#stadium_type_select li:first").find("a").attr("s_id")
		}
		sport_id = sport_id * 1
		$(".reserve-table-web tbody").html('')
		$(".reserve-table-time-web tbody").html('')
		//$(".batch_times").empty()
		$(".batch_places").html('')
		var html_time = []		
		html_time.push('<tr>')
		for (var t=8;t<24;t++){			
			html_time.push('<td>')
			var time = ''
			time = t + ":00"
			if (t < 10){
				time = "0" + time
			}
			html_time.push(time)
			html_time.push('</td>')	
			
			//$(".batch_times").append('<option value=' + t + '>' + time + '</option>')
		}
		html_time.push('</tr>')	
		//alert(JSON.stringify({'id':id,"sport_id":sport_id,'date':$(".btn-new-selected").closest("li").attr("full_date")}))
		$(".reserve-table-web tbody").append(html_time.join(''))
		$.ajax({
			url:'/stadium/order/',
			type:'POST',
			dataType:'JSON',
			data:JSON.stringify({'id':id,"sport_id":sport_id,'date':$(".btn-new-selected").closest("li").attr("full_date")}),
			async:false,
			success:function(result){
	    		if (result.error == 0){
					//alert(JSON.stringify(result))
	    			//预定添加列
	    			var orders = result.orders
					//alert(JSON.stringify(orders))
	    			//增加场地数
	    			var num = orders.length
					var html = []
					var html_place = []
					html_place.push('<tr><td></td></tr>')
					for (var a=0;a<num;a++){
						html_place.push('<tr>')
						html_place.push('<td>')
						html_place.push(orders[a].name)		
						html_place.push('</td>')
						html_place.push('</tr>')	

						//批量
						$(".batch_places").append('<option value=' + orders[a].id + '>' + orders[a].name + '</option>')
					}
					$(".reserve-table-time-web tbody").append(html_place.join(''))
					
					//获取当前时间
					var current_time = new Date();
					hour = current_time.getHours()
					//alert(hour)
					var current_month = current_time.getMonth()*1 + 1 + ""
					if (current_month.length == 1){
						current_month = "0" + current_month
					}
					current_time_full = current_time.getFullYear() + '-' + current_month + '-'
					if ((current_time.getDate()+"").length == 1){
						current_time_full += '0' + current_time.getDate()
					}else{
						current_time_full += current_time.getDate()
					}
					
					for (var i=0;i<num;i++){
						html.push('<tr>')
						
						
						var order_hours_tmp = []
						for (var t=0;t<orders[i].order_hours.length;t++){
							//alert(orders[i].order_hours[t].hour)
							order_hours_tmp.push(orders[i].order_hours[t].hour) 
						}
						
						//business_time
						var business_time_tmp = []
						for (var b=0;b<orders[i].business_time.length;b++){
							for (var t=parseInt(orders[i].business_time[b].from_hour);t<parseInt(orders[i].business_time[b].to_hour)+1;t++){
								//alert(orders[i].order_hours[t].hour)
								business_time_tmp.push(t) 
							}
						}
						
						//alert(business_time_tmp)
						//alert(JSON.stringify(order_hours_tmp))
						for (var k=0;k<16;k++){
								//alert(business_time_tmp.indexOf(k+8))
								if (business_time_tmp.indexOf(k+8) == -1){								
									html.push('<td money=' + orders[i].price[k+8+""] +' time=' + (k*1 +8) + ' place_name=' + orders[i].name.split("号场")[0]  +' place_id=' + orders[i].id + ' status="not-reserveable-web" class="not-reserveable-web"></td>')
								
								}else if (order_hours_tmp.indexOf(k+8) == -1){
									if (orders[i].price[k+8+""]){
										html.push('<td money=' + orders[i].price[k+8+""] +' time=' + (k*1 +8) + ' place_name=' + orders[i].name.split("号场")[0]  +' place_id=' + orders[i].id + ' status="reserveable-web" class="reserveable-web" onclick="reserve(this)"></td>')
									}else{
										html.push('<td money=' + orders[i].price[k+8+""] +' time=' + (k*1 +8) + ' place_name=' + orders[i].name.split("号场")[0]  +' place_id=' + orders[i].id + ' status="not-reserveable-web" class="not-reserveable-web"></td>')
									}
								}else{
									for (var h=0;h<orders[i].order_hours.length;h++){
										if (orders[i].order_hours[h].hour == (k+8)){
											var display = ""
											var content = ""
											if (orders[i].order_hours[h].order_type == 0){
												if (orders[i].order_hours[h].is_payed == true){
													display = "sold-mobile"
												}else{
													display = "notpaid-mobile"
												}
												if (orders[i].order_hours[h].member_card_number){
													content = orders[i].order_hours[h].member_card_number
												}else {
													content = orders[i].order_hours[h].contact
												}
												html.push('<td money=' + orders[i].price[k+8+""] +' num=' + orders[i].order_hours[h].number + ' class=' + display +' time=' + (k*1 +8) +' place_name=' + orders[i].name.split("号场")[0]  +' place_id=' + orders[i].id + '>' + content + '</td>')
											}else if (orders[i].order_hours[h].order_type == 1){
												if (orders[i].order_hours[h].is_payed == true){
													display = "sold-web"
												}else{
													display = "notpaid"
												}
												if (orders[i].order_hours[h].member_card_number || orders[i].order_hours[h].member_card_number!=''){
													content = orders[i].order_hours[h].member_card_number
												}else {
													content = orders[i].order_hours[h].contact
												}
												html.push('<td money=' + orders[i].price[k+8+""] +' num=' + orders[i].order_hours[h].number + ' class=' + display +' time=' + (k*1 +8) +' place_name=' + orders[i].name.split("号场")[0]  +' place_id=' + orders[i].id + '>' + content + '</td>')
											}else if (orders[i].order_hours[h].order_type == 3){
												display = "lock"
												html.push('<td money=' + orders[i].price[k+8+""] +' class=' + display +' place_name=' + orders[i].name.split("号场")[0] +' time=' + (k*1 +8) +' place_id=' + orders[i].id + ' onclick="reserve(this)">' + content + '</td>')
											}
											
											
											
										}
									}
								}
							
							/*if (orders[i].order_hours.indexOf(k+8) == -1){
								html.push('<td number=' +  + 'money=' + orders[i].price.nonmember[k+8+""] +' time=' + (k*1 +8) + ' place_name=' + orders[i].name.split("号场")[0]  +' place_id=' + orders[i].id + ' status="reserveable-web" class="reserveable-web" onclick="reserve(this)"></td>')	
							}else{
								html.push('<td num=' + 1 + ' class="sold-web" place_name=' + orders[i].name.split("号场")[0]  +' place_id=' + orders[i].id + '></td>')
							}*/
						}
						html.push('</tr>')
					}
					$(".reserve-table-web tbody").append(html.join(''))
					$("#loadingCover").hide()
					
	    		}else{
					
					$("#loadingCover").hide()
					$(".qb_quick_tip").css('background','#e96262')
					showBubble("获取信息失败")
				}
    		},error:function (XMLHttpRequest, textStatus, errorThrown)  {	
				$("#loadingCover").hide()
				$(".qb_quick_tip").css('background','#e96262')
				showBubble("获取信息失败")
			}
		})
		var height_tmp = ($(".reserve-table-web tr:not(:first) td:first").height())
		//$(".reserve-table-time-web td:not(:first)").css('height', height_tmp+'px')
	}
	
	function select(obj){
		$(".btn-new-selected").removeClass("btn-new-selected")
		$(obj).addClass('btn-new-selected')
		var chosen_date = $(obj).closest('li').attr('full_date')		
		//alert(chosen_date)
		
		get_reserve_infos()
	}
	
	function reserve(obj){
		$("#chosen_places").html('')
		var current_time = new Date();
			var hour = current_time.getHours()
			var current_month = current_time.getMonth()*1 + 1 + ""
			if (current_month.length == 1){				
				current_month = "0" + current_month
			}
			var current_time_full = current_time.getFullYear() + '-' + current_month + '-'
			if ((current_time.getDate()+"").length == 1){
				current_time_full += '0' + current_time.getDate()
			}else{
				current_time_full += current_time.getDate()
			}
		if ($(obj).is(".reserveable-web")){
			
			//alert(current_time_full)
			//alert($(obj).attr('time'))
			if ( ($(obj).attr('time')*1) <= hour-1 && current_time_full == $(".btn-new-selected").closest("li").attr("full_date")){
					$(".qb_quick_tip").css('background','#e96262')
					showBubble("已超过可预订时间")
			}else if ($(".btn-new-selected").closest("li").attr("order") == "no"){
				$(".qb_quick_tip").css('background','#e96262')
					showBubble("已超过可预订时间")
			}else{
			
				$(obj).removeClass("reserveable-web")	
				$(obj).addClass("chosen")
			}
		}else if ($(obj).is(".chosen")){
			$(obj).removeClass("chosen")	
			$(obj).addClass("reserveable-web")
		}
		if ($(obj).is(".lock")){
			if ( ($(obj).attr('time')*1) <= hour-1 && current_time_full == $(".btn-new-selected").closest("li").attr("full_date")){
					$(".qb_quick_tip").css('background','#e96262')
					showBubble("已超过可操作时间")
			}else if ($(".btn-new-selected").closest("li").attr("order") == "no"){
				$(".qb_quick_tip").css('background','#e96262')
					showBubble("已超过可操作时间")
			}else{
		
				//解锁ajax
				var id = getUrlParam('id')
				if (!id){
					id = 1
				}
				var date = $(".btn-new-selected").closest("li").attr("full_date")
				var places = []
				//$(".reserve-table-web tbody tr").find(".lock").each(function(){
					var place_id = $(obj).attr('place_id')
					var unlock_hours = [$(obj).attr('time')]
					places.push({'id':place_id,'unlock_hours':unlock_hours})	
				//})
				
				$.ajax({
					url:'/stadium/unlock_place/',
					type:'POST',
					dataType:'JSON',
					data:JSON.stringify({'id':id,'date':date, 'places':places}),
					async:false,				
					success:function(result){	
						
						if (result.error == 0){
								$(obj).removeClass("lock")
								$(obj).addClass("reserveable-web")
								//$(".qb_quick_tip").css('background','#44b549')
								//showBubble("解锁成功");
							}else{
								$(".qb_quick_tip").css('background','#e96262')
								showBubble("解锁失败")
							}
							
					},error:function (XMLHttpRequest, textStatus, errorThrown)  {
						$(".qb_quick_tip").css('background','#e96262')
						showBubble("解锁失败")
					}
				})
			}
			
			
		}
		var total_fee = 0
		$(".reserve-table-web tbody tr").find(".chosen").each(function(){
			total_fee = total_fee + ($(this).attr('money')*1)			
		})
		$("#total_fee").html(total_fee)
	}
	
	function show_member_card(type){
		$("#telephone").val('')
		$("#contact").val('')
		$("#member_card_number").val('')
		$("#note").val('')
		if (type == 0){			
			$("#member_card").hide()
		}else{
			$("#member_card").show()
		}
	}
	
	function show_member_card_batch(type){
		$("#telephone").val('')
		$("#contact").val('')
		$("#member_card_number_batch").val('')
		$("#note").val('')
		if (type == 0){			
			$("#member_card_batch").hide()
		}else{
			$("#member_card_batch").show()
		}
	}
	
	function show_weekly_lock(type){
		if (type == 0){			
			$(".weekly_lock").hide()
		}else{
			$(".weekly_lock").show()
		}
	}
	
	function show_weekly_unlock(type){
		if (type == 0){			
			$(".weekly_unlock").hide()
		}else{
			$(".weekly_unlock").show()
		}
	}
	
	function show_weekly_reserve(type){
		if (type == 0){			
			$(".weekly_reserve").hide()
		}else{
			$(".weekly_reserve").show()
		}
	}
	
	function lock(){
		
		if (!$(".reserve-table-web tbody tr").find(".chosen").length > 0){
			$(".qb_quick_tip").css('background','#e96262')
			showBubble("未选择场地")
			return false
		}
		
		
		var id = getUrlParam('id')
		if (!id){
			id = 1
		}
		var date = $(".btn-new-selected").closest("li").attr("full_date")
		var places = []
		$(".reserve-table-web tbody tr").find(".chosen").each(function(){
			var place_id = $(this).attr('place_id')
			var lock_hours = [$(this).attr('time')]
			places.push({'id':place_id,'lock_hours':lock_hours})	
		})
		$.ajax({
			url:'/stadium/lock_place/',
			type:'POST',
			dataType:'JSON',
			data:JSON.stringify({'id':id,'date':date, 'places':places}),
			async:false,
			success:function(result){
				if (result.error == 0){
					$(".chosen").each(function(){
						$(this).removeClass("chosen")
						$(this).addClass("lock")
						var total_fee = 0
						$(".reserve-table-web tbody tr").find(".chosen").each(function(){
							total_fee = total_fee + ($(this).attr('money')*1)			
						})
						$("#total_fee").html(total_fee)
						$("#telephone").val('')
						$("#contact").val('')
						$("#member_card_number").val('')						
					})
					$(".qb_quick_tip").css('background','#44b549')
						showBubble("锁定成功");
				}else{
					$(".qb_quick_tip").css('background','#e96262')
					showBubble("锁定失败")
				}
			},error:function (XMLHttpRequest, textStatus, errorThrown)  {
				$(".qb_quick_tip").css('background','#e96262')
					showBubble("锁定失败")
			}
		})
	}
	
	
	
	function start_reserve(){
		if (!$(".reserve-table-web tbody tr").find(".chosen").length > 0){
			$(".qb_quick_tip").css('background','#e96262')
			showBubble("未选择场地")
			return false
		}
		
		
		var member_card_number = $("#member_card_number").val()
		var contact = $("#contact").val()
		var telephone = $("#telephone").val()
		var note = $("#note").val()
		//var total_fee = $("#total_fee").val()
		var flag = true
		
		if (!contact || contact=='请输入联系人'){
		$("#contact").val('请输入联系人')
		$("#contact").css('color','red')
		flag = false
		}
		if (!telephone || telephone=='请输入手机号码'){
			$("#telephone").val('请输入手机号码')
			$("#telephone").css('color','red')
			flag = false
		}else if (!/^(13[0-9]|14[0-9]|15[0-9]|18[0-9])\d{8}$/i.test(telephone)){
			$("#telephone").val('请输入有效的手机号码')
			$("#telephone").css('color','red')
			flag = false
		}
		
		if ($("#member_card_number").is(':visible')){	
			if (!member_card_number || member_card_number=='请输入会员卡号'){
				$("#member_card_number").val('请输入会员卡号')
				$("#member_card_number").css('color','red')
				flag = false
			}
		}
		
		//if (!total_fee || total_fee == '')
		var id = getUrlParam('id')
		if (!id){
			id = 1
		}
		var type = 1
		if (!$("#member_card_number").is(':visible')){	
			member_card_number = ''
		}
		var date = new Date();
		var num = date.getTime() + MathRand()
		var day = $(".btn-new-selected").closest("li").attr("full_date")
		var terms_of_payment = 1
		var places = []
		$(".reserve-table-web tbody tr").find(".chosen").each(function(){
			var place_id = $(this).attr('place_id')
			var order_hours = [$(this).attr('time')]
			places.push({'id':place_id,'order_hours':order_hours})	
		})
		var money = $("#total_fee").html()
		var data = JSON.stringify({'id':id,'contact':contact,'number':num,'telephone':telephone,'note':note,'member_card_number':member_card_number,'type':type,'day':day,'money':money,'terms_of_payment':terms_of_payment,'places':places})
		//alert(data)
		if (flag){		
			//提交
			$("#loadingCover").show()
			$.ajax({
				url:'/stadium/submit_order/',
				type:'POST',
				dataType:'JSON',
				data:data,
				async:false,
				success:function(result){
					if (result.error == 0){
						//alert(JSON.stringify(result))
						$(".reserve-table-web tbody tr").find(".chosen").each(function(){
							$(this).attr('num',num)
							if (member_card_number || member_card_number!= ''){
								$(this).html(member_card_number)
								
								//设置cookie
								var cookie = contact +";" + telephone + ";" + note
								
								$.cookie(member_card_number, cookie, { path: "/", expires: 7})
								//$(this).attr('num',member_card_number)
							}else{
								$(this).html(contact)
							}
							//$(this).html(member_card_number)
							$(this).removeClass('reserveable-web')
							$(this).removeClass('chosen')
							$(this).addClass('notpaid')							
						})
						$("#loadingCover").hide()
						$(".qb_quick_tip").css('background','#44b549')
							showBubble("预定成功");
						
							
					}else if (result.error == 2){
						$("#loadingCover").hide()
						$(".qb_quick_tip").css('background','#e96262')
						showBubble("该场地已经被预定了，请刷新页面后重试")
					}else{
						$("#loadingCover").hide()
						$(".qb_quick_tip").css('background','#e96262')
						showBubble("预定失败")
					}					
										
				},error:function (XMLHttpRequest, textStatus, errorThrown)  {
					$("#loadingCover").hide()
					$(".qb_quick_tip").css('background','#e96262')
					showBubble("预定失败")
				}
			})
		}
		
	}
	
	function confirm_pay(obj,type){
	//alert()
	var num = $(obj).closest('table').find('.number').html()
	var money = $(obj).closest('table').find('.money').html()
		if (type == 0){//确认支付
			$.ajax({
				url:'/stadium/pay_order/',
				type:'POST',
				dataType:'JSON',
				data:JSON.stringify({"number":num,"money":money}),
				async:false,
				success:function(result){
					//alert(result.error)
					if (result.error == 0){
						$(obj).closest('tr').hide()
						$(obj).closest('table').find('.is_payed').html('已付款')
						$(".reserve-table-web tbody tr").find(".notpaid").each(function(){
							if ($(this).attr('num') == num){								
									$(this).removeClass('notpaid')
									$(this).addClass('sold-web')
							}
						})
						$(".reserve-table-web tbody tr").find(".notpaid-mobile").each(function(){
							if ($(this).attr('num') == num){
								$(this).removeClass('notpaid-mobile')
								$(this).addClass('sold-mobile')		
							}
						})
						$(".qb_quick_tip").css('background','#44b549')
						showBubble("确认支付成功");
					}else{
						$(".qb_quick_tip").css('background','#e96262')
						showBubble("确认支付失败")
					}
				},error:function (XMLHttpRequest, textStatus, errorThrown)  {
					$(".qb_quick_tip").css('background','#e96262')
					showBubble("确认支付失败")
				}
			})
		}else{
			if(confirm("确定取消该订单？"))
			 {
				$.ajax({
					url:'/order/cancel/',
					type:'POST',
					dataType:'json',
					data:JSON.stringify({'number':num}),
					async:false,
					success:function(result){		
						//alert(result.error)        	
						if (result.error == 0){
							$("#" + num).hide()
							$(".reserve-table-web tbody tr").find(".notpaid").each(function(){
								if ($(this).attr('num') == num){
									$(this).removeClass('notpaid')								
									$(this).html('')
									$(this).addClass('reserveable-web')
									$(this).attr('onclick','reserve(this)')
								}
							})
							$(".reserve-table-web tbody tr").find(".notpaid-mobile").each(function(){
								if ($(this).attr('num') == num){
									$(this).removeClass('notpaid-mobile')						
									$(this).html('')
									$(this).addClass('reserveable-web')
									$(this).attr('onclick','reserve(this)')
								}
							})
						
						
						$(".qb_quick_tip").css('background','#44b549')
						showBubble("取消成功");
						}else{
							$(".qb_quick_tip").css('background','#e96262')
							showBubble("取消失败")
						}
					},
					error: function (XMLHttpRequest, textStatus, errorThrown)  {
						$(".qb_quick_tip").css('background','#e96262')
							showBubble("取消失败")
					}
				})
				
			 }
		}		
	}
	
	function MathRand() 
	{ 
		var Num=""; 
		for(var i=0;i<6;i++) 
		{ 
			Num+=Math.floor(Math.random()*10); 
		} 
		return Num
	} 
	
	function get_left_date(){
		click--
		if (click >0){
			$(".breadcrumb").scrollLeft($('.breadcrumb').scrollLeft() - 85) 
			return false
		}
		if (click <=0 && Math.abs(click) <= leftcount){
			$(".breadcrumb").scrollLeft($('.breadcrumb').scrollLeft() - 85) 
			return false
		}
		var first_li = $(".breadcrumb li:first")
		var left_date = $(first_li).attr("full_date")
		var left_day = $(first_li).attr("day")
		var year =  left_date.split("-")[0]
		var month =  left_date.split("-")[1]
		var day = left_date.split("-")[2]
		var left_date_tmp = new Date(left_date.replace(/-/,"/")) 
		var new_date_tmp = left_date_tmp.getTime()-1000*60*60*24;
		//var d=new Date();
		//alert(d)
		
		var date = new Date(new_date_tmp)
		var year = date.getFullYear() 
		var month = date.getMonth() + 1;
		
		if (month.length == 1){
			month = '0' + month
		}
		var day = date.getDate();
		var day_day = date.getDay()
		var weekday = ""
		switch(day_day){
				case 0:
					weekday = '周日';
					break;
				case 1:
					weekday = '周一';
					break;
				case 2:
					weekday = '周二';
					break;
				case 3:
					weekday = '周三';
					break;
				case 4:
					weekday = '周四';
					break;
				case 5:
					weekday = '周五';
					break;
				case 6:
					weekday = '周六';
					break;
			}
		
		var display_day = '' + day
			if (display_day.length == 1){
				display_day = '0' + day
			}	
		var canorder = ""
		var date_now = new Date()
		var date_new = new Date(year + '-' + month + '-' + display_day)
		if (date_new < date_now){
			canorder = "no"
		}else{
			canorder = "yes"
		}
		var html = '<li order=' + canorder + ' day=' + day_day + ' full_date=' + year + '-' + month + '-' + display_day + ' style="display:inline-block;padding-right:5px;"><a href="javascript:void(0)"><button onclick="select(this)" class="btn-new" type="button" style="text-shadow:none;background-color:#fff;color:#bdbdbd;border-color:#bdbdbd;width:80px;height:32px;font-size:12px">' + month + '-' + display_day + ' ' + weekday + '</button></a></li>'
		$("#date_selecter").prepend(html)		
		$(".breadcrumb").scrollLeft($('.breadcrumb').scrollLeft()) 
		leftcount ++ 
	}
	
	function get_right_date(){
		click++
		if (click <0){
			$(".breadcrumb").scrollLeft($('.breadcrumb').scrollLeft() + 85) 
			return false
		}
		if (click >=0 && click <= rightcount){
			$(".breadcrumb").scrollLeft($('.breadcrumb').scrollLeft() + 85) 
			return false
		}
		var last_li = $(".breadcrumb li:last")
		
		var right_date = $(last_li).attr("full_date")
		var right_day = $(last_li).attr("day")
		var year =  right_date.split("-")[0]
		var month =  right_date.split("-")[1]
		var day = right_date.split("-")[2]
		var right_date_tmp = new Date(right_date.replace(/-/,"/")) 
		var new_date_tmp = right_date_tmp.getTime()+1000*60*60*24;
		//var d=new Date();
		//alert(d)
		
		var date = new Date(new_date_tmp)
		var year = date.getFullYear() 
		var month = date.getMonth() + 1;
		
		if (month.length == 1){
			month = '0' + month
		}
		var day = date.getDate();
		var day_day = date.getDay()
		var weekday = ""
		switch(day_day){
				case 0:
					weekday = '周日';
					break;
				case 1:
					weekday = '周一';
					break;
				case 2:
					weekday = '周二';
					break;
				case 3:
					weekday = '周三';
					break;
				case 4:
					weekday = '周四';
					break;
				case 5:
					weekday = '周五';
					break;
				case 6:
					weekday = '周六';
					break;
			}
		
		var display_day = '' + day
			if (display_day.length == 1){
				display_day = '0' + day
			}
		var canorder = ""
		var date_now = new Date()
		var date_new = new Date(year + '-' + month + '-' + display_day)
		if (date_new < date_now){
			canorder = "no"
		}else{
			canorder = "yes"
		}
		var html = '<li order=' + canorder + ' day=' + day_day + ' full_date=' + year + '-' + month + '-' + display_day + ' style="display:inline-block;padding-right:5px;"><a href="javascript:void(0)"><button onclick="select(this)" class="btn-new" type="button" style="text-shadow:none;background-color:#fff;color:#bdbdbd;border-color:#bdbdbd;width:80px;height:32px;font-size:12px;">' + month + '-' + display_day + ' ' + weekday + '</button></a></li>'
		$("#date_selecter").append(html)
		$(".breadcrumb").scrollLeft($('.breadcrumb').scrollLeft() + 85) 
		rightcount++
		//$(".breadcrumb").animate({scrollLeft:105},1000)
		//$("#date_selecter li:last").remove()
	}
	
	function start_batch_lock(){
		$("#loadingCover").show()
		var id = getUrlParam('id')
		if (!id){
			id = 1
		}
		var circle = $("input[name='batch_circle_lock']:checked").val()
		var weekday = ""
		if (circle == "1"){
			weekday = $("#batch_lock_weekly").val()
		}
		var place = $("#batch_lock_places").val()
		var startdate = $("#batch_lock_startdate").val()
		var enddate = $("#batch_lock_enddate").val()
		var startdate_tmp = new Date(startdate)
		var enddate_tmp = new Date(enddate)
		var starttime = parseInt($("#batch_lock_starttime").val())
		var endtime =parseInt($("#batch_lock_endtime").val())		

		if (startdate == ""){
			//$("#loadingCover").hide()
			$(".qb_quick_tip").css('background','#e96262')
			showBubble("请选择开始日期")
		}else if (enddate == ""){
			$(".qb_quick_tip").css('background','#e96262')
			showBubble("请选择结束日期")
		}else if (startdate_tmp > enddate_tmp){
			$(".qb_quick_tip").css('background','#e96262')
			showBubble("开始日期大于结束日期，请重新选择")
		}else if (parseInt(starttime) > parseInt(endtime)){
			$(".qb_quick_tip").css('background','#e96262')
			showBubble("开始时间大于结束时间，请重新选择")
		}else{
			var lock_hours = []
			for (starttime;starttime<=endtime;starttime++){			
				lock_hours.push(starttime)
			}
			if (circle == "0"){
				var data = {'id':id,'period':parseInt(circle),'place_id':parseInt(place),'start_day':startdate,'end_day':enddate,'lock_hours':lock_hours}
			}else{
				var data = {'id':id,'period':parseInt(circle),'weekday':weekday,'place_id':parseInt(place),'start_day':startdate,'end_day':enddate,'lock_hours':lock_hours}
			}
			
			$.ajax({
				url:'/stadium/batch_lock_place/',
				type:'POST',
				data:JSON.stringify(data),
				dataType:'JSON',
				success:function(result){
					if (result.error == 0){
						$("#loadingCover").hide()
						$(".qb_quick_tip").css('background','#44b549')
						showBubble("批量锁定成功")
						get_reserve_infos()
					}else{
						$("#loadingCover").hide()
						$(".qb_quick_tip").css('background','#e96262')
						showBubble("批量锁定失败")
					}			
				},error:function (XMLHttpRequest, textStatus, errorThrown)  {
					$("#loadingCover").hide()
					$(".qb_quick_tip").css('background','#e96262')
					showBubble("批量锁定失败")
				}
			})
		}
		$("#loadingCover").hide()
	}
	
	function start_batch_unlock(){
		$("#loadingCover").show()
		var id = getUrlParam('id')
		if (!id){
			id = 1
		}
		var circle = $("input[name='batch_circle_unlock']:checked").val()
		var weekday = ""
		if (circle == "1"){
			weekday = $("#batch_unlock_weekly").val()
		}
		var place = $("#batch_unlock_places").val()
		var startdate = $("#batch_unlock_startdate").val()
		var enddate = $("#batch_unlock_enddate").val()
		var startdate_tmp = new Date(startdate)
		var enddate_tmp = new Date(enddate)
		var starttime = parseInt($("#batch_unlock_starttime").val())
		var endtime = parseInt($("#batch_unlock_endtime").val())
		
		var data = {}
		if (startdate == ""){
			//$("#loadingCover").hide()
			$(".qb_quick_tip").css('background','#e96262')
			showBubble("请选择开始日期")
		}else if (enddate == ""){
			$(".qb_quick_tip").css('background','#e96262')
			showBubble("请选择结束日期")
		}else if (startdate_tmp > enddate_tmp){
			$(".qb_quick_tip").css('background','#e96262')
			showBubble("开始日期大于结束日期，请重新选择")
		}else if (parseInt(starttime) > parseInt(endtime)){
			$(".qb_quick_tip").css('background','#e96262')
			showBubble("开始时间大于结束时间，请重新选择")
		}else{
			var unlock_hours = []
			for (starttime;starttime<=endtime;starttime++){			
				unlock_hours.push(starttime)
			}
			if (circle == "0"){
				var data = {'id':id,'period':parseInt(circle),'place_id':parseInt(place),'start_day':startdate,'end_day':enddate,'unlock_hours':unlock_hours}
			}else{
				var data = {'id':id,'period':parseInt(circle),'weekday':weekday,'place_id':parseInt(place),'start_day':startdate,'end_day':enddate,'unlock_hours':unlock_hours}
			}
			$.ajax({
				url:'/stadium/batch_unlock_place/',
				type:'POST',
				data:JSON.stringify(data),
				dataType:'JSON',
				success:function(result){
					if (result.error == 0){
						$("#loadingCover").hide()
						$(".qb_quick_tip").css('background','#44b549')
						showBubble("批量解锁成功")
						get_reserve_infos()
					}else{						
						$("#loadingCover").hide()
						$(".qb_quick_tip").css('background','#e96262')
						showBubble("批量解锁失败")
					}			
				},error:function (XMLHttpRequest, textStatus, errorThrown)  {
					$("#loadingCover").hide()
					$(".qb_quick_tip").css('background','#e96262')
					showBubble("批量解锁失败")
				}
			})
		}
		$("#loadingCover").hide()
	}
	
	function start_batch_reserve(){
		//var type = $("input[name='member_ship_batch']:checked").val()
		$("#loadingCover").show()
		var id = getUrlParam('id')
		if (!id){
			id = 1
		}
		var circle = $("input[name='batch_circle_reserve']:checked").val()
		var weekday = ""
		if (circle == "1"){
			weekday = $("#batch_reserve_weekly").val()
		}
		var place = $("#batch_reserve_places").val()
		var member_card_number = $("#member_card_number_batch").val()
		var contact = $("#contact_batch").val()
		var telephone = $("#telephone_batch").val()
		var note = $("#note_batch").val()
		var startdate = $("#batch_reserve_startdate").val()
		var enddate = $("#batch_reserve_enddate").val()
		var startdate_tmp = new Date(startdate)
		var enddate_tmp = new Date(enddate)
		var starttime = parseInt($("#batch_reserve_starttime").val())
		var endtime = parseInt($("#batch_reserve_endtime").val())
		var total_fee = $("#total_fee_batch").val()
		var flag = true
		
		var data = {}
		if (!contact || contact=='请输入联系人'){
			$("#contact_batch").val('请输入联系人')
			$("#contact_batch").css('color','red')
			flag = false
		}
		if (!telephone || telephone=='请输入手机号码'){
			$("#telephone_batch").val('请输入手机号码')
			$("#telephone_batch").css('color','red')
			flag = false
		}else if (!/^(13[0-9]|14[0-9]|15[0-9]|18[0-9])\d{8}$/i.test(telephone)){
			$("#telephone_batch").val('请输入有效的手机号码')
			$("#telephone_batch").css('color','red')
			flag = false
		}
		
		if ($("#member_card_number_batch").is(':visible')){	
			if (!member_card_number || member_card_number=='请输入会员卡号'){
				$("#member_card_number_batch").val('请输入会员卡号')
				$("#member_card_number_batch").css('color','red')
				flag = false
			}
		}
		if (flag){
			if (startdate == ""){
				//$("#loadingCover").hide()
				$(".qb_quick_tip").css('background','#e96262')
				showBubble("请选择开始日期")
			}else if (enddate == ""){
				$(".qb_quick_tip").css('background','#e96262')
				showBubble("请选择结束日期")
			}else if (startdate_tmp > enddate_tmp){
				$(".qb_quick_tip").css('background','#e96262')
				showBubble("开始日期大于结束日期，请重新选择")
			}else if (parseInt(starttime) > parseInt(endtime)){
				$(".qb_quick_tip").css('background','#e96262')
				showBubble("开始时间大于结束时间，请重新选择")
			}else if ($.trim(total_fee) == ""){
				$(".qb_quick_tip").css('background','#e96262')
				showBubble("请输入总金额")
			}else{				
				var date = new Date();
				var number = date.getTime() + MathRand()
				var order_hours = []
				for (starttime;starttime<=endtime;starttime++){			
					order_hours.push(starttime)
				}
				if (circle == "0"){
					var data = {'id':id,'number':number,'contact':contact,'member_card_number':member_card_number,'telephone':telephone,'note':note,'type':0,'money':total_fee,'terms_of_payment':1,'period':parseInt(circle),'place_id':parseInt(place),'start_day':startdate,'end_day':enddate,'order_hours':order_hours}
				}else{
					var data = {'id':id,'number':number,'contact':contact,'member_card_number':member_card_number,'telephone':telephone,'note':note,'type':0,'money':total_fee,'terms_of_payment':1,'period':parseInt(circle),'weekday':weekday,'place_id':parseInt(place),'start_day':startdate,'end_day':enddate,'order_hours':order_hours}
				}
				
				//alert(JSON.stringify(data))
				$.ajax({
					url:'/stadium/batch_submit_order/',
					type:'POST',
					data:JSON.stringify(data),
					dataType:'JSON',
					success:function(result){
						if (result.error == 0){
							if (member_card_number || member_card_number!= ''){
								$(this).html(member_card_number)
								var cookie = contact +";" + telephone + ";" + note
								$.cookie(member_card_number, cookie, { path: "/", expires: 7})
							}
							$("#loadingCover").hide()
							$(".qb_quick_tip").css('background','#44b549')
							showBubble("批量预定成功")
							get_reserve_infos()							
						}else{							
							$("#loadingCover").hide()
							$(".qb_quick_tip").css('background','#e96262')
							showBubble("批量预定失败")
						}			
					},error:function (XMLHttpRequest, textStatus, errorThrown)  {
						$("#loadingCover").hide()
						$(".qb_quick_tip").css('background','#e96262')
						showBubble("批量预定失败")
					}
				})
			}
		}
		$("#loadingCover").hide()
	}
	
	function start_batch_unreserve(){
		$("#loadingCover").show()
		var id = getUrlParam('id')
		if (!id){
			id = 1
		}
		var circle = $("input[name='batch_circle_reserve']:checked").val()
		var weekday = ""
		if (circle == "1"){
			weekday = $("#batch_reserve_weekly").val()
		}
		var place = $("#batch_reserve_places").val()
		var startdate = $("#batch_reserve_startdate").val()
		var enddate = $("#batch_reserve_enddate").val()
		var startdate_tmp = new Date(startdate)
		var enddate_tmp = new Date(enddate)
		var starttime = parseInt($("#batch_reserve_starttime").val())
		var endtime = parseInt($("#batch_reserve_endtime").val())
		
		var data = {}
		if (startdate == ""){
				//$("#loadingCover").hide()
				$(".qb_quick_tip").css('background','#e96262')
				showBubble("请选择开始日期")
			}else if (enddate == ""){
				$(".qb_quick_tip").css('background','#e96262')
				showBubble("请选择结束日期")
			}else if (startdate_tmp > enddate_tmp){
				$(".qb_quick_tip").css('background','#e96262')
				showBubble("开始日期大于结束日期，请重新选择")
			}else if (parseInt(starttime) > parseInt(endtime)){
				$(".qb_quick_tip").css('background','#e96262')
				showBubble("开始时间大于结束时间，请重新选择")
			}else{
				var unlock_hours = []
				for (starttime;starttime<=endtime;starttime++){			
					unlock_hours.push(starttime)
				}
				if (circle == "0"){
					var data = {'id':id,'period':parseInt(circle),'place_id':parseInt(place),'start_day':startdate,'end_day':enddate,'unlock_hours':unlock_hours}
				}else{
					var data = {'id':id,'period':parseInt(circle),'weekday':weekday,'place_id':parseInt(place),'start_day':startdate,'end_day':enddate,'unlock_hours':unlock_hours}
				}
				alert(JSON.stringify(data))
				$.ajax({
					url:'/stadium/batch_unlock_place/',
					type:'POST',
					data:JSON.stringify(data),
					dataType:'JSON',
					success:function(result){
						if (result.error == 0){
							$("#loadingCover").hide()
							$(".qb_quick_tip").css('background','#44b549')
							showBubble("批量取消预定成功")
						}			
					},error:function (XMLHttpRequest, textStatus, errorThrown)  {
						$("#loadingCover").hide()
						$(".qb_quick_tip").css('background','#e96262')
						showBubble("批量取消预定失败")
					}
				})
			}
		$("#loadingCover").hide()
	}
	
	var timeout
	function showBubble(a) {
		var c = $("#bubble");
			c.css("opacity", 1), c.hasClass("qb_none") || c.html(a), c.html(a).removeClass("qb_none")
			timeout = 	setTimeout("disapper()", 1300 )
	}

	function disapper(){
		$("#bubble").addClass("qb_none").removeAttr("style")
		clearTimeout(timeout)
	}	
	
	 