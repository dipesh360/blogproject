// ajax for sending OTP

function ReSendOTP(username, mess_id) {
	
	mess = document.getElementById(mess_id);
	mess.innerText = "Sending...";
	$.ajax({
		type: 'GET',
		url: '/resendOTP',
		data: {usr:username},
		success: function(data){
			mess.innerText = data;

		}
	})
}
