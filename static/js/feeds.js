
function postToFeed(link, place, _id, from, to) {
  var obj = {
    method: 'feed',
    link: link,
    picture: 'https://willbeout.herokuapp.com/static/img/og.png',
    name: place,
    caption: 'Join me for Drinks/Food?',
    description: fDate(from) + " to " + fDate(to) + "."
  };

  function callback(response) {
    document.getElementById('msg').innerHTML = "Post ID: " + response['post_id'];
  }
  FB.ui(obj, callback);
}

$(function() {
  $('.share-event').click(function(event) {
    event.preventDefault();
    var share = $(this);
    postToFeed(
      share.attr('data-link'),
      share.attr('data-place'),
      share.attr('data-id'),
      share.attr('data-from'),
      share.attr('data-to')
    );
  });
});

function fDate(date){
	a = new Date(date);
	days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
	months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
	dates = ['1st', 
			 '2nd', 
			 '3rd', 
			 '4th',
			 '5th',
			 '6th',
			 '7th',
			 '8th',
			 '9th',
			 '10th',
			 '11th',
			 '12th',
			 '13th',
			 '14th',
			 '15th',
			 '16th',
			 '17th',
			 '18th',
			 '19th',
			 '20th',
			 '21st',
			 '22nd',
			 '23rd',
			 '24th',
			 '25th',
			 '26th',
			 '27th',
			 '28th',
			 '29th',
			 '30th',
			 '31st'];
	day = days[a.getDay()];
	c = dates[a.getDate()-1];
	month = months[a.getMonth()+1];
	return day + ' ' + month + ' ' + c + ' ' + a.getFullYear();
}

$('.popover-bottom').popover(placement='bottom')
