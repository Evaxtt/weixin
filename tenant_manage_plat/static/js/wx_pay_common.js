function start_pay(flag){	
	
	var applicant = $("#applicant").val()
	var telephone = $("#telephone").val()
	var member_card_number = $("#member_card_number").val()
	var memo = $("#memo").val()
	//var flag = validate()
	
	
	
	
	if (flag){
		var pay_method = $("input[type='radio']:checked").val();
		//订单号
		var date = new Date();
		var num = date.getTime() + MathRand()
		var money = getUrlParam('total_fee') 
		if (pay_method == "offline"){
			if (submit_pay('',1, num) == true){
				//if (change_pay_status(num,getUrlParam('total_fee')) == true){
					window.location.href = "/stadium/reserve_result_wx.html"
				//}
			}else{
				//alert('预定失败')
			}
		}else{
			var flag_wx = true
			var prepay_id = ''
			var openid = getUrlParam('openid')
			url = "/wx/get_prepay_id?openid=" + openid + '&num=' + num + '&total_fee=' + (money *100)
			//(money *100)
			//alert(url)
			$.ajax({
				url:url,
				dataType:'JSON',
				data:{},
				async:false,
				success:function(result){
		        	if (result.result == 'OK'){
		        		prepay_id = result.prepay_id
		        	}        		         
		        },
				error: function (XMLHttpRequest, textStatus, errorThrown)  {
					alert('error')
					flag_wx = false
				}
			})
			//alert(prepay_id)
			
			var appid = ''
			var timeStamp = ''
			var nonceStr = ''
			var paySign = ''
			$.ajax({
				url:"/wx/start_pay?prepay_id=" + prepay_id,
				dataType:'JSON',
				data:{},
				async:false,
				success:function(result){
		        	
		        		appid = result.appId
		        		timeStamp = result.timeStamp
		        		nonceStr = result.nonceStr
		        		package = "prepay_id=" + prepay_id
		        		paySign = result.paySign
		        	       		         
		        },
				error: function (XMLHttpRequest, textStatus, errorThrown)  {
					alert('error')
					flag_wx = false
				}
			})
			
			if (flag_wx){
				if (submit_pay(prepay_id, 0, num) == true){
					
					//获取到prepayid 开始调用支付
					WeixinJSBridge.invoke('getBrandWCPayRequest',{
						"appId":appid,
						"timeStamp":timeStamp + '',
						"nonceStr":nonceStr,
						"package":package,
						"signType":"MD5",
						"paySign":paySign		
					},function(res){
						if (res.err_msg == "get_brand_wcpay_request:ok"){
							if (change_pay_status(num,money)==true){
								window.location.href = "/stadium/reserve_result_wx.html"
							}
						}else{
							$.ajax({
						 		url:'/order/cancel/',
						 		type:'POST',
						 		dataType:'json',
						 		data:JSON.stringify({'number':num}),
						 		async:false,
						 		success:function(result){		        	
								    if (result.error == 0){
								    	
								    }
								},
								error: function (XMLHttpRequest, textStatus, errorThrown)  {
									alert('cancelerror')
								}
						 	})
						}
					})
				}else{
					//alert('预定失败1')
				}
			}
		}
	}
	
	
}

function submit_pay(prepay_id, terms_of_payment, num){	
	

	var id = getUrlParam('id')
	var contact = $("#applicant").val()
	var openid = getUrlParam('openid')
	
	
	
	
	var telephone = $("#telephone").val()
	var member_card_number = $("#member_card_number").val()
	var note = $("#memo").val()
	var type = 0
	var day = getUrlParam('day')
	var money = getUrlParam('total_fee')
	var order_detail = getUrlParam('order_detail')
	var places = JSON.parse(order_detail)
	
	if (!$("#member_card_number_div").is(':visible')){	
		member_card_number = ''
	}
	
	var data = JSON.stringify({'id':id,'contact':contact,'openid':openid,'number':num,'telephone':telephone,'note':note,'member_card_number':member_card_number,'type':type,'day':day,'money':money,'terms_of_payment':terms_of_payment,'places':places, 'prepay_id':prepay_id})
	//alert(data)
	
	var flag = true
	
	//alert(JSON.stringify(places))
	$.ajax({
		url:'/stadium_info/submit_order/',
		type:'POST',
		dataType:'JSON',
		data:data,
		async:false,
		success:function(result){
    		if (result.error == 0){
    			flag = true
			}else{
				flag  = false
				if (result.error == 2){
					window.location.href = '/stadium/reserve_errorinfo_wx.html?errcode=duplicate'
				}
				if (result.error == 3){
					window.location.href = '/stadium/reserve_errorinfo_wx.html?errcode=notpaid'
				}
			}	
								
								
    	},error:function (XMLHttpRequest, textStatus, errorThrown)  {
			alert('error')
			flag = false
		}
	})
	$("#start_pay").html("提交")
	$("#start_pay").css("background-color","#ff9933")
	$("#start_pay").attr("onclick","validate()")
	return flag
}

function change_pay_status(num,money){
	//alert()
	var flag = true
	$.ajax({
		url:'/stadium_info/pay_order/',
		type:'POST',
		dataType:'JSON',
		data:JSON.stringify({"number":num,"money":money}),
		async:false,
		success:function(result){
			//alert(result.error)
			if (result.error == 0){
				flag = true
			}else{
				window.location.href = '/stadium/reserve_errorinfo_wx.html?errcode=paymenterror'
				flag = false
			}
    	},error:function (XMLHttpRequest, textStatus, errorThrown)  {
			flag = false
		}
	})
	return flag
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