$(document).ready(function(){

	$('.collection').click(function(){
		$(this).children().css('color', 'red');
		var news = $(this).parent().parent().attr('data-id');
		var user = $(this).parent().parent().attr('data-user');

		$.ajax(
		{
			type: "GET",
			url: "/collections",

			data:{
				news: news,
				user: user,
			},

		})

	});


	$('.history').click(function(){
		var news = $(this).parent().attr('data-id');
		var user = $(this).parent().attr('data-user');
		console.log(news);
		console.log(user);
		$.ajax(
		{
			type: 'GET',
			url: '/historys',
			data:{
				news: news,
				user: user,
			}
		})
	});
	

});